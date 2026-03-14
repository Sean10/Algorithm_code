# macOS 本地监控系统

基于 Docker Compose 的本地监控系统，用于监控 macOS 主机的运行状态。支持 Node Exporter 和 MacTop 两种监控源。

## 重要说明

由于 Docker 在 macOS 上运行在 Linux 虚拟机中，**Node Exporter 和 MacTop 必须在宿主机上直接运行**才能采集真实系统指标。

## 快速开始

### 1. 安装并启动监控服务

#### Node Exporter (基础系统指标)
```bash
brew install node_exporter
brew services start node_exporter
```

#### MacTop (Apple Silicon 专用指标) - 推荐
```bash
brew install mactop
brew services start mactop
```

MacTop 提供以下 Apple Silicon 专用指标：
- CPU: P-Core / E-Core 分别监控
- GPU: 使用率、频率、温度、功耗
- 内存：使用量、Swap
- 功耗：CPU/GPU/DRAM/ANE 各组件功耗
- 温度：SoC、GPU 及多个传感器温度
- 磁盘 I/O、网络吞吐量
- 风扇转速、热状态

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
| MacTop | 9101 | 宿主机运行，brew services 管理 |
| Prometheus | 9090 | Docker 容器 |
| Grafana | 3000 | Docker 容器 |

## 管理命令

```bash
# Node Exporter (宿主机)
brew services start node_exporter    # 启动
brew services stop node_exporter     # 停止
brew services restart node_exporter  # 重启
brew services list                   # 查看状态

# MacTop (宿主机)
brew services start mactop           # 启动
brew services stop mactop            # 停止
brew services restart mactop         # 重启

# Docker 服务
docker-compose up -d      # 启动
docker-compose stop       # 停止
docker-compose down       # 停止并删除容器
```

## 验证

```bash
# 检查 Node Exporter
curl http://localhost:9100/metrics | head

# 检查 MacTop
curl http://localhost:9101/metrics | head

# 检查 Prometheus 采集状态
curl http://localhost:9090/api/v1/targets | python3 -m json.tool
```

## Dashboard 说明

### MacTop Dashboard (推荐 - Apple Silicon 专用)

`mactop-macos.json` - 专为 Apple Silicon Mac 设计的 Dashboard，包含：

- **系统概览**: 芯片型号、核心数、功耗、温度、热状态
- **CPU 监控**: 总使用率、P-Core/E-Core 分别监控、每核心使用率
- **GPU 监控**: 使用率、频率、温度、功耗
- **内存监控**: 使用量、使用率、Swap
- **功耗监控**: CPU/GPU/DRAM/ANE 各组件功耗、DRAM 带宽
- **温度监控**: SoC、GPU 及关键传感器温度
- **磁盘 I/O**: IOPS、吞吐量
- **网络监控**: 网络吞吐量、Thunderbolt 网络
- **风扇监控**: 风扇转速

### macOS 专用 Dashboard (Node Exporter)

`node-exporter-macos.json` - macOS 专用 dashboard，已转换所有指标名称

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
3. 上传 `grafana/provisioning/dashboards/mactop-macos.json` (推荐)
4. 选择 Prometheus 数据源

## 目录结构

```
monitor_localhost_mac/
├── docker-compose.yml
├── prometheus/prometheus.yml       # Prometheus 配置 (包含 mactop 抓取)
├── README.md                       # 使用说明
└── grafana/provisioning/
    ├── datasources/prometheus.yml
    └── dashboards/
        ├── node-exporter-basic.json   # 原始 Linux dashboard
        ├── node-exporter-macos.json   # macOS 转换版 (Node Exporter)
        └── mactop-macos.json          # MacTop Dashboard (推荐)
```

## 参考资料

- [MacTop GitHub](https://github.com/metaspartan/mactop) - Apple Silicon 监控工具
- [DARWIN_METRICS_MAPPING.md](./DARWIN_METRICS_MAPPING.md) - 详细的 macOS 指标映射文档
- [node_exporter issue #723](https://github.com/prometheus/node_exporter/issues/723) - Darwin 指标差异讨论
