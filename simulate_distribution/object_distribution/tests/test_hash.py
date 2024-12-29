import unittest
import numpy as np
from object_distribution.simulators.hash import HashSimulator
from collections import Counter

class TestHashSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = HashSimulator(num_objects=1000, num_nodes=10)
        # 为算法比较测试设置更大的规模
        self.comparison_num_objects = 10000
        self.comparison_num_nodes = 100

    def test_distribution_generation(self):
        objects = self.simulator.generate_distribution('normal')
        self.assertEqual(len(objects), 1000)
        
        objects = self.simulator.generate_distribution('zipf')
        self.assertEqual(len(objects), 1000)

        objects = self.simulator.generate_distribution('uniform')
        self.assertEqual(len(objects), 1000)

    def test_hash_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        results = self.simulator.hash_mapping(objects, 10)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_invalid_distribution(self):
        with self.assertRaises(ValueError):
            self.simulator.generate_distribution('invalid')

    def test_invalid_hash_type(self):
        with self.assertRaises(ValueError):
            HashSimulator(num_objects=1000, num_nodes=10, hash_type='invalid')

    def _calculate_distribution_metrics(self, results):
        """计算分布指标"""
        counts = Counter(results)
        loads = np.array(list(counts.values()))
        return {
            'min_load': np.min(loads),
            'max_load': np.max(loads),
            'mean_load': np.mean(loads),
            'std_load': np.std(loads),
            'load_imbalance': (np.max(loads) - np.min(loads)) / np.mean(loads)
        }

    def test_hash_algorithms_comparison(self):
        """比较不同哈希算法的分布特性"""
        hash_types = ['python', 'rjenkins']
        results = {}
        
        for hash_type in hash_types:
            simulator = HashSimulator(
                num_objects=self.comparison_num_objects,
                num_nodes=self.comparison_num_nodes,
                hash_type=hash_type
            )
            _, hash_results = simulator.simulate('uniform')
            metrics = self._calculate_distribution_metrics(hash_results)
            results[hash_type] = metrics
            
            # 基本断言
            self.assertTrue(0 <= hash_results.min() < self.comparison_num_nodes)
            self.assertTrue(0 <= hash_results.max() < self.comparison_num_nodes)
            
            # 负载均衡性检查
            expected_load = self.comparison_num_objects / self.comparison_num_nodes
            self.assertLess(
                metrics['load_imbalance'], 
                0.6,  # 允许60%的负载不平衡
                f"{hash_type}的负载不平衡度过高: {metrics['load_imbalance']}"
            )
            
            # 标准差检查
            self.assertLess(
                metrics['std_load'] / expected_load,
                0.35,  # 标准差应该小于平均负载的35%
                f"{hash_type}的负载分布标准差过大"
            )
        
        # 比较不同算法的性能
        for metric in ['load_imbalance', 'std_load']:
            print(f"\n{metric}比较:")
            for hash_type, metrics in results.items():
                print(f"{hash_type}: {metrics[metric]:.4f}")

if __name__ == '__main__':
    unittest.main() 