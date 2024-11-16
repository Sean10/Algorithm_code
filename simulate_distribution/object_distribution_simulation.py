import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, zipf
import hashlib
import os
import multiprocessing as mp
from functools import partial

class Node:
    def __init__(self, node_id, tier="primary"):
        self.id = node_id
        self.tier = tier
        self.scatter_width = 0  # 记录与多少其他节点形成了copyset

class Copyset:
    def __init__(self):
        self.nodes = []
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def remove_node(self, node):
        self.nodes = [n for n in self.nodes if n.id != node.id]
    
    def size(self):
        return len(self.nodes)
    
    def is_same(self, other_copyset):
        self_ids = set(node.id for node in self.nodes)
        other_ids = set(node.id for node in other_copyset.nodes)
        return self_ids == other_ids

class ObjectDistributionSimulator:
    def __init__(self, num_objects, num_nodes, num_processes=None):
        self.num_objects = num_objects
        self.num_nodes = num_nodes
        self.virtual_nodes = 1000
        self.Q = 3  # Dynamo's Q value
        self.num_processes = num_processes or mp.cpu_count()

    def _parallel_hash(self, chunk, num_nodes):
        hash_func = np.vectorize(lambda x: hash(x) % num_nodes)
        return hash_func(chunk)

    def _parallel_dht(self, chunk, ring):
        keys = np.array([self.get_hash(obj) for obj in chunk])
        indices = np.searchsorted(ring[:, 0], keys, side='right') % len(ring)
        return ring[indices, 1]

    def _parallel_dynamo(self, chunk, virtual_nodes):
        results = []
        for obj in chunk:
            obj_hash = self.get_hash(obj)
            for token, node in virtual_nodes:
                if token > obj_hash:
                    results.append(node)
                    break
            else:
                results.append(virtual_nodes[0][1])
        return np.array(results)

    def _split_data(self, data):
        """Split data into chunks for parallel processing"""
        chunk_size = len(data) // self.num_processes
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def hash_mapping(self, objects, num_nodes):
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_hash, num_nodes=num_nodes)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def dht_mapping(self, objects, ring):
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_dht, ring=ring)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def dynamo_mapping(self, objects, num_nodes):
        # 构建虚拟节点
        virtual_nodes = []
        for i in range(num_nodes):
            for j in range(self.Q):
                token = self.get_hash(f"node{i}:token{j}")
                virtual_nodes.append((token, i))
        virtual_nodes.sort(key=lambda x: x[0])

        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_dynamo, virtual_nodes=virtual_nodes)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def generate_distribution(self, distribution_type):
        if distribution_type == 'normal':
            return norm.rvs(loc=self.num_objects/2, scale=self.num_objects/6, size=self.num_objects)
        elif distribution_type == 'zipf':
            return zipf.rvs(a=1.5, size=self.num_objects)
        else:
            raise ValueError("Unsupported distribution type")

    def get_hash(self, key):
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def build_ring(self, num_nodes):
        ring = np.array([(self.get_hash(f"{i}:{j}"), i) for i in range(num_nodes) for j in range(self.virtual_nodes)])
        return ring[np.argsort(ring[:, 0])]

    def simulate(self, distribution_type):
        print(f"Running simulation with {self.num_processes} processes...")
        objects = self.generate_distribution(distribution_type)
        
        print("Computing hash mapping...")
        hash_results = self.hash_mapping(objects, self.num_nodes)
        
        print("Computing DHT mapping...")
        ring = self.build_ring(self.num_nodes)
        dht_results = self.dht_mapping(objects, ring)
        
        print("Computing Dynamo mapping...")
        dynamo_results = self.dynamo_mapping(objects, self.num_nodes)
        
        return objects, hash_results, dht_results, dynamo_results

    def plot_results(self, objects, hash_results, dht_results, dynamo_results, distribution_type):
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 20))

        ax1.hist(objects, bins=50)
        ax1.set_title(f'{distribution_type.capitalize()} Distribution of Objects')
        ax1.set_xlabel('Object ID')
        ax1.set_ylabel('Frequency')

        ax2.hist(hash_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax2.set_title('Simple Hash Mapping Results')
        ax2.set_xlabel('Node ID')
        ax2.set_ylabel('Number of Objects')

        ax3.hist(dht_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax3.set_title('DHT Mapping Results')
        ax3.set_xlabel('Node ID')
        ax3.set_ylabel('Number of Objects')

        ax4.hist(dynamo_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax4.set_title('Dynamo Mapping Results')
        ax4.set_xlabel('Node ID')
        ax4.set_ylabel('Number of Objects')

        plt.tight_layout()
        os.makedirs('output', exist_ok=True)
        plt.savefig(f'output/{distribution_type}_distribution.png')
        plt.close()

    def analyze_node_increase(self, objects, initial_nodes, final_nodes):
        initial_hash = self.hash_mapping(objects, initial_nodes)
        final_hash = self.hash_mapping(objects, final_nodes)
        hash_changes = np.sum(initial_hash != final_hash)

        initial_ring = self.build_ring(initial_nodes)
        final_ring = self.build_ring(final_nodes)
        initial_dht = self.dht_mapping(objects, initial_ring)
        final_dht = self.dht_mapping(objects, final_ring)
        dht_changes = np.sum(initial_dht != final_dht)

        return hash_changes, dht_changes

class TieredCopysetSimulator(ObjectDistributionSimulator):
    def __init__(self, num_objects, num_nodes, replicas=3, num_processes=None):
        super().__init__(num_objects, num_nodes, num_processes)
        self.replicas = replicas
        self.nodes = []
        self.copysets = []
        self.node_to_copysets = {}  # 记录每个节点属于哪些copyset
        
        # 初始化节点，将节点分为主层和备份层
        primary_count = int(num_nodes * 0.7)  # 70%作为主层节点
        for i in range(num_nodes):
            tier = "primary" if i < primary_count else "backup"
            node = Node(i, tier)
            self.nodes.append(node)
            self.node_to_copysets[node.id] = []

    def check_tier(self, copyset):
        """检查copyset是否满足层级要求：R-1个主层节点和1个备份层节点"""
        backup_count = sum(1 for node in copyset.nodes if node.tier == "backup")
        return backup_count == 1

    def did_not_appear(self, copyset):
        """检查copyset是否已经存在"""
        for existing_copyset in self.copysets:
            if copyset.is_same(existing_copyset):
                return False
        return True

    def build_copysets(self):
        """构建满足要求的copysets"""
        done = False
        while not done:
            done = True
            # 按scatter width排序��点
            self.nodes.sort(key=lambda x: x.scatter_width)
            
            for node in self.nodes:
                if node.scatter_width >= self.virtual_nodes:
                    continue
                
                copyset = Copyset()
                copyset.add_node(node)
                
                # 尝试添加其他节点以形成新的copyset
                candidates = sorted(self.nodes, key=lambda x: x.scatter_width)
                for candidate in candidates:
                    if candidate.id == node.id:
                        continue
                    
                    copyset.add_node(candidate)
                    if copyset.size() == self.replicas:
                        if self.check_tier(copyset) and self.did_not_appear(copyset):
                            self.copysets.append(copyset)
                            # 更新scatter width
                            for n in copyset.nodes:
                                self.node_to_copysets[n.id].append(copyset)
                                n.scatter_width = len(set(
                                    other_node.id 
                                    for cs in self.node_to_copysets[n.id]
                                    for other_node in cs.nodes 
                                    if other_node.id != n.id
                                ))
                            done = False
                            break
                        copyset.remove_node(candidate)

    def tiered_mapping(self, objects, num_nodes):
        """基于tiered copyset的对象映射"""
        self.build_copysets()
        
        results = []
        for obj in objects:
            obj_hash = self.get_hash(obj)
            copyset_index = obj_hash % len(self.copysets)
            # 选择copyset中的一个节点作为主节点
            primary_nodes = [n for n in self.copysets[copyset_index].nodes if n.tier == "primary"]
            node = primary_nodes[obj_hash % len(primary_nodes)]
            results.append(node.id)
            
        return np.array(results)

    def simulate(self, distribution_type):
        print(f"Running simulation with {self.num_processes} processes...")
        objects = self.generate_distribution(distribution_type)
        
        print("Computing hash mapping...")
        hash_results = self.hash_mapping(objects, self.num_nodes)
        
        print("Computing DHT mapping...")
        ring = self.build_ring(self.num_nodes)
        dht_results = self.dht_mapping(objects, ring)
        
        print("Computing Dynamo mapping...")
        dynamo_results = self.dynamo_mapping(objects, self.num_nodes)
        
        print("Computing Tiered Copyset mapping...")
        tiered_results = self.tiered_mapping(objects, self.num_nodes)
        
        return objects, hash_results, dht_results, dynamo_results, tiered_results

    def plot_results(self, objects, hash_results, dht_results, dynamo_results, tiered_results, distribution_type):
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 20))

        ax1.hist(objects, bins=50)
        ax1.set_title(f'{distribution_type.capitalize()} Distribution of Objects')
        ax1.set_xlabel('Object ID')
        ax1.set_ylabel('Frequency')

        ax2.hist(hash_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax2.set_title('Simple Hash Mapping Results')
        ax2.set_xlabel('Node ID')
        ax2.set_ylabel('Number of Objects')

        ax3.hist(dht_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax3.set_title('DHT Mapping Results')
        ax3.set_xlabel('Node ID')
        ax3.set_ylabel('Number of Objects')

        ax4.hist(dynamo_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax4.set_title('Dynamo Mapping Results')
        ax4.set_xlabel('Node ID')
        ax4.set_ylabel('Number of Objects')

        ax5.hist(tiered_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax5.set_title('Tiered Copyset Mapping Results')
        ax5.set_xlabel('Node ID')
        ax5.set_ylabel('Number of Objects')

        plt.tight_layout()
        os.makedirs('output', exist_ok=True)
        plt.savefig(f'output/{distribution_type}_distribution.png')
        plt.close()

    def analyze_node_increase(self, objects, initial_nodes, final_nodes):
        initial_hash = self.hash_mapping(objects, initial_nodes)
        final_hash = self.hash_mapping(objects, final_nodes)
        hash_changes = np.sum(initial_hash != final_hash)

        initial_ring = self.build_ring(initial_nodes)
        final_ring = self.build_ring(final_nodes)
        initial_dht = self.dht_mapping(objects, initial_ring)
        final_dht = self.dht_mapping(objects, final_ring)
        dht_changes = np.sum(initial_dht != final_dht)

        return hash_changes, dht_changes

class CrushSimulator(ObjectDistributionSimulator):
    def __init__(self, num_objects, num_nodes, num_processes=None):
        super().__init__(num_objects, num_nodes, num_processes)
        self.buckets = self._create_crush_buckets()
        
    def _create_crush_buckets(self):
        """创建CRUSH的分层结构"""
        # 简化版的CRUSH层级：root -> rack -> host -> device
        num_racks = max(2, self.num_nodes // 20)  # 每个机架约20个节点
        num_hosts_per_rack = max(2, self.num_nodes // num_racks // 5)  # 每个主机约5个设备
        
        buckets = {
            'root': {'type': 'root', 'items': []},
            'racks': [],
            'hosts': [],
            'devices': []
        }
        
        # 创建设备（最底层）
        for i in range(self.num_nodes):
            device = {
                'id': i,
                'type': 'device',
                'weight': 1.0,  # 假设所有设备权重相同
                'pos': i
            }
            buckets['devices'].append(device)
        
        # 创建主机
        host_id = 0
        for i in range(num_racks * num_hosts_per_rack):
            host = {
                'id': f'host-{host_id}',
                'type': 'host',
                'items': [],
                'weight': 0
            }
            devices_per_host = len(buckets['devices']) // (num_racks * num_hosts_per_rack)
            start_idx = i * devices_per_host
            end_idx = start_idx + devices_per_host
            for device in buckets['devices'][start_idx:end_idx]:
                host['items'].append(device)
                host['weight'] += device['weight']
            buckets['hosts'].append(host)
            host_id += 1
        
        # 创建机架
        for i in range(num_racks):
            rack = {
                'id': f'rack-{i}',
                'type': 'rack',
                'items': [],
                'weight': 0
            }
            hosts_per_rack = len(buckets['hosts']) // num_racks
            start_idx = i * hosts_per_rack
            end_idx = start_idx + hosts_per_rack
            for host in buckets['hosts'][start_idx:end_idx]:
                rack['items'].append(host)
                rack['weight'] += host['weight']
            buckets['racks'].append(rack)
            buckets['root']['items'].append(rack)
        
        return buckets

    def _crush_hash(self, x, r):
        """CRUSH哈希函数"""
        h = hashlib.md5(f"{x}:{r}".encode()).hexdigest()
        return int(h, 16)

    def _select_bucket_items(self, bucket, value, count):
        """从bucket中选择指定数量的项"""
        selected = []
        r = 0
        while len(selected) < count:
            hash_value = self._crush_hash(value, r)
            pos = hash_value % len(bucket['items'])
            item = bucket['items'][pos]
            if item not in selected:
                selected.append(item)
            r += 1
        return selected

    def crush_mapping(self, objects, replicas=3):
        """使用CRUSH算法进行对象映射"""
        results = []
        for obj in objects:
            # 首先选择机架
            racks = self._select_bucket_items(self.buckets['root'], obj, replicas)
            
            # 从每个机架中选择主机
            selected_devices = []
            for rack in racks:
                hosts = self._select_bucket_items(rack, obj, 1)
                for host in hosts:
                    devices = self._select_bucket_items(host, obj, 1)
                    selected_devices.extend(d['id'] for d in devices)
            
            # 只返回主副本的位置
            results.append(selected_devices[0])
        
        return np.array(results)

    def simulate(self, distribution_type):
        objects, hash_results, dht_results, dynamo_results = super().simulate(distribution_type)
        
        print("Computing CRUSH mapping...")
        crush_results = self.crush_mapping(objects)
        
        return objects, hash_results, dht_results, dynamo_results, crush_results

    def plot_results(self, objects, hash_results, dht_results, dynamo_results, crush_results, distribution_type):
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 25))
        
        ax1.hist(objects, bins=50)
        ax1.set_title(f'{distribution_type.capitalize()} Distribution of Objects')
        ax1.set_xlabel('Object ID')
        ax1.set_ylabel('Frequency')

        ax2.hist(hash_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax2.set_title('Simple Hash Mapping Results')
        ax2.set_xlabel('Node ID')
        ax2.set_ylabel('Number of Objects')

        ax3.hist(dht_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax3.set_title('DHT Mapping Results')
        ax3.set_xlabel('Node ID')
        ax3.set_ylabel('Number of Objects')

        ax4.hist(dynamo_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax4.set_title('Dynamo Mapping Results')
        ax4.set_xlabel('Node ID')
        ax4.set_ylabel('Number of Objects')

        ax5.hist(crush_results, bins=self.num_nodes, range=(0, self.num_nodes))
        ax5.set_title('CRUSH Mapping Results')
        ax5.set_xlabel('Node ID')
        ax5.set_ylabel('Number of Objects')
        
        plt.tight_layout()
        os.makedirs('output', exist_ok=True)
        plt.savefig(f'output/{distribution_type}_distribution.png')
        plt.close()

if __name__ == '__main__':
    # 设置进程数为CPU核心数
    num_processes = mp.cpu_count()
    print(f"Using {num_processes} CPU cores")
    
    simulator = TieredCopysetSimulator(
        num_objects=100000,  # 增加对象数量以更好地展示并行计算的优势
        num_nodes=100,
        num_processes=num_processes
    )

    for dist_type in ['normal', 'zipf']:
        print(f"\nProcessing {dist_type} distribution...")
        objects, hash_results, dht_results, dynamo_results, tiered_results = simulator.simulate(dist_type)
        simulator.plot_results(objects, hash_results, dht_results, dynamo_results, tiered_results, dist_type)

        initial_nodes = 100
        final_nodes = 105
        hash_changes, dht_changes = simulator.analyze_node_increase(objects, initial_nodes, final_nodes)
        
        print(f"\n{dist_type.capitalize()} Distribution Results:")
        print(f"Number of nodes increased from {initial_nodes} to {final_nodes}")
        print(f"Objects changed in Simple Hash mapping: {hash_changes}")
        print(f"Objects changed in DHT mapping: {dht_changes}")
        print(f"Change ratio - Simple Hash: {hash_changes/len(objects):.2%}, DHT: {dht_changes/len(objects):.2%}")

        hash_std = np.std([np.sum(hash_results == i) for i in range(simulator.num_nodes)])
        dht_std = np.std([np.sum(dht_results == i) for i in range(simulator.num_nodes)])
        dynamo_std = np.std([np.sum(dynamo_results == i) for i in range(simulator.num_nodes)])
        tiered_std = np.std([np.sum(tiered_results == i) for i in range(simulator.num_nodes)])
        print(f"\nLoad balance (lower is better):")
        print(f"Simple Hash: {hash_std:.2f}")
        print(f"DHT: {dht_std:.2f}")
        print(f"Dynamo: {dynamo_std:.2f}")
        print(f"Tiered Copyset: {tiered_std:.2f}")
