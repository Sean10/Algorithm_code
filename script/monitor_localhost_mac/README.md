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

- 地址: http://localhost:3000
- 账号: `admin` / `admin`

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

## 目录结构

```
monitor_localhost_mac/
├── docker-compose.yml
├── prometheus/prometheus.yml
└── grafana/provisioning/
    ├── datasources/prometheus.yml
    └── dashboards/node-exporter-basic.json
```