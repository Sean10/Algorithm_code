# macOS (Darwin) 指标映射文档

## 问题说明

Grafana Node Exporter Dashboard 1860 是为 Linux 系统设计的，使用了 Linux 特定的指标名称。
macOS (Darwin) 的 node_exporter 输出不同的指标名称，导致 dashboard 无法正确显示数据。

## 内存指标映射

| Linux 指标 | macOS 指标 | 说明 |
|------------|------------|------|
| `node_memory_MemTotal_bytes` | `node_memory_total_bytes` | 总内存 |
| `node_memory_MemFree_bytes` | `node_memory_free_bytes` | 空闲内存 |
| `node_memory_Active_bytes` | `node_memory_active_bytes` | 活跃内存 |
| `node_memory_Inactive_bytes` | `node_memory_inactive_bytes` | 非活跃内存 |
| `node_memory_Cached_bytes` | `node_memory_internal_bytes` | 缓存/内部内存 |
| `node_memory_Buffers_bytes` | _无_ | macOS 无此概念 |
| `node_memory_Slab_bytes` | _无_ | macOS 无此概念 |
| `node_memory_PageTables_bytes` | _无_ | macOS 无此概念 |
| `node_memory_SwapTotal_bytes` | `node_memory_swap_total_bytes` | Swap 总量 |
| `node_memory_SwapFree_bytes` | `node_memory_swap_total_bytes - node_memory_swap_used_bytes` | Swap 空闲 |
| `node_memory_MemAvailable_bytes` | _计算_ | `(total - active - wired)` |
| `node_memory_SReclaimable_bytes` | _无_ | macOS 无此概念 |
| `node_memory_Mapped_bytes` | `node_memory_purgeable_bytes` | 可清除内存 |
| `node_memory_Writeback_bytes` | _无_ | macOS 无此概念 |
| `node_memory_Dirty_bytes` | _无_ | macOS 无此概念 |

## macOS 特有指标

```
node_memory_compressed_bytes        # 压缩内存 (macOS 特有)
node_memory_purgeable_bytes         # 可清除内存 (macOS 特有)
node_memory_wired_bytes             # 有线内存 (macOS 特有)
node_memory_swap_used_bytes         # 已用 Swap (macOS 特有)
node_memory_swapped_in_bytes_total  # Swap 入总量
node_memory_swapped_out_bytes_total # Swap 出总量
```

## 内存计算等式

### Linux
```promql
# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 已用内存
node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Cached_bytes - node_memory_Buffers_bytes
```

### macOS
```promql
# 内存使用率 (近似)
(1 - ((node_memory_total_bytes - node_memory_active_bytes - node_memory_wired_bytes) / node_memory_total_bytes)) * 100

# 或简单计算
(node_memory_active_bytes + node_memory_wired_bytes) / node_memory_total_bytes * 100

# 已用内存
node_memory_active_bytes + node_memory_wired_bytes + node_memory_compressed_bytes
```

## 磁盘 I/O 指标差异

Linux node_exporter 提供:
```
node_disk_io_time_seconds_total
node_disk_io_time_weighted_seconds_total
node_disk_read_bytes_total
node_disk_written_bytes_total
node_disk_reads_completed_total
node_disk_writes_completed_total
```

macOS node_exporter 提供:
```
node_disk_read_bytes_total
node_disk_write_time_seconds_total
node_disk_read_time_seconds_total
node_disk_reads_completed_total
node_disk_writes_completed_total
# 缺少：node_disk_io_time_seconds_total
```

## 文件系统指标

文件系统指标在 macOS 和 Linux 上基本相同:
```
node_filesystem_avail_bytes
node_filesystem_free_bytes
node_filesystem_size_bytes
node_filesystem_files
node_filesystem_files_free
```

## 网络指标

网络指标在 macOS 和 Linux 上基本相同:
```
node_network_receive_bytes_total
node_network_transmit_bytes_total
node_network_receive_packets_total
node_network_transmit_packets_total
node_network_receive_drop_total
node_network_transmit_drop_total
node_network_receive_errs_total
node_network_transmit_errs_total
```

## CPU 指标

CPU 指标在 macOS 和 Linux 上基本相同:
```
node_cpu_seconds_total{mode="idle"}
node_cpu_seconds_total{mode="user"}
node_cpu_seconds_total{mode="system"}
node_cpu_seconds_total{mode="nice"}
```

注意：macOS 可能没有 `iowait`, `irq`, `softirq`, `steal` 等模式。

## 负载指标

负载指标有所不同:
- Linux: `node_load1`, `node_load5`, `node_load15`
- macOS: `node_load1`, `node_load5`, `node_load15` (但计算方式不同)

## Grafana Dashboard 修改建议

### 内存面板修改

原 Linux 查询:
```promql
node_memory_MemTotal_bytes{instance="$node",job="$job"}
```

macOS 查询:
```promql
node_memory_total_bytes{instance="$node",job="$job"}
```

### 内存使用率面板修改

原 Linux 查询:
```promql
clamp_min((1 - (node_memory_MemAvailable_bytes{instance="$node", job="$job"} / node_memory_MemTotal_bytes{instance="$node", job="$job"})) * 100, 0)
```

macOS 查询:
```promql
clamp_min((1 - ((node_memory_total_bytes - node_memory_active_bytes - node_memory_wired_bytes) / node_memory_total_bytes)) * 100, 0)
```

### Swap 使用率面板修改

原 Linux 查询:
```promql
((node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes) / node_memory_SwapTotal_bytes) * 100
```

macOS 查询:
```promql
(node_memory_swap_used_bytes / node_memory_swap_total_bytes) * 100
```

## 参考资料

- [node_exporter issue #723](https://github.com/prometheus/node_exporter/issues/723)
- [node_exporter Darwin collector](https://github.com/prometheus/node_exporter/blob/master/collector/meminfo_darwin.go)
- [node_exporter textfile collector](https://github.com/prometheus/node_exporter#textfile-collector)
