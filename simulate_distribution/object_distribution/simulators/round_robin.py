from .base import BaseSimulator

class RoundRobinSimulator(BaseSimulator):
    """轮询分配策略模拟器"""

    def __init__(self, num_objects, num_nodes, num_processes):
        super().__init__(num_objects, num_nodes, num_processes)
        self.current_node = 0
        self.nodes = [0 for i in range(num_nodes)]

    def assign_object(self, obj):
        """将对象分配到节点"""
        node = self.nodes[self.current_node]
        node += 1
        self.current_node = (self.current_node + 1) % self.num_nodes
        return node

    def run_simulation(self, num_objects):
        """运行模拟"""
        for i in range(self.num_objects):
            obj = f"object_{i}"
            self.assign_object(obj)
        return self.nodes

    def simulate(self, num_objects):
        objects = [f"object_{i}" for i in range(self.num_objects)]
        results = []
        for obj in objects:
            node = self.assign_object(obj)
            results.append(node)
        return objects, results