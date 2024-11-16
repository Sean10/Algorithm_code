from .base import BaseSimulator
import numpy as np
import multiprocessing as mp
from functools import partial
from ..utils.hash_utils import get_hash

class HashSimulator(BaseSimulator):
    def __init__(self, num_objects, num_nodes, num_processes=None):
        super().__init__(num_objects, num_nodes, num_processes)

    def _parallel_hash(self, chunk, num_nodes):
        """并行处理哈希映射"""
        hash_func = np.vectorize(lambda x: hash(x) % num_nodes)
        return hash_func(chunk)

    def hash_mapping(self, objects, num_nodes):
        """使用多进程进行哈希映射"""
        with mp.Pool(self.num_processes) as pool:
            chunks = self._split_data(objects)
            func = partial(self._parallel_hash, num_nodes=num_nodes)
            results = pool.map(func, chunks)
        return np.concatenate(results)

    def simulate(self, distribution_type):
        """运行模拟"""
        objects = self.generate_distribution(distribution_type)
        hash_results = self.hash_mapping(objects, self.num_nodes)
        return objects, hash_results 