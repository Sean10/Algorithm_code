import os
import numpy as np
from object_distribution.simulators import (
    HashSimulator,
    DHTSimulator,
    DynamoSimulator,
    TieredCopysetSimulator,
    CrushSimulator, 
    RoundRobinSimulator
)
from object_distribution.utils.visualization import DistributionVisualizer
from object_distribution.utils.performance import PerformanceAnalyzer
import multiprocessing as mp

class SimulationRunner:
    def __init__(self, num_objects=100000, num_nodes=100, enabled_algorithms=None, num_processes=None):
        self.num_objects = num_objects
        self.num_nodes = num_nodes
        self.visualizer = DistributionVisualizer()
        self.analyzer = PerformanceAnalyzer()
        
        # 如果未指定进程数，使用CPU核数-2
        self.num_processes = num_processes or max(1, mp.cpu_count() - 2)
        
        # 创建所有可用的模拟器
        all_simulators = {
            'Hash': HashSimulator(num_objects, num_nodes, num_processes=self.num_processes),
            'DHT': DHTSimulator(num_objects, num_nodes, num_processes=self.num_processes),
            'Dynamo': DynamoSimulator(num_objects, num_nodes, num_processes=self.num_processes),
            'TieredCopyset': TieredCopysetSimulator(num_objects, num_nodes, num_processes=self.num_processes),
            'CRUSH': CrushSimulator(num_objects, num_nodes, num_processes=self.num_processes),
            'RoundRobin': RoundRobinSimulator(num_objects, num_nodes, num_processes=self.num_processes)
        }
        
        # 如果指定了算法，只使用指定的算法
        if enabled_algorithms:
            self.simulators = {k: v for k, v in all_simulators.items() if k in enabled_algorithms}
        else:
            self.simulators = all_simulators
        
        # 装饰run_simulations方法
        self.run_simulations = PerformanceAnalyzer.profile_cpu(self.analyzer)(self.run_simulations)

    def enable_profiling(self, enable=True):
        """启用或禁用性能分析"""
        self.analyzer.enable_profiling = enable

    def run_simulations(self, distribution_type):
        """运行模拟"""
        results = {'objects': None}
        
        for name, simulator in self.simulators.items():
            print(f"\nRunning {name} simulation...")
            simulation_results = simulator.simulate(distribution_type)
            
            if results['objects'] is None:
                results['objects'] = simulation_results[0]
            results[name] = simulation_results[-1]
            
        return results

    def analyze_node_changes(self, distribution_type, initial_nodes=100, final_nodes=200):
        change_results = {}
        objects = next(iter(self.simulators.values())).generate_distribution(distribution_type)
        
        for name, simulator in self.simulators.items():
            print(f"\nAnalyzing {name} node changes...")
            initial_mapping = simulator.simulate(distribution_type)[-1]
            
            # 临时更新节点数
            original_nodes = simulator.num_nodes
            simulator.num_nodes = final_nodes
            final_mapping = simulator.simulate(distribution_type)[-1]
            simulator.num_nodes = original_nodes
            
            changes = np.sum(initial_mapping != final_mapping)
            change_results[name] = changes
            
        return change_results

    def run_complete_analysis(self):
        distributions = ['normal', 'zipf']
        
        for dist_type in distributions:
            print(f"\n{'='*20} Processing {dist_type} distribution {'='*20}")
            
            # 运行模拟
            results = self.run_simulations(dist_type)
            
            # 可视化分布
            self.visualizer.plot_distribution_comparison(results, dist_type)
            
            # 分析负载均衡
            balance_metrics = self.analyzer.analyze_load_balance(results, self.num_nodes)
            self.visualizer.plot_load_balance(results, self.num_nodes)
            
            # 分析节点变化影响
            change_results = self.analyze_node_changes(dist_type)
            self.visualizer.plot_node_change_impact(change_results, self.num_objects)
            
            # 打印性能分析结果
            print("\nLoad Balance Analysis:")
            for algo, metrics in balance_metrics.items():
                print(f"\n{algo}:")
                print(f"  Standard Deviation: {metrics['std_dev']:.2f}")
                print(f"  Max/Min Load Ratio: {metrics['max_load']/metrics['min_load']:.2f}")
                
            print("\nNode Change Impact Analysis:")
            impact_metrics = self.analyzer.analyze_node_change_impact(change_results, self.num_objects)
            for algo, metrics in impact_metrics.items():
                print(f"\n{algo}:")
                print(f"  Change Ratio: {metrics['change_ratio']:.2%}")
                print(f"  Stability Score: {metrics['stability_score']:.2f}")

        # 打印整体性能分析
        self.analyzer.print_cpu_stats()
        self.analyzer.print_line_stats()

def main():
    print("Starting Object Distribution Simulation...")
    print(f"Using {os.cpu_count()} CPU cores")
    
    runner = SimulationRunner(
        num_objects=1000000,  # 使用更大的数据集
        num_nodes=100
    )
    
    runner.run_complete_analysis()
    
    print("\nSimulation completed. Results are available in the 'output' directory.")

if __name__ == '__main__':
    main() 