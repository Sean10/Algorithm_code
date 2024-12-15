import unittest
from object_distribution.simulators.round_robin import RoundRobinSimulator

class TestRoundRobinSimulator(unittest.TestCase):
    """测试轮询分配策略模拟器"""

    def setUp(self):
        self.num_nodes = 3
        self.simulator = RoundRobinSimulator(self.num_nodes)

    def test_assign_object(self):
        """测试对象分配"""
        # 分配第一个对象
        node = self.simulator.assign_object("object_0")
        self.assertEqual(node.id, 0)

        # 分配第二个对象
        node = self.simulator.assign_object("object_1")
        self.assertEqual(node.id, 1)

        # 分配第三个对象
        node = self.simulator.assign_object("object_2")
        self.assertEqual(node.id, 2)

        # 分配第四个对象，应该回到第一个节点
        node = self.simulator.assign_object("object_3")
        self.assertEqual(node.id, 0)

    def test_run_simulation(self):
        """测试运行模拟"""
        num_objects = 6
        nodes = self.simulator.run_simulation(num_objects)

        # 检查每个节点分配的对象数量
        for node in nodes:
            self.assertEqual(len(node.objects), 2)

if __name__ == '__main__':
    unittest.main()