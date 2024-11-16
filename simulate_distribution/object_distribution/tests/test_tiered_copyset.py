import unittest
import numpy as np
from object_distribution.simulators.tiered_copyset import TieredCopysetSimulator

class TestTieredCopysetSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = TieredCopysetSimulator(num_objects=1000, num_nodes=10)

    def test_node_initialization(self):
        self.assertEqual(len(self.simulator.nodes), 10)
        primary_nodes = sum(1 for node in self.simulator.nodes if node.tier == "primary")
        self.assertEqual(primary_nodes, 7)  # 70% should be primary

    def test_copyset_building(self):
        self.simulator.build_copysets()
        self.assertTrue(len(self.simulator.copysets) > 0)
        for copyset in self.simulator.copysets:
            self.assertEqual(copyset.size(), self.simulator.replicas)
            self.assertTrue(self.simulator.check_tier(copyset))

    def test_tiered_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        results = self.simulator.tiered_mapping(objects)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_simulation(self):
        objects, results = self.simulator.simulate('normal')
        self.assertEqual(len(objects), 1000)
        self.assertEqual(len(results), 1000)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_scatter_width(self):
        self.simulator.build_copysets()
        for node in self.simulator.nodes:
            self.assertTrue(hasattr(node, 'scatter_width'))
            self.assertTrue(isinstance(node.scatter_width, int))

if __name__ == '__main__':
    unittest.main() 