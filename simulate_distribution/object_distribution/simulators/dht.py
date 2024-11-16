import numpy as np
import multiprocessing as mp
from functools import partial
from .base import BaseSimulator
from ..utils.hash_utils import get_hash

class DHTSimulator(BaseSimulator):
    def __init__(self, num_objects, num_nodes, num_processes=None):
        super().__init__(num_objects, num_nodes, num_processes)
        self.virtual_nodes = 1000

    def build_ring(self, num_nodes):
        """构建一致性哈希环"""
        ring = np.array([
            (get_hash(f"{i}:{j}"), i) 
            for i in range(num_nodes) 
            for j in range(self.virtual_nodes)
        ])
        return ring[np.argsort(ring[:, 0])]

    def _parallel_dht(self, chunk, ring):
        """并行处理DHT映射"""
        keys = np.array([get_hash(obj) for obj in chunk])
        indices = np.searchsorted(ring[:, 0], keys, side='right') % len(ring)
        return ring[indices, 1]

    def dht_mapping(self, objects, ring):
        """使用多进程进行DHT映射"""
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_dht, ring=ring)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def simulate(self, distribution_type):
        objects = self.generate_distribution(distribution_type)
        ring = self.build_ring(self.num_nodes)
        dht_results = self.dht_mapping(objects, ring)
        return objects, dht_results 