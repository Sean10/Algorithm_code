import unittest
import numpy as np
from object_distribution.simulators.crush import CrushSimulator

class TestCrushSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = CrushSimulator(num_objects=1000, num_nodes=10)

    def test_bucket_creation(self):
        buckets = self.simulator.buckets
        self.assertIn('root', buckets)
        self.assertIn('racks', buckets)
        self.assertIn('hosts', buckets)
        self.assertIn('devices', buckets)
        
        # 检查设备数量
        self.assertEqual(len(buckets['devices']), 10)
        
        # 检查层级关系
        self.assertTrue(len(buckets['racks']) > 0)
        self.assertTrue(len(buckets['hosts']) > 0)
        self.assertTrue(len(buckets['root']['items']) > 0)

    def test_item_selection(self):
        # 测试从bucket中选择项目
        bucket = {
            'items': [{'id': i} for i in range(5)]
        }
        selected = self.simulator._select_bucket_items(bucket, 'test_value', 3)
        self.assertEqual(len(selected), 3)
        self.assertEqual(len(set(item['id'] for item in selected)), 3)  # 确保没有重复

    def test_crush_mapping(self):
        objects = np.array([1, 2, 3, 4, 5])
        results = self.simulator.crush_mapping(objects)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_simulation(self):
        objects, results = self.simulator.simulate('normal')
        self.assertEqual(len(objects), 1000)
        self.assertEqual(len(results), 1000)
        self.assertTrue(all(0 <= x < 10 for x in results))

    def test_failure_domains(self):
        # 测试故障域隔离
        objects = np.array([1])
        results = self.simulator.crush_mapping(objects, replicas=3)
        
        # 获取选中设备所属的机架
        def get_rack_id(device_id):
            for rack in self.simulator.buckets['racks']:
                for host in rack['items']:
                    for device in host['items']:
                        if device['id'] == device_id:
                            return rack['id']
            return None
        
        # 验证副本是否分布在不同的机架上
        rack_ids = set(get_rack_id(device_id) for device_id in results)
        self.assertTrue(len(rack_ids) > 1)  # 确保副本分布在不同的机架上

if __name__ == '__main__':
    unittest.main() 