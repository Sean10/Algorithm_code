#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"
#include "thread_pool/thread_pool_original.hpp"

using namespace tp_bench;

// 通用的Benchmark函数，可测试任何类型的线程池
static void RunBenchmark(benchmark::State& state, ThreadPoolType type) {
    const size_t thread_count = state.range(0);
    
    BenchmarkConfig config;
    config.pool_type = type;
    config.thread_count = thread_count;
    config.task_count = 20000; // 使用更多的任务来放大差异
    config.task_type = TaskType::CPU_INTENSIVE;
    config.cpu_work_size = 10000;
    config.enable_memory_profiling = false; // 在此测试中我们更关心时间

    BenchmarkExecutor executor(config);
    
    for (auto _ : state) {
        auto metrics = executor.run_benchmark();
        
        state.counters["threads"] = thread_count;
        state.counters["throughput"] = benchmark::Counter(
            metrics.throughput_tasks_per_sec, benchmark::Counter::kIsRate);
        state.counters["avg_latency_us"] = benchmark::Counter(
            metrics.avg_task_time.count() / 1000.0);
    }
}

// --- 注册优化前后的Benchmark ---

// 测试1: 优化前的版本 (单队列)
static void BM_OriginalThreadPool(benchmark::State& state) {
    RunBenchmark(state, ThreadPoolType::TP_CUSTOM_ORIGINAL);
}
BENCHMARK(BM_OriginalThreadPool)
    ->DenseRange(1, std::thread::hardware_concurrency() * 2, 2)
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime();

// 测试2: 优化后的版本 (工作窃取)
static void BM_OptimizedThreadPool(benchmark::State& state) {
    RunBenchmark(state, ThreadPoolType::TP_CUSTOM_OPTIMIZED);
}
BENCHMARK(BM_OptimizedThreadPool)
    ->DenseRange(1, std::thread::hardware_concurrency() * 2, 2)
    ->Unit(benchmark::kMillisecond)
    ->UseRealTime(); 