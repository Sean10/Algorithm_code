import time
import logging
from opentelemetry import metrics
from opentelemetry._logs import set_logger_provider, get_logger
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LogRecordProcessor
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry._logs import LogRecord, SeverityNumber

# 配置服务资源信息（将在日志和指标中共享）
resource = Resource(attributes={
    SERVICE_NAME: "my-application"  # 服务名称，用于标识你的应用
})

# ---------------------------
# 配置Metrics
# ---------------------------
# 创建OTLP指标导出器，指向你的OpenTelemetry服务
metric_exporter = OTLPMetricExporter(
    endpoint="http://localhost:4317",  # OpenTelemetry Collector的地址
    insecure=True
)

# 创建指标读取器，定期导出指标
metric_reader = PeriodicExportingMetricReader(
    metric_exporter,
    export_interval_millis=5000  # 每5秒导出一次指标
)

# 配置指标提供者
metric_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
)

# 设置全局指标提供者
metrics.set_meter_provider(metric_provider)

# 获取meter实例
meter = metrics.get_meter(
    name="myapp.metrics",
    version="1.0.0"
)

# 创建一个计数器指标
request_counter = meter.create_counter(
    name="app.requests.count",
    description="Total number of requests received",
    unit="1"
)

# 创建一个直方图指标
response_time_histogram = meter.create_histogram(
    name="app.response.time",
    description="Response time in milliseconds",
    unit="ms"
)

# ---------------------------
# 配置Logs
# ---------------------------
# 创建OTLP日志导出器
log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4317",  # 与指标使用相同的OpenTelemetry服务
    insecure=True
)

# 配置日志处理器
log_processor = BatchLogRecordProcessor(log_exporter)

# 配置日志提供者
log_provider = LoggerProvider(
    resource=resource,
)
log_provider.add_log_record_processor(log_processor)

# 设置全局日志提供者
set_logger_provider(log_provider)

# 获取logger实例
logger = get_logger("myapp.logger")

# 将Python标准日志与OpenTelemetry集成
class OTelLogHandler(logging.Handler):
    def emit(self, record):
        # 映射日志级别到 OpenTelemetry SeverityNumber
        severity_mapping = {
            logging.DEBUG: SeverityNumber.DEBUG,
            logging.INFO: SeverityNumber.INFO,
            logging.WARNING: SeverityNumber.WARN,
            logging.ERROR: SeverityNumber.ERROR,
            logging.CRITICAL: SeverityNumber.FATAL,
        }
        
        log_record = LogRecord(
            timestamp=int(record.created * 1e9),  # 转换为纳秒（整数）
            body=record.getMessage(),
            severity_text=record.levelname,
            severity_number=severity_mapping.get(record.levelno, SeverityNumber.INFO),
            attributes={"logger": record.name},
        )
        logger.emit(log_record)

# 配置标准日志系统
logging.basicConfig(level=logging.INFO)
logging.getLogger().addHandler(OTelLogHandler())

# ---------------------------
# 应用示例代码
# ---------------------------
def handle_request(i: int):
    # 记录请求开始
    logging.info("Handling new request")
    
    # 增加请求计数
    request_counter.add(1, attributes={"endpoint": "/api/test"})
    
    # 模拟处理时间
    start_time = time.time()
    # time.sleep(0.1)  # 模拟处理耗时
    processing_time = (time.time() - start_time) * 1000  # 转换为毫秒
    
    # 记录响应时间
    response_time_histogram.record(
        processing_time,
        attributes={"endpoint": "/api/test", "status": "success"}
    )
    
    # 记录请求完成
    logging.info(f"Request processed in {processing_time:.2f}ms, helloi world {i}")

if __name__ == "__main__":
    print("Starting application with OpenTelemetry logs and metrics...")
    try:
        # 模拟处理一些请求
        for i in range(1000):
            handle_request(i)
            # time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # 确保资源被正确释放
        metric_provider.shutdown()
        log_provider.shutdown()
