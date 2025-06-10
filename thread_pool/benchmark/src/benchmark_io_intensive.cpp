#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"

using namespace tp_bench;

// IO密集型任务配置
static BenchmarkConfig create_io_config(size_t threads, size_t delay_ms) {
    BenchmarkConfig config;
    config.thread_count = threads;
    config.task_count = 500;
    config.task_type = TaskType::IO_INTENSIVE;
    config.io_delay_ms = delay_ms;
    config.enable_memory_profiling = false;
    config.pool_type = ThreadPoolType::TP_CUSTOM_OPTIMIZED;
    return config;
}

// IO密集型 - 不同延迟
THREAD_POOL_BENCHMARK(IO_1ms_Delay_4Threads, create_io_config(4, 1));
THREAD_POOL_BENCHMARK(IO_1ms_Delay_8Threads, create_io_config(8, 1));
THREAD_POOL_BENCHMARK(IO_10ms_Delay_8Threads, create_io_config(8, 10));
THREAD_POOL_BENCHMARK(IO_10ms_Delay_16Threads, create_io_config(16, 10));
THREAD_POOL_BENCHMARK(IO_20ms_Delay_16Threads, create_io_config(16, 20));
THREAD_POOL_BENCHMARK(IO_20ms_Delay_32Threads, create_io_config(32, 20));


// 标准的Google Benchmark实现
static void BM_CustomThreadPool_IO_Scaling(benchmark::State& state) {
    const size_t thread_count = state.range(0);
    const size_t delay_ms = state.range(1);
    
    auto config = create_io_config(thread_count, delay_ms);
    BenchmarkExecutor executor(config);
    
    for (auto _ : state) {
        auto metrics = executor.run_benchmark();
        
        state.counters["threads"] = thread_count;
        state.counters["delay_ms"] = delay_ms;
        state.counters["throughput"] = benchmark::Counter(
            metrics.throughput_tasks_per_sec, benchmark::Counter::kIsRate);
        state.counters["avg_latency_us"] = benchmark::Counter(
            metrics.avg_task_time.count() / 1000.0);
        state.counters["memory_peak_mb"] = benchmark::Counter(
            metrics.memory_peak_kb / 1024.0);
    }
}

// 定义测试范围：线程数 × IO延迟
BENCHMARK(BM_CustomThreadPool_IO_Scaling)
    ->Args({4, 1})->Args({8, 1})
    ->Args({8, 5})->Args({16, 5})
    ->Args({16, 10})->Args({32, 10})
    ->Args({32, 20})->Args({64, 20})
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime(); 