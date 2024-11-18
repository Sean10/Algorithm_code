import numpy as np
import multiprocessing as mp
from functools import partial
from .base import BaseSimulator
from ..models.node import Node
from ..models.copyset import Copyset
from ..utils.hash_utils import get_hash

class TieredCopysetSimulator(BaseSimulator):
    def __init__(self, num_objects, num_nodes, replicas=3, num_processes=None, virtual_nodes=1000):
        super().__init__(num_objects, num_nodes, num_processes)
        self.replicas = replicas
        self.virtual_nodes = virtual_nodes
        self.nodes = []
        self.copysets = []
        self.node_to_copysets = {}
        self._initialize_nodes()

    def _initialize_nodes(self):
        """初始化节点，将节点分为主层和备份层"""
        primary_count = int(self.num_nodes * 0.7)  # 70%作为主层节点
        for i in range(self.num_nodes):
            tier = "primary" if i < primary_count else "backup"
            node = Node(i, tier)
            self.nodes.append(node)
            self.node_to_copysets[node.id] = []

    def check_tier(self, copyset):
        """检查copyset是否满足层级要求"""
        backup_count = sum(1 for node in copyset.nodes if node.tier == "backup")
        return backup_count == 1

    def did_not_appear(self, copyset):
        """检查copyset是否已经存在"""
        return not any(copyset.is_same(existing) for existing in self.copysets)

    def build_copysets(self):
        """构建满足要求的copysets"""
        # 预处理：将节点分组，提高查找效率
        primary_nodes = [n for n in self.nodes if n.tier == "primary"]
        backup_nodes = [n for n in self.nodes if n.tier == "backup"]
        
        if not primary_nodes or not backup_nodes:
            raise RuntimeError("无法创建copyset：需要同时具有主节点和备份节点")
        
        target_copysets = min(self.virtual_nodes, len(primary_nodes) * 3)
        attempts = 0
        max_attempts = self.num_nodes * 5  # 减少最大尝试次数以提高性能
        
        while len(self.copysets) < target_copysets and attempts < max_attempts:
            attempts += 1
            
            # 选择scatter width最小的主节点作为起始点
            available_primary = [n for n in primary_nodes if n.scatter_width < self.virtual_nodes]
            if not available_primary:
                break
                
            start_node = min(available_primary, key=lambda x: x.scatter_width)
            copyset = Copyset()
            copyset.add_node(start_node)
            
            # 快速选择剩余的主节点
            remaining_primary = [n for n in primary_nodes 
                               if n.id != start_node.id and 
                               n.scatter_width < self.virtual_nodes]
            
            # 选择scatter width最小的主节点
            needed_primary = self.replicas - 2  # 减去起始节点和一个备份节点
            if remaining_primary and needed_primary > 0:
                selected = sorted(remaining_primary, key=lambda x: x.scatter_width)[:needed_primary]
                for node in selected:
                    copyset.add_node(node)
            
            # 选择scatter width最小的备份节点
            available_backup = [n for n in backup_nodes if n.scatter_width < self.virtual_nodes]
            if available_backup:
                backup_node = min(available_backup, key=lambda x: x.scatter_width)
                copyset.add_node(backup_node)
            
            # 验证并添加copyset
            if (copyset.size() == self.replicas and 
                self.check_tier(copyset) and 
                self.did_not_appear(copyset)):
                self.copysets.append(copyset)
                self._update_scatter_width(copyset)
        
        # 如果没有创建足够的copysets，使用简化的备用策略
        if len(self.copysets) < self.virtual_nodes // 2:
            self._create_simple_copysets(primary_nodes, backup_nodes)

    def _create_simple_copysets(self, primary_nodes, backup_nodes):
        """创建简单的copyset作为备用方案"""
        target = self.virtual_nodes - len(self.copysets)
        attempts = 0
        max_attempts = target * 2
        
        while len(self.copysets) < self.virtual_nodes and attempts < max_attempts:
            attempts += 1
            copyset = Copyset()
            
            # 随机选择主节点，但优先选择scatter width较小的
            primary_candidates = sorted(primary_nodes, key=lambda x: x.scatter_width)
            selected_primary = primary_candidates[:self.replicas-1]
            
            if len(selected_primary) < self.replicas-1:
                continue
                
            for node in selected_primary:
                copyset.add_node(node)
            
            # 随机选择一个备份节点
            backup_candidates = sorted(backup_nodes, key=lambda x: x.scatter_width)
            if not backup_candidates:
                continue
                
            copyset.add_node(backup_candidates[0])
            
            if self.did_not_appear(copyset):
                self.copysets.append(copyset)
                self._update_scatter_width(copyset)

    def _update_scatter_width(self, copyset):
        """优化的scatter width更新方法"""
        # 使用集合操作提高性能
        node_ids = {n.id for n in copyset.nodes}
        for node in copyset.nodes:
            self.node_to_copysets[node.id].append(copyset)
            # 只更新新添加的连接
            other_nodes = node_ids - {node.id}
            node.scatter_width = len(set(
                n_id for cs in self.node_to_copysets[node.id]
                for n in cs.nodes
                if (n_id := n.id) != node.id
            ))

    def _parallel_tiered_mapping(self, chunk, copysets):
        """并行处理tiered copyset映射"""
        results = []
        for obj in chunk:
            obj_hash = get_hash(obj)
            copyset_index = obj_hash % len(copysets)
            copyset = copysets[copyset_index]
            primary_nodes = [n for n in copyset.nodes if n.tier == "primary"]
            node = primary_nodes[obj_hash % len(primary_nodes)]
            results.append(node.id)
        return np.array(results)

    def tiered_mapping(self, objects):
        """使用多进程进行tiered copyset映射"""
        self.build_copysets()
        if not self.copysets:
            raise RuntimeError("No valid copysets could be built")
            
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_tiered_mapping, copysets=self.copysets)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def simulate(self, distribution_type):
        objects = self.generate_distribution(distribution_type)
        tiered_results = self.tiered_mapping(objects)
        return objects, tiered_results 