# Golang OpenTelemetry 示例

这个项目演示了如何在Golang中使用OpenTelemetry进行指标收集和zap进行日志记录。

## 功能特性

- ✅ 使用OpenTelemetry收集指标（计数器和直方图）
- ✅ 使用zap进行结构化日志记录
- ✅ 生成1000条hello world日志记录
- ✅ 便捷的日志API，避免了OpenTelemetry原生日志的复杂body构造

## 项目结构


```
golang/
├── go.mod          # Go模块依赖
├── main.go         # 主程序文件
└── README.md       # 说明文档
```

## 依赖包

- `go.opentelemetry.io/otel` - OpenTelemetry核心库
- `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc` - OTLP指标导出器
- `go.opentelemetry.io/otel/metric` - 指标API
- `go.opentelemetry.io/otel/sdk/metric` - 指标SDK
- `go.uber.org/zap` - 高性能结构化日志库

## 运行程序

1. 安装依赖：
```bash
go mod tidy
```

2. 编译程序：
```bash
go build -o main .
```

3. 运行程序：
```bash
OTEL_SERVICE_NAME=my-golang-application OTEL_SERVICE_VERSION=1.0.0 OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf ./main
```

## 程序说明

### 指标收集

程序创建了两个指标：
- `app.requests.count` - 请求计数器
- `app.response.time` - 响应时间直方图

### 日志记录

使用zap进行结构化日志记录，每条日志包含：
- `request_id` - 请求ID
- `processing_time_ms` - 处理时间（毫秒）
- `message` - hello world消息

### 与Python版本的对比

相比Python版本，Golang版本：
- 使用zap替代了复杂的OpenTelemetry日志bridge
- 保持了便捷的日志记录API
- 指标功能完全一致
- 性能更优，类型安全

## 配置说明

程序默认配置：
- OpenTelemetry Collector地址：`http://localhost:4317`
- 指标导出间隔：5秒
- 日志级别：INFO
- 服务名称：`my-golang-application`

如需修改配置，请编辑`main.go`文件中的相应参数。

## 注意事项

- 如果没有运行OpenTelemetry Collector，程序会显示连接错误，但不影响程序正常运行
- 日志会输出到标准输出，可以重定向到文件
- 指标数据会尝试发送到OTLP端点，需要配合Collector使用
