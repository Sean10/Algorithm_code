#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"

using namespace tp_bench;

// CPU密集型任务配置
static BenchmarkConfig create_cpu_config(size_t threads, size_t work_size) {
    BenchmarkConfig config;
    config.thread_count = threads;
    config.task_count = 1000;
    config.task_type = TaskType::CPU_INTENSIVE;
    config.cpu_work_size = work_size;
    config.enable_memory_profiling = false;
    config.pool_type = ThreadPoolType::TP_CUSTOM_OPTIMIZED;
    return config;
}

// CPU密集型 - 轻量级工作负载
THREAD_POOL_BENCHMARK(CPU_Light_1Thread, create_cpu_config(1, 1000));
THREAD_POOL_BENCHMARK(CPU_Light_2Thread, create_cpu_config(2, 1000));
THREAD_POOL_BENCHMARK(CPU_Light_4Thread, create_cpu_config(4, 1000));
THREAD_POOL_BENCHMARK(CPU_Light_8Thread, create_cpu_config(8, 1000));

// CPU密集型 - 中等工作负载
THREAD_POOL_BENCHMARK(CPU_Medium_1Thread, create_cpu_config(1, 10000));
THREAD_POOL_BENCHMARK(CPU_Medium_2Thread, create_cpu_config(2, 10000));
THREAD_POOL_BENCHMARK(CPU_Medium_4Thread, create_cpu_config(4, 10000));
THREAD_POOL_BENCHMARK(CPU_Medium_8Thread, create_cpu_config(8, 10000));

// CPU密集型 - 重量级工作负载
THREAD_POOL_BENCHMARK(CPU_Heavy_1Thread, create_cpu_config(1, 100000));
THREAD_POOL_BENCHMARK(CPU_Heavy_2Thread, create_cpu_config(2, 100000));
THREAD_POOL_BENCHMARK(CPU_Heavy_4Thread, create_cpu_config(4, 100000));
THREAD_POOL_BENCHMARK(CPU_Heavy_8Thread, create_cpu_config(8, 100000));

// 标准的Google Benchmark实现
static void BM_CustomThreadPool_CPU_Scaling(benchmark::State& state) {
    const size_t thread_count = state.range(0);
    const size_t work_size = state.range(1);
    
    auto config = create_cpu_config(thread_count, work_size);
    BenchmarkExecutor executor(config);
    
    for (auto _ : state) {
        auto metrics = executor.run_benchmark();
        
        state.counters["threads"] = thread_count;
        state.counters["work_size"] = work_size;
        state.counters["throughput"] = benchmark::Counter(
            metrics.throughput_tasks_per_sec, benchmark::Counter::kIsRate);
        state.counters["avg_latency_us"] = benchmark::Counter(
            metrics.avg_task_time.count() / 1000.0);
        state.counters["memory_peak_mb"] = benchmark::Counter(
            metrics.memory_peak_kb / 1024.0);
        state.counters["efficiency"] = benchmark::Counter(
            metrics.throughput_tasks_per_sec / thread_count);
    }
}

// 定义测试范围：线程数 × 工作负载大小
BENCHMARK(BM_CustomThreadPool_CPU_Scaling)
    ->Args({1, 1000})->Args({1, 10000})->Args({1, 100000})
    ->Args({2, 1000})->Args({2, 10000})->Args({2, 100000})
    ->Args({4, 1000})->Args({4, 10000})->Args({4, 100000})
    ->Args({8, 1000})->Args({8, 10000})->Args({8, 100000})
    ->Args({16, 1000})->Args({16, 10000})->Args({16, 100000})
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime(); 