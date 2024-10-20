import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, zipf
import hashlib
import os

class ObjectDistributionSimulator:
    def __init__(self, num_objects, num_nodes):
        self.num_objects = num_objects
        self.num_nodes = num_nodes
        self.virtual_nodes = 1000

    def generate_distribution(self, distribution_type):
        if distribution_type == 'normal':
            return norm.rvs(loc=self.num_objects/2, scale=self.num_objects/6, size=self.num_objects)
        elif distribution_type == 'zipf':
            return zipf.rvs(a=1.5, size=self.num_objects)
        else:
            raise ValueError("Unsupported distribution type")

    def hash_mapping(self, objects, num_nodes):
        # 使用 NumPy 的 vectorize 函数来并行化哈希计算
        hash_func = np.vectorize(lambda x: hash(x) % num_nodes)
        return hash_func(objects)

    def get_hash(self, key):
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def build_ring(self, num_nodes):
        ring = np.array([(self.get_hash(f"{i}:{j}"), i) for i in range(num_nodes) for j in range(self.virtual_nodes)])
        return ring[np.argsort(ring[:, 0])]

    def dht_mapping(self, objects, ring):
        keys = np.array([self.get_hash(obj) for obj in objects])
        indices = np.searchsorted(ring[:, 0], keys, side='right') % len(ring)
        return ring[indices, 1]

    def simulate(self, distribution_type):
        objects = self.generate_distribution(distribution_type)
        hash_results = self.hash_mapping(objects, self.num_nodes)
        
        ring = self.build_ring(self.num_nodes)
        dht_results = self.dht_mapping(objects, ring)
        
        return objects, hash_results, dht_results

    def plot_results(self, objects, hash_results, dht_results, distribution_type):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

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

# 使用示例
simulator = ObjectDistributionSimulator(num_objects=100000, num_nodes=100)

for dist_type in ['normal', 'zipf']:
    objects, hash_results, dht_results = simulator.simulate(dist_type)
    simulator.plot_results(objects, hash_results, dht_results, dist_type)

    initial_nodes = 100
    final_nodes = 105
    hash_changes, dht_changes = simulator.analyze_node_increase(objects, initial_nodes, final_nodes)
    
    print(f"{dist_type.capitalize()} Distribution:")
    print(f"Number of nodes increased from {initial_nodes} to {final_nodes}")
    print(f"Objects changed in Simple Hash mapping: {hash_changes}")
    print(f"Objects changed in DHT mapping: {dht_changes}")
    print(f"Change ratio - Simple Hash: {hash_changes/len(objects):.2%}, DHT: {dht_changes/len(objects):.2%}")
    print()

    hash_std = np.std([np.sum(hash_results == i) for i in range(simulator.num_nodes)])
    dht_std = np.std([np.sum(dht_results == i) for i in range(simulator.num_nodes)])
    print(f"Load balance (lower is better) - Simple Hash: {hash_std:.2f}, DHT: {dht_std:.2f}")
    print()
