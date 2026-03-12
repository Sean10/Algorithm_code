# macOS 本地监控系统

基于 Docker Compose 的本地监控系统，用于监控 macOS 主机的运行状态。

## 重要说明

由于 Docker 在 macOS 上运行在 Linux 虚拟机中，**Node Exporter 必须在宿主机上直接运行**才能采集真实系统指标。

## 快速开始

### 1. 安装并启动 Node Exporter

```bash
brew install node_exporter
brew services start node_exporter
```

### 2. 启动 Docker 服务

```bash
docker-compose up -d
```

### 3. 访问 Grafana

- 地址：http://localhost:3000
- 账号：`admin` / `admin`

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Node Exporter | 9100 | 宿主机运行，brew services 管理 |
| Prometheus | 9090 | Docker 容器 |
| Grafana | 3000 | Docker 容器 |

## 管理命令

```bash
# Node Exporter (宿主机)
brew services start node_exporter    # 启动
brew services stop node_exporter     # 停止
brew services restart node_exporter  # 重启
brew services list                   # 查看状态

# Docker 服务
docker-compose up -d      # 启动
docker-compose stop       # 停止
docker-compose down       # 停止并删除容器
```

## 验证

```bash
# 检查 Node Exporter
curl http://localhost:9100/metrics | head

# 检查 Prometheus 采集状态
curl http://localhost:9090/api/v1/targets | python3 -m json.tool
```

## Dashboard 说明

### macOS 专用 Dashboard

由于 Linux 和 macOS (Darwin) 的 node_exporter 指标名称不同，我们提供了专门针对 macOS 优化的 dashboard：

- **node-exporter-macos.json**: macOS 专用 dashboard，已转换所有指标名称

#### 主要指标差异

| Linux 指标 | macOS 指标 |
|------------|------------|
| `node_memory_MemTotal_bytes` | `node_memory_total_bytes` |
| `node_memory_MemFree_bytes` | `node_memory_free_bytes` |
| `node_memory_Cached_bytes` | `node_memory_internal_bytes` |
| `node_memory_Buffers_bytes` | 无 |
| `node_memory_MemAvailable_bytes` | 计算：`total - active - wired` |

#### 在 Grafana 中导入

1. 登录 Grafana (http://localhost:3000)
2. 进入 Dashboards → Import
3. 上传 `grafana/provisioning/dashboards/node-exporter-macos.json`
4. 选择 Prometheus 数据源

## 目录结构

```
monitor_localhost_mac/
├── docker-compose.yml
├── prometheus/prometheus.yml
├── README.md                       # 使用说明
├── CONVERSION_NOTES.md             # 转换说明和注意事项
├── DARWIN_METRICS_MAPPING.md       # 详细的指标映射文档
├── convert_dashboard_to_macos.py   # Dashboard 转换脚本
└── grafana/provisioning/
    ├── datasources/prometheus.yml
    └── dashboards/
        ├── node-exporter-basic.json   # 原始 Linux dashboard
        └── node-exporter-macos.json   # macOS 转换版
```

## 参考资料

- [DARWIN_METRICS_MAPPING.md](./DARWIN_METRICS_MAPPING.md) - 详细的 macOS 指标映射文档
- [node_exporter issue #723](https://github.com/prometheus/node_exporter/issues/723) - Darwin 指标差异讨论
