# OpenTelemetry 学习项目

基于 OpenTelemetry 的可观测性学习项目，实现了完整的指标和日志监控链路。

今天在折腾公司对接全链路监控, 想用来观测自己app的吞吐性能.

结果始终没能顺利跑通demo程序, 不知道究竟是公司服务端还没完全兼容还是别的什么原因, 所以姑且来看看阿里云的
产品对接上是什么样子.

## 🏗️ 架构概述

```
Python 应用 → Grafana Alloy → Prometheus/Loki → Grafana
```

- **Python 应用**: 使用 OpenTelemetry SDK 发送指标和日志
- **Grafana Alloy**: 接收 OTLP 数据并转发到存储系统
- **Prometheus**: 存储和查询指标数据
- **Loki**: 存储和查询日志数据  
- **Grafana**: 统一的可视化和查询界面

## 📁 项目结构

```
learn_opentelemetry/
├── config/                    # 配置文件目录
│   ├── alloy.alloy           # Grafana Alloy 配置
│   ├── loki.yaml             # Loki 配置
│   └── prometheus.yml        # Prometheus 配置
├── python/                   # Python 示例应用
│   ├── main.py              # 主应用程序
│   ├── pyproject.toml       # 项目依赖配置
│   └── README.md            # Python 应用说明
├── docker-compose.yml       # Docker Compose 配置
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 1. 启动监控基础设施

```bash
# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps
```

### 2. 运行 Python 示例应用

```bash
cd python
uv run main.py
```

### 3. 访问监控界面

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alloy UI**: http://localhost:12345

## 📊 在 Grafana 中查看数据

### 配置数据源

1. **添加 Prometheus 数据源**:
   - URL: `http://prometheus:9090`
   - 用于查看指标数据

2. **添加 Loki 数据源**:
   - URL: `http://loki:3100`
   - 用于查看日志数据

### 示例查询

#### 指标查询 (Prometheus)
```promql
# 请求计数
otel_request_count_total

# 响应时间分布
otel_response_time_histogram_bucket
```

#### 日志查询 (Loki)
```logql
# 查看所有应用日志
{service="my-application"}

# 按日志级别过滤
{service="my-application"} |= "INFO"

# 查看请求处理日志
{service="my-application"} |= "Request processed"
```

## 🔧 配置说明

### Alloy 配置 (`config/alloy.alloy`)
- 接收 OTLP 数据 (gRPC: 4317, HTTP: 4318)
- 将指标转发到 Prometheus
- 将日志转发到 Loki

### Loki 配置 (`config/loki.yaml`)
- 配置存储后端为本地文件系统
- 启用日志接收和查询功能

### Prometheus 配置 (`config/prometheus.yml`)
- 配置抓取 Alloy 暴露的指标
- 启用远程写入接收器

## 🐛 故障排除

### 检查服务状态
```bash
# 查看所有容器状态
docker compose ps

# 查看特定服务日志
docker compose logs alloy
docker compose logs loki
docker compose logs prometheus
```

### 验证数据流
```bash
# 检查 Loki 中的标签
curl -s "http://localhost:3100/loki/api/v1/labels"

# 检查 Prometheus 指标
curl -s "http://localhost:8889/metrics"
```

### 常见问题

1. **日志不显示**: 确保 Loki 服务正常运行，检查 Alloy 配置
2. **指标不显示**: 检查 Prometheus 配置和 Alloy 指标导出
3. **连接问题**: 确保所有服务在同一 Docker 网络中

## 📚 学习资源

- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
- [Grafana Alloy 文档](https://grafana.com/docs/alloy/)
- [Loki 文档](https://grafana.com/docs/loki/)
- [Prometheus 文档](https://prometheus.io/docs/)

## 🎯 下一步

- [ ] 添加分布式追踪 (Traces)
- [ ] 集成 Pyroscope 性能分析
- [ ] 添加告警规则
- [ ] 创建 Grafana 仪表板模板