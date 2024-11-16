import numpy as np
import multiprocessing as mp
from functools import partial
from .base import BaseSimulator
from ..utils.hash_utils import get_hash, crush_hash

class CrushSimulator(BaseSimulator):
    def __init__(self, num_objects, num_nodes, num_processes=None):
        super().__init__(num_objects, num_nodes, num_processes)
        self.buckets = self._create_crush_buckets()
        
    def _create_crush_buckets(self):
        """创建CRUSH的分层结构"""
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
                'weight': 1.0,
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

    def _select_bucket_items(self, bucket, value, count):
        """从bucket中选择指定数量的项"""
        selected = []
        r = 0
        while len(selected) < count:
            hash_value = crush_hash(value, r)
            pos = hash_value % len(bucket['items'])
            item = bucket['items'][pos]
            if item not in selected:
                selected.append(item)
            r += 1
        return selected

    def _parallel_crush(self, chunk, replicas=3):
        """并行处理CRUSH映射"""
        results = []
        for obj in chunk:
            # 首先选择机架
            racks = self._select_bucket_items(self.buckets['root'], obj, replicas)
            
            # 从每个机架中选择主机和设备
            selected_devices = []
            for rack in racks:
                hosts = self._select_bucket_items(rack, obj, 1)
                for host in hosts:
                    devices = self._select_bucket_items(host, obj, 1)
                    selected_devices.extend(d['id'] for d in devices)
            
            # 只返回主副本的位置
            results.append(selected_devices[0])
        
        return np.array(results)

    def crush_mapping(self, objects, replicas=3):
        """使用多进程进行CRUSH映射"""
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_crush, replicas=replicas)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def simulate(self, distribution_type):
        objects = self.generate_distribution(distribution_type)
        crush_results = self.crush_mapping(objects)
        return objects, crush_results 