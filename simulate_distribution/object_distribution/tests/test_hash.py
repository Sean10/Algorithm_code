import unittest
import numpy as np
from object_distribution.simulators.hash import HashSimulator

class TestHashSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = HashSimulator(num_objects=1000, num_nodes=10)

    def test_distribution_generation(self):
        objects = self.simulator.generate_distribution('normal')
        self.assertEqual(len(objects), 1000)
        
        objects = self.simulator.generate_distribution('zipf')
        self.assertEqual(len(objects), 1000)

    def test_hash_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        results = self.simulator.hash_mapping(objects, 10)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_invalid_distribution(self):
        with self.assertRaises(ValueError):
            self.simulator.generate_distribution('invalid')

if __name__ == '__main__':
    unittest.main() 