#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"

using namespace tp_bench;

// 对比测试配置
static BenchmarkConfig create_comparison_config(ThreadPoolType type, size_t threads) {
    BenchmarkConfig config;
    config.pool_type = type;
    config.thread_count = threads;
    config.task_count = 10000;
    config.task_type = TaskType::CPU_INTENSIVE;
    config.cpu_work_size = 20000;
    config.enable_memory_profiling = false;
    return config;
}

// 针对不同线程池实现的通用Benchmark函数
static void BM_ThreadPool_Comparison(benchmark::State& state, ThreadPoolType type) {
    const size_t thread_count = state.range(0);
    
    auto config = create_comparison_config(type, thread_count);
    BenchmarkExecutor executor(config);
    
    for (auto _ : state) {
        auto metrics = executor.run_benchmark();
        
        state.counters["threads"] = thread_count;
        state.counters["throughput"] = benchmark::Counter(
            metrics.throughput_tasks_per_sec, benchmark::Counter::kIsRate);
        state.counters["avg_latency_us"] = benchmark::Counter(
            metrics.avg_task_time.count() / 1000.0);
        state.counters["memory_peak_mb"] = benchmark::Counter(
            metrics.memory_peak_kb / 1024.0);
    }
}

// 我们的线程池实现
static void BM_CustomThreadPool(benchmark::State& state) {
    BM_ThreadPool_Comparison(state, ThreadPoolType::TP_CUSTOM_OPTIMIZED);
}

// std::async实现
static void BM_StdAsync(benchmark::State& state) {
    BM_ThreadPool_Comparison(state, ThreadPoolType::TP_STD_ASYNC);
}

// 注册Benchmarks
BENCHMARK(BM_CustomThreadPool)
    ->DenseRange(1, 16, 1) // 1到16个线程
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime();

BENCHMARK(BM_StdAsync)
    ->DenseRange(1, 16, 1)
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime();

//
// 在这里可以添加其他线程池实现的Benchmark
// 例如：TBB, OpenMP等
//
// static void BM_TBBThreadPool(benchmark::State& state) {
//     BM_ThreadPool_Comparison(state, ThreadPoolType::TP_TBB);
// }
// BENCHMARK(BM_TBBThreadPool)->DenseRange(1, 16, 1);
//
