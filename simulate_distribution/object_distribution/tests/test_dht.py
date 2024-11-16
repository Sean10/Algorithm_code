import unittest
import numpy as np
from object_distribution.simulators.dht import DHTSimulator

class TestDHTSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = DHTSimulator(num_objects=1000, num_nodes=10)

    def test_ring_creation(self):
        ring = self.simulator.build_ring(10)
        self.assertEqual(len(ring), 10 * self.simulator.virtual_nodes)
        self.assertTrue(np.all(np.diff(ring[:, 0]) >= 0))  # 确保环是有序的

    def test_dht_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        ring = self.simulator.build_ring(10)
        results = self.simulator.dht_mapping(objects, ring)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_simulation(self):
        objects, results = self.simulator.simulate('normal')
        self.assertEqual(len(objects), 1000)
        self.assertEqual(len(results), 1000)
        self.assertTrue(all(0 <= x < 10 for x in results))

if __name__ == '__main__':
    unittest.main() 