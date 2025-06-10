#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import re

def parse_benchmark_json(filepath):
    """解析Google Benchmark输出的JSON文件，并从文件名中提取系列名称"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # 从文件名中提取系列名称, e.g., memory_comparison_default -> default
    basename = os.path.basename(filepath)
    series_name_from_file = "unknown"
    if "memory_comparison" in basename:
        match = re.search(r'memory_comparison_(\w+)_', basename)
        if match:
            series_name_from_file = match.group(1)
    elif "optimization_comparison" in basename:
        # 假设优化对比测试的系列名在测试名称中
        pass # 在循环中处理

    benchmarks = []
    for bench in data['benchmarks']:
        # 尝试从 'label' 字段解析，这是最可靠的
        label = bench.get('label', '')
        match = re.search(r'([\w_]+)/(\d+)\s+threads', label)
        if match:
            series_name = match.group(1)
            threads = int(match.group(2))
        else:
            # 如果label不匹配，则回退到解析'name'字段
            # Google benchmark fixture tests name format: Fixture_Test/arg1/arg2...
            match = re.match(r'(\w+_\w+)/(\d+)', bench['name'])
            if match:
                series_name = match.group(1)
                threads = int(match.group(2))
            else: # 最后回退到文件名
                series_name = series_name_from_file
                threads = 1 # 无法解析时默认为1
        
        # 针对optimization_comparison的特殊处理
        if "Original" in bench['name']:
            series_name = "OriginalThreadPool"
        elif "Optimized" in bench['name']:
            series_name = "OptimizedThreadPool"

        item = {
            'series': series_name,
            'threads': threads,
            'cpu_time': bench.get('cpu_time'),
            'real_time': bench.get('real_time'),
            'bytes_per_second': bench.get('bytes_per_second'),
            'items_per_second': bench.get('items_per_second'),
            'iterations': bench.get('iterations'),
            'time_unit': bench.get('time_unit'),
        }
        benchmarks.append(item)
        
    return pd.DataFrame(benchmarks)

def plot_comparison(df, y_metric, y_label, title, output_path):
    """通用的对比绘图函数"""
    if 'threads' not in df.columns or y_metric not in df.columns or df[y_metric].isnull().all():
        print(f"警告: 缺少 'threads' 或 '{y_metric}' 列，或者该列全为空值，无法为 '{title}' 绘图。")
        return
        
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 确保series是字符串类型以便正确分组
    df['series'] = df['series'].astype(str)
    
    for series_name, group in df.groupby('series'):
        sorted_group = group.sort_values('threads').dropna(subset=[y_metric])
        if not sorted_group.empty:
            ax.plot(sorted_group['threads'], sorted_group[y_metric], marker='o', linestyle='-', label=series_name)

    ax.set_xlabel('线程数 (Number of Threads)')
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, which='both', linestyle='--')
    ax.set_xticks(df['threads'].unique())
    plt.tight_layout()
    
    filename = f"{title.replace(' ', '_').replace('/', '_')}.png"
    plt.savefig(os.path.join(output_path, filename))
    print(f"图表已保存到: {os.path.join(output_path, filename)}")
    plt.close(fig) # 关闭图形，防止在某些环境下自动显示

def analyze_files(filepaths):
    """分析一个或多个benchmark JSON文件"""
    print(f"--- 正在分析文件: {', '.join(filepaths)} ---")
    
    all_dfs = []
    for filepath in filepaths:
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}，已跳过。")
            continue
        try:
            df = parse_benchmark_json(filepath)
            all_dfs.append(df)
        except Exception as e:
            print(f"解析文件 {filepath} 时出错: {e}")

    if not all_dfs:
        print("没有可供分析的数据。")
        return
        
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # 打印数据摘要
    print("\nBenchmark 数据摘要:")
    display_cols = ['series', 'threads', 'real_time', 'items_per_second', 'bytes_per_second']
    existing_cols = [col for col in display_cols if col in combined_df.columns]
    print(combined_df[existing_cols].to_string())
    
    # 假设所有文件都在同一个输出目录
    output_dir = os.path.dirname(filepaths[0])
    
    # 根据文件名或内容决定绘图类型
    is_memory_test = any("memory_comparison" in f for f in filepaths)
    is_optimization_test = any("optimization_comparison" in f for f in filepaths)

    if is_memory_test:
        plot_comparison(combined_df, 'bytes_per_second', '吞吐量 (Bytes / Second)', '内存分配器吞吐量对比', output_dir)
        plot_comparison(combined_df, 'real_time', '执行时间 (ms)', '内存分配器执行时间对比', output_dir)
    elif is_optimization_test:
        plot_comparison(combined_df, 'items_per_second', '吞吐量 (Tasks / Second)', '优化前后吞吐量对比', output_dir)
        plot_comparison(combined_df, 'real_time', '执行时间 (ms)', '优化前后执行时间对比', output_dir)
    else:
        # 其他类型文件的通用绘图
        plot_comparison(combined_df, 'items_per_second', '吞吐量 (Tasks / Second)', '吞吐量-线程数关系图', output_dir)


def main():
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <path_to_benchmark1.json> [path_to_benchmark2.json ...]")
        sys.exit(1)
        
    filepaths = sys.argv[1:]
    
    try:
        analyze_files(filepaths)
    except Exception as e:
        print(f"分析过程中出现严重错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 