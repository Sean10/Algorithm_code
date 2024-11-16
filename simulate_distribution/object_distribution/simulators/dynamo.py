import numpy as np
import multiprocessing as mp
from functools import partial
from .base import BaseSimulator
from ..utils.hash_utils import get_hash

class DynamoSimulator(BaseSimulator):
    def __init__(self, num_objects, num_nodes, num_processes=None, Q=3):
        super().__init__(num_objects, num_nodes, num_processes)
        self.Q = Q  # Q-way replication

    def _build_virtual_nodes(self):
        """构建Dynamo的虚拟节点"""
        virtual_nodes = []
        for i in range(self.num_nodes):
            for j in range(self.Q):
                token = get_hash(f"node{i}:token{j}")
                virtual_nodes.append((token, i))
        return sorted(virtual_nodes, key=lambda x: x[0])

    def _parallel_dynamo(self, chunk, virtual_nodes):
        """并行处理Dynamo映射"""
        results = []
        for obj in chunk:
            obj_hash = get_hash(obj)
            for token, node in virtual_nodes:
                if token > obj_hash:
                    results.append(node)
                    break
            else:
                results.append(virtual_nodes[0][1])
        return np.array(results)

    def dynamo_mapping(self, objects):
        """使用多进程进行Dynamo映射"""
        virtual_nodes = self._build_virtual_nodes()
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_dynamo, virtual_nodes=virtual_nodes)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def simulate(self, distribution_type):
        objects = self.generate_distribution(distribution_type)
        dynamo_results = self.dynamo_mapping(objects)
        return objects, dynamo_results 