#!/usr/bin/env python3
"""
将 Linux Node Exporter Dashboard 转换为 macOS (Darwin) 兼容版本
"""

import json
import re
import sys

def replace_metric(expr, linux_metric, darwin_metric):
    """替换指标，正确处理 label 部分"""
    # 使用更精确的正则表达式
    # 模式 1: 指标名{label} - 保留 label
    pattern1 = rf'{re.escape(linux_metric)}(\{{[^}}]*\}})'
    if darwin_metric == '0':
        replacement1 = '0'
    else:
        replacement1 = f'{darwin_metric}\\1'
    result = re.sub(pattern1, replacement1, expr)

    # 模式 2: 指标名后面没有 label (且不是 label 的一部分)
    pattern2 = rf'{re.escape(linux_metric)}(?!\{{)'
    if darwin_metric == '0':
        replacement2 = '0'
    else:
        replacement2 = darwin_metric
    result = re.sub(pattern2, replacement2, result)

    return result

def replace_memory_metrics(expr):
    """替换内存指标"""
    result = expr

    # 首先处理 MemAvailable 的特殊计算
    def replace_memavailable(match):
        label = match.group(1) if match.group(1) else ''
        return f'(node_memory_total_bytes{label} - node_memory_active_bytes{label} - node_memory_wired_bytes{label})'

    result = re.sub(r'node_memory_MemAvailable_bytes(\{[^}]*\})?', replace_memavailable, result)

    # 处理 SwapTotal
    result = replace_metric(result, 'node_memory_SwapTotal_bytes', 'node_memory_swap_total_bytes')

    # 处理 SwapFree: Linux 的 SwapFree = macOS 的 (swap_total - swap_used)
    def replace_swapfree(match):
        label = match.group(1) if match.group(1) else ''
        return f'(node_memory_swap_total_bytes{label} - node_memory_swap_used_bytes{label})'

    result = re.sub(r'node_memory_SwapFree_bytes(\{[^}]*\})?', replace_swapfree, result)

    # 基本内存指标映射
    mappings = [
        ('node_memory_MemTotal_bytes', 'node_memory_total_bytes'),
        ('node_memory_MemFree_bytes', 'node_memory_free_bytes'),
        ('node_memory_Active_bytes', 'node_memory_active_bytes'),
        ('node_memory_Inactive_bytes', 'node_memory_inactive_bytes'),
        ('node_memory_Cached_bytes', 'node_memory_internal_bytes'),
        ('node_memory_SwapCached_bytes', '0'),
        ('node_memory_Buffers_bytes', '0'),
        ('node_memory_Slab_bytes', '0'),
        ('node_memory_PageTables_bytes', '0'),
        ('node_memory_SReclaimable_bytes', '0'),
        ('node_memory_SUnreclaim_bytes', '0'),
        ('node_memory_KernelStack_bytes', '0'),
        ('node_memory_Percpu_bytes', '0'),
        ('node_memory_Dirty_bytes', '0'),
        ('node_memory_Writeback_bytes', '0'),
        ('node_memory_WritebackTmp_bytes', '0'),
        ('node_memory_NFS_Unstable_bytes', '0'),
        ('node_memory_Mapped_bytes', 'node_memory_purgeable_bytes'),
        ('node_memory_Shmem_bytes', '0'),
        ('node_memory_ShmemHugePages_bytes', '0'),
        ('node_memory_ShmemPmdMapped_bytes', '0'),
        ('node_memory_AnonHugePages_bytes', '0'),
        ('node_memory_AnonPages_bytes', '0'),
        ('node_memory_Unevictable_bytes', '0'),
        ('node_memory_Mlocked_bytes', '0'),
        ('node_memory_HardwareCorrupted_bytes', '0'),
        ('node_memory_Committed_AS_bytes', '0'),
        ('node_memory_CommitLimit_bytes', '0'),
        ('node_memory_Bounce_bytes', '0'),
        ('node_memory_VmallocChunk_bytes', '0'),
        ('node_memory_VmallocTotal_bytes', '0'),
        ('node_memory_VmallocUsed_bytes', '0'),
        ('node_memory_DirectMap1G_bytes', '0'),
        ('node_memory_DirectMap2M_bytes', '0'),
        ('node_memory_DirectMap4k_bytes', '0'),
        ('node_memory_HugePages_Free', '0'),
        ('node_memory_HugePages_Rsvd', '0'),
        ('node_memory_HugePages_Surp', '0'),
        ('node_memory_HugePages_Total', '0'),
        ('node_memory_Hugepagesize_bytes', '0'),
        ('node_memory_Inactive_file_bytes', '0'),
        ('node_memory_Inactive_anon_bytes', '0'),
        ('node_memory_Active_file_bytes', '0'),
        ('node_memory_Active_anon_bytes', 'node_memory_active_bytes'),
    ]

    for linux_metric, darwin_metric in mappings:
        result = replace_metric(result, linux_metric, darwin_metric)

    return result

