import time
import numpy as np
from functools import wraps
import psutil
import os

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = {}

    def measure_time(self, func_name):
        """装饰器：测量函数执行时间"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                if func_name not in self.metrics:
                    self.metrics[func_name] = []
                self.metrics[func_name].append(end_time - start_time)
                
                return result
            return wrapper
        return decorator

    def measure_memory(self):
        """测量当前内存使用情况"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # 转换为MB

    def analyze_load_balance(self, results_dict, num_nodes):
        """分析负载均衡性能"""
        balance_metrics = {}
        for name, results in results_dict.items():
            if name == 'objects':
                continue
            load = [np.sum(results == i) for i in range(num_nodes)]
            balance_metrics[name] = {
                'std_dev': np.std(load),
                'max_load': np.max(load),
                'min_load': np.min(load),
                'avg_load': np.mean(load)
            }
        return balance_metrics

    def analyze_node_change_impact(self, change_results, num_objects):
        """分析节点变化的影响"""
        impact_metrics = {}
        for algo, changes in change_results.items():
            impact_metrics[algo] = {
                'absolute_changes': changes,
                'change_ratio': changes / num_objects,
                'stability_score': 1 - (changes / num_objects)
            }
        return impact_metrics

    def get_summary(self):
        """生成性能分析总结"""
        summary = {
            'execution_times': {},
            'memory_usage': self.measure_memory()
        }
        
        for func_name, times in self.metrics.items():
            summary['execution_times'][func_name] = {
                'avg_time': np.mean(times),
                'max_time': np.max(times),
                'min_time': np.min(times),
                'std_dev': np.std(times)
            }
            
        return summary

    def print_summary(self):
        """打印性能分析结果"""
        summary = self.get_summary()
        
        print("\nPerformance Analysis Summary:")
        print("-" * 50)
        
        print("\nExecution Times (seconds):")
        for func_name, metrics in summary['execution_times'].items():
            print(f"\n{func_name}:")
            print(f"  Average: {metrics['avg_time']:.4f}")
            print(f"  Maximum: {metrics['max_time']:.4f}")
            print(f"  Minimum: {metrics['min_time']:.4f}")
            print(f"  Std Dev: {metrics['std_dev']:.4f}")
        
        print(f"\nMemory Usage: {summary['memory_usage']:.2f} MB") 