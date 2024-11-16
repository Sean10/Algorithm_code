import matplotlib.pyplot as plt
import numpy as np
import os

class DistributionVisualizer:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_distribution_comparison(self, results_dict, distribution_type):
        """绘制不同算法的分布对比图"""
        num_algorithms = len(results_dict)
        fig, axes = plt.subplots(num_algorithms + 1, 1, figsize=(10, 5 * (num_algorithms + 1)))
        
        # 绘制原始对象分布
        objects = results_dict['objects']
        axes[0].hist(objects, bins=50)
        axes[0].set_title(f'{distribution_type.capitalize()} Distribution of Objects')
        axes[0].set_xlabel('Object ID')
        axes[0].set_ylabel('Frequency')

        # 绘制每个算法的映射结果
        for i, (name, results) in enumerate(results_dict.items()):
            if name == 'objects':
                continue
            ax = axes[i + 1]
            ax.hist(results, bins=len(np.unique(results)), range=(0, max(results)))
            ax.set_title(f'{name} Mapping Results')
            ax.set_xlabel('Node ID')
            ax.set_ylabel('Number of Objects')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{distribution_type}_comparison.png')
        plt.close()

    def plot_load_balance(self, results_dict, num_nodes):
        """绘制负载均衡对比图"""
        algorithms = [name for name in results_dict.keys() if name != 'objects']
        std_devs = []
        
        for algo in algorithms:
            results = results_dict[algo]
            load = [np.sum(results == i) for i in range(num_nodes)]
            std_devs.append(np.std(load))

        plt.figure(figsize=(10, 6))
        plt.bar(algorithms, std_devs)
        plt.title('Load Balance Comparison (Lower is Better)')
        plt.xlabel('Algorithm')
        plt.ylabel('Standard Deviation')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/load_balance_comparison.png')
        plt.close()

    def plot_node_change_impact(self, change_results, num_objects):
        """绘制节点变化影响对比图"""
        algorithms = list(change_results.keys())
        changes = [changes/num_objects * 100 for changes in change_results.values()]

        plt.figure(figsize=(10, 6))
        plt.bar(algorithms, changes)
        plt.title('Impact of Node Changes (Lower is Better)')
        plt.xlabel('Algorithm')
        plt.ylabel('Percentage of Objects Remapped')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/node_change_impact.png')
        plt.close() 