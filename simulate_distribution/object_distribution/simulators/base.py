import numpy as np
from scipy.stats import norm, zipf
import multiprocessing as mp
from functools import partial
from ..utils.hash_utils import get_hash

class BaseSimulator:
    def __init__(self, num_objects, num_nodes, num_processes=None):
        self.num_objects = num_objects
        self.num_nodes = num_nodes
        self.num_processes = num_processes or max(1, mp.cpu_count() - 2)

    def generate_distribution(self, distribution_type):
        if distribution_type == 'normal':
            return norm.rvs(loc=self.num_objects/2, scale=self.num_objects/6, size=self.num_objects)
        elif distribution_type == 'zipf':
            return zipf.rvs(a=1.5, size=self.num_objects)
        else:
            raise ValueError("Unsupported distribution type")

    def _split_data(self, data):
        """Split data into chunks for parallel processing"""
        chunk_size = len(data) // self.num_processes
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def simulate(self, distribution_type):
        """Must be implemented by subclasses"""
        raise NotImplementedError 