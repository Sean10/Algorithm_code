package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"time"

	bridge "github.com/keyval-dev/opentelemetry-zap-bridge"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/metric"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
	"go.uber.org/zap"
)

var (
	// 指标实例
	requestCounter    metric.Int64Counter
	responseHistogram metric.Float64Histogram
)

// 初始化OpenTelemetry资源
func initResource() *resource.Resource {
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceName("my-golang-application"),
			semconv.ServiceVersion("1.0.0"),
		),
	)
	if err != nil {
		log.Fatalf("Failed to create resource: %v", err)
	}
	return res
}

// 初始化Metrics
func initMetrics(ctx context.Context, res *resource.Resource) *sdkmetric.MeterProvider {
	// 创建OTLP指标导出器
	metricExporter, err := otlpmetricgrpc.New(ctx,
		otlpmetricgrpc.WithEndpoint("localhost:4317"),
		otlpmetricgrpc.WithInsecure(),
	)
	if err != nil {
		log.Fatalf("Failed to create metric exporter: %v", err)
	}

	// 创建指标提供者
	meterProvider := sdkmetric.NewMeterProvider(
		sdkmetric.WithResource(res),
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(
			metricExporter,
			sdkmetric.WithInterval(5*time.Second), // 每5秒导出一次
		)),
	)

	// 设置全局指标提供者
	otel.SetMeterProvider(meterProvider)

	// 获取meter实例
	meter := meterProvider.Meter(
		"myapp.metrics",
		metric.WithInstrumentationVersion("1.0.0"),
	)

	// 创建计数器指标
	var err1, err2 error
	requestCounter, err1 = meter.Int64Counter(
		"app.requests.count",
		metric.WithDescription("Total number of requests received"),
		metric.WithUnit("1"),
	)

	// 创建直方图指标
	responseHistogram, err2 = meter.Float64Histogram(
		"app.response.time",
		metric.WithDescription("Response time in milliseconds"),
		metric.WithUnit("ms"),
	)

	if err1 != nil || err2 != nil {
		log.Fatalf("Failed to create metrics: %v, %v", err1, err2)
	}

	return meterProvider
}

// 初始化zap日志与OpenTelemetry集成
func initLogs() *zap.Logger {
	// 创建标准的zap logger
	logger, err := zap.NewProduction()
	if err != nil {
		log.Fatalf("Failed to create zap logger: %v", err)
	}

	// 使用odigos bridge附加OpenTelemetry支持
	logger = bridge.AttachToZapLogger(logger)

	// 设置为全局logger
	zap.ReplaceGlobals(logger)

	return logger
}

// 处理请求的函数
func handleRequest(ctx context.Context, i int) {
	// 记录请求开始 - 使用标准zap调用，bridge会自动转换为OpenTelemetry
	zap.L().Info("Handling new request",
		zap.Int("request_id", i),
	)

	// 增加请求计数
	requestCounter.Add(ctx, 1,
		metric.WithAttributes(
			attribute.String("endpoint", "/api/test"),
		),
	)

	// 模拟处理时间
	startTime := time.Now()
	// time.Sleep(100 * time.Millisecond) // 可以取消注释来模拟处理耗时
	processingTime := float64(time.Since(startTime).Nanoseconds()) / 1e6 // 转换为毫秒

	// 记录响应时间
	responseHistogram.Record(ctx, processingTime,
		metric.WithAttributes(
			attribute.String("endpoint", "/api/test"),
			attribute.String("status", "success"),
		),
	)

	// 记录请求完成 - bridge会自动发送到OpenTelemetry
	zap.L().Info("Request processed",
		zap.Int("request_id", i),
		zap.Float64("processing_time_ms", processingTime),
		zap.String("message", fmt.Sprintf("hello world %d", i)),
	)
}

func main() {
	ctx := context.Background()

	// 初始化资源
	res := initResource()

	// 初始化Metrics
	meterProvider := initMetrics(ctx, res)
	defer func() {
		// 创建一个新的context用于shutdown，避免使用可能已经取消的context
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		if err := meterProvider.Shutdown(shutdownCtx); err != nil {
			// 只在非取消错误时打印日志
			if !errors.Is(err, context.Canceled) {
				log.Printf("Error shutting down meter provider: %v", err)
			}
		}
	}()

	// 初始化Logs - 使用odigos bridge集成OpenTelemetry
	logger := initLogs()
	defer func() {
		// 安全地调用Sync，避免panic
		defer func() {
			if r := recover(); r != nil {
				// 捕获并忽略sync时的panic，这在odigos bridge中可能发生
				// log.Printf("Logger sync panic recovered (可以忽略): %v", r)
			}
		}()
		logger.Sync()
	}()

	fmt.Println("Starting Golang application with OpenTelemetry metrics and logs via otelzap...")

	// 模拟处理1000个请求
	for i := 0; i < 1000; i++ {
		handleRequest(ctx, i)
		// time.Sleep(10 * time.Millisecond) // 可以取消注释来添加延迟
	}

	fmt.Println("Completed processing 1000 requests")

	// 等待一段时间确保所有数据都被导出
	fmt.Println("Waiting for telemetry data to be exported...")
	time.Sleep(6 * time.Second) // 稍微超过导出间隔(5秒)
	fmt.Println("Application finished")
}