def replace_disk_metrics(expr):
    """替换磁盘指标"""
    result = expr

    # node_disk_io_time_seconds_total 在 macOS 不存在，用 read+write time 替代
    def replace_io_time(match):
        label = match.group(1) if match.group(1) else ''
        return f'(node_disk_read_time_seconds_total{label} + node_disk_write_time_seconds_total{label})'

    result = re.sub(r'node_disk_io_time_seconds_total(\{[^}]*\})?', replace_io_time, result)
    result = re.sub(r'node_disk_io_time_weighted_seconds_total(\{[^}]*\})?', replace_io_time, result)

    # macOS 不存在的磁盘指标设为 0
    disk_metrics_to_zero = [
        'node_disk_reads_merged_total',
        'node_disk_writes_merged_total',
        'node_disk_discards_completed_total',
        'node_disk_discards_merged_total',
        'node_disk_discarded_sectors_total',
        'node_disk_discard_time_seconds_total',
        'node_disk_flush_requests_total',
        'node_disk_flush_requests_time_seconds_total',
        'node_disk_io_now',
    ]

    for metric in disk_metrics_to_zero:
        result = replace_metric(result, metric, '0')

    return result

def fix_duplicate_labels(expr):
    """修复重复的 label"""
    # 匹配如 {label}{label} 的模式
    expr = re.sub(r'(\{[^}]*\})(\{[^}]*\})+', r'\1', expr)
    return expr

def simplify_expression(expr):
    """简化表达式"""
    # 移除 + 0 和 - 0
    expr = re.sub(r'\s*\+\s*0\b', '', expr)
    expr = re.sub(r'\b0\s*\+\s*', '', expr)
    expr = re.sub(r'\s*-\s*0\b', '', expr)

    # 简化 (A - (A - B)) 为 B
    # 匹配 SwapTotal - (SwapTotal - SwapUsed) 模式
    expr = re.sub(
        r'\(node_memory_swap_total_bytes\{([^}]*)\}\s*-\s*\(node_memory_swap_total_bytes\{\1\}\s*-\s*node_memory_swap_used_bytes\{\1\}\)\)',
        r'node_memory_swap_used_bytes{\1}',
        expr
    )

    return expr

def process_panel(panel):
    """处理单个 panel"""
    if 'targets' in panel:
        for target in panel['targets']:
            if 'expr' in target:
                expr = target['expr']
                # 替换内存指标
                expr = replace_memory_metrics(expr)
                # 替换磁盘指标
                expr = replace_disk_metrics(expr)
                # 修复重复 label
                expr = fix_duplicate_labels(expr)
                # 简化表达式
                expr = simplify_expression(expr)
                target['expr'] = expr

    # 递归处理子面板
    if 'panels' in panel:
        for child in panel['panels']:
            process_panel(child)

def convert_dashboard(input_file, output_file):
    """转换 dashboard 文件"""
    with open(input_file, 'r') as f:
        dashboard = json.load(f)

    # 修改标题
    dashboard['title'] = 'Node Exporter for macOS'
    dashboard['description'] = 'Prometheus Node Exporter Dashboard for macOS (Darwin) - Modified from Grafana 1860'

    # 处理所有面板
    if 'panels' in dashboard:
        for panel in dashboard['panels']:
            process_panel(panel)

    # 保存新文件
    with open(output_file, 'w') as f:
        json.dump(dashboard, f, indent=2)

    print(f"转换完成：{output_file}")

if __name__ == '__main__':
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = 'node-exporter-basic.json'
        output_file = 'node-exporter-macos.json'

    convert_dashboard(input_file, output_file)
