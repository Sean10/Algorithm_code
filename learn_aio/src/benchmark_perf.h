#pragma once

#include <string>
#include <functional>
#include <chrono>
#include <memory>

#include <nanobench.h>
#include "config.h"
#include "stats.h"
#include <cstdint>

namespace aio_bench {

class PerformanceBenchmark {
private:
    const Config& config_;
    ankerl::nanobench::Bench bench_;
    
public:
    explicit PerformanceBenchmark(const Config& config);
    
    // 基准测试单个IO操作的延迟
    void benchmark_io_latency();
    
    // 基准测试内存分配性能
    void benchmark_memory_allocation();
    
    // 基准测试随机数生成性能
    void benchmark_random_generation();
    
    // 基准测试统计计算性能
    void benchmark_stats_calculation();
    
    // 运行所有性能基准测试
    void run_all_benchmarks();
    
    // 设置基准测试配置
    void configure_bench();
};

// 性能监控宏，用于测量代码段的执行时间
#define PERF_MEASURE(name, code) \
    do { \
        ankerl::nanobench::Bench().run(name, [&] { \
            code; \
        }); \
    } while(0)

// 性能监控类，用于运行时性能分析
class RuntimeProfiler {
private:
    struct ProfileData {
        std::vector<uint64_t> io_latencies;
        std::vector<size_t> io_sizes;
        std::vector<uint64_t> memory_alloc_times;
        std::vector<size_t> memory_alloc_sizes;
        std::chrono::steady_clock::time_point start_time;
        std::chrono::steady_clock::time_point end_time;
        uint64_t total_ios;
        uint64_t total_bytes;
    };
    
    ProfileData data_;
    bool profiling_active_;
    
public:
    RuntimeProfiler();
    ~RuntimeProfiler();
    
    void start_profiling();
    void stop_profiling();
    void print_results();
    
    // 记录IO操作
    void record_io_operation(uint64_t latency_ns, size_t bytes);
    
    // 记录内存分配
    void record_memory_allocation(size_t bytes, uint64_t duration_ns);
    
    // 获取当前性能数据
    bool is_profiling() const { return profiling_active_; }
};

} // namespace aio_bench 