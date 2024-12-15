import argparse
import json
import os
import multiprocessing as mp
from object_distribution.examples.main import SimulationRunner

def parse_args():
    parser = argparse.ArgumentParser(description='Object Distribution Simulator CLI')
    
    # 基本参数
    parser.add_argument('--num-objects', type=int, default=100000,
                      help='Number of objects to simulate (default: 100000)')
    parser.add_argument('--num-nodes', type=int, default=100,
                      help='Number of nodes in the system (default: 100)')
    parser.add_argument('--num-processes', type=int, 
                      default=max(1, mp.cpu_count() - 2),
                      help='Number of processes to use (default: CPU count - 2)')
    parser.add_argument('--distributions', nargs='+', default=['normal', 'zipf'],
                      choices=['normal', 'zipf'],
                      help='Distribution types to simulate (default: normal zipf)')
    
    # 算法选择
    parser.add_argument('--algorithms', nargs='+',
                      default=['Hash', 'DHT', 'Dynamo', 'TieredCopyset', 'CRUSH', 'RoundRobin'],
                      choices=['Hash', 'DHT', 'Dynamo', 'TieredCopyset', 'CRUSH', 'RoundRobin'],
                      help='Algorithms to simulate')
    
    # 性能分析选项
    parser.add_argument('--analyze-node-changes', action='store_true',
                      help='Analyze impact of node changes')
    parser.add_argument('--initial-nodes', type=int, default=100,
                      help='Initial number of nodes for change analysis')
    parser.add_argument('--final-nodes', type=int, default=200,
                      help='Final number of nodes for change analysis')
    
    # 输出选项
    parser.add_argument('--output-dir', type=str, default='output',
                      help='Directory for output files (default: output)')
    parser.add_argument('--save-metrics', action='store_true',
                      help='Save performance metrics to JSON file')
    parser.add_argument('--no-plots', action='store_true',
                      help='Disable plot generation')
    
    # 添加性能分析选项
    parser.add_argument('--profile', action='store_true',
                      help='Enable detailed CPU profiling')
    parser.add_argument('--profile-lines', action='store_true',
                      help='Enable line-by-line profiling')
    
    return parser.parse_args()

def save_metrics(metrics, output_dir):
    """保存性能指标到JSON文件"""
    os.makedirs(output_dir, exist_ok=True)
    metrics_file = os.path.join(output_dir, 'metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {metrics_file}")

def main():
    args = parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 初始化模拟器
    runner = SimulationRunner(
        num_objects=args.num_objects,
        num_nodes=args.num_nodes,
        enabled_algorithms=args.algorithms,
        num_processes=args.num_processes
    )
    
    # 如果启用了性能分析，设置profiling
    if args.profile:
        runner.enable_profiling(True)
    
    # 运行模拟
    metrics = {}
    for dist_type in args.distributions:
        print(f"\n{'='*20} Processing {dist_type} distribution {'='*20}")
        
        # 运行模拟并收集结果
        results = runner.run_simulations(dist_type)
        metrics[dist_type] = {}
        
        # 生成可视化
        if not args.no_plots:
            runner.visualizer.plot_distribution_comparison(results, dist_type)
            
        # 分析负载均衡
        balance_metrics = runner.analyzer.analyze_load_balance(results, args.num_nodes)
        metrics[dist_type]['load_balance'] = balance_metrics
        
        # 分析节点变化影响
        if args.analyze_node_changes:
            change_results = runner.analyze_node_changes(
                dist_type, 
                args.initial_nodes, 
                args.final_nodes
            )
            metrics[dist_type]['node_changes'] = runner.analyzer.analyze_node_change_impact(
                change_results, 
                args.num_objects
            )
    
    # 保存性能指标
    if args.save_metrics:
        save_metrics(metrics, args.output_dir)
    
    # 打印性能分析总结
    runner.analyzer.print_summary()
    
    # 如果启用了性能分析，打印详细信息
    if args.profile or args.profile_lines:
        print("\nPerformance Analysis:")
        if args.profile:
            runner.analyzer.print_cpu_stats()
        if args.profile_lines:
            runner.analyzer.print_line_stats()

if __name__ == '__main__':
    main() 