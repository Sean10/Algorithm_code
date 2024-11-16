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
        done = False
        while not done:
            done = True
            self.nodes.sort(key=lambda x: x.scatter_width)
            
            for node in self.nodes:
                if node.scatter_width >= self.virtual_nodes:
                    continue
                
                copyset = Copyset()
                copyset.add_node(node)
                
                candidates = sorted(self.nodes, key=lambda x: x.scatter_width)
                for candidate in candidates:
                    if candidate.id == node.id:
                        continue
                    
                    copyset.add_node(candidate)
                    if copyset.size() == self.replicas:
                        if self.check_tier(copyset) and self.did_not_appear(copyset):
                            self.copysets.append(copyset)
                            self._update_scatter_width(copyset)
                            done = False
                            break
                        copyset.remove_node(candidate)

    def _update_scatter_width(self, copyset):
        """更新节点的scatter width"""
        for node in copyset.nodes:
            self.node_to_copysets[node.id].append(copyset)
            node.scatter_width = len(set(
                other_node.id 
                for cs in self.node_to_copysets[node.id]
                for other_node in cs.nodes 
                if other_node.id != node.id
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