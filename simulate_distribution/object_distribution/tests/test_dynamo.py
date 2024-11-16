import unittest
import numpy as np
from object_distribution.simulators.dynamo import DynamoSimulator

class TestDynamoSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = DynamoSimulator(num_objects=1000, num_nodes=10)

    def test_virtual_nodes_creation(self):
        virtual_nodes = self.simulator._build_virtual_nodes()
        self.assertEqual(len(virtual_nodes), 10 * self.simulator.Q)
        self.assertTrue(all(isinstance(node[1], int) for node in virtual_nodes))

    def test_dynamo_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        results = self.simulator.dynamo_mapping(objects)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_simulation(self):
        objects, results = self.simulator.simulate('normal')
        self.assertEqual(len(objects), 1000)
        self.assertEqual(len(results), 1000)
        self.assertTrue(all(0 <= x < 10 for x in results))

if __name__ == '__main__':
    unittest.main() 