#include "benchmark_perf.h"
#include "utils.h"
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>

namespace aio_bench {

PerformanceBenchmark::PerformanceBenchmark(const Config& config) 
    : config_(config) {
    configure_bench();
}

void PerformanceBenchmark::configure_bench() {
    bench_.title("AIO基准测试工具 - 性能分析")
          .unit("ns")
          .warmup(100)
          .epochs(1000)
          .minEpochIterations(100);
}

void PerformanceBenchmark::benchmark_io_latency() {
    std::cout << "\n=== IO操作延迟基准测试 ===" << std::endl;
    
    // 模拟IO延迟计算
    bench_.run("IO延迟计算", [&] {
        auto start = std::chrono::steady_clock::now();
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        ankerl::nanobench::doNotOptimizeAway(duration.count());
    });
    
    // 模拟延迟统计
    std::vector<uint64_t> latencies;
    for (int i = 0; i < 1000; i++) {
        latencies.push_back(i * 10 + rand() % 50);
    }
    
    bench_.run("延迟统计计算", [&] {
        std::sort(latencies.begin(), latencies.end());
        size_t p95_idx = static_cast<size_t>(0.95 * (latencies.size() - 1));
        uint64_t p95 = latencies[p95_idx];
        ankerl::nanobench::doNotOptimizeAway(p95);
    });
}

void PerformanceBenchmark::benchmark_memory_allocation() {
    std::cout << "\n=== 内存分配基准测试 ===" << std::endl;
    
    // 测试对齐内存分配
    bench_.run("对齐内存分配", [&] {
        void* ptr = Utils::aligned_alloc(config_.block_size, 4096);
        ankerl::nanobench::doNotOptimizeAway(ptr);
        Utils::aligned_free(ptr);
    });
    
    // 测试标准内存分配对比
    bench_.run("标准内存分配", [&] {
        void* ptr = malloc(config_.block_size);
        ankerl::nanobench::doNotOptimizeAway(ptr);
        free(ptr);
    });
}

void PerformanceBenchmark::benchmark_random_generation() {
    std::cout << "\n=== 随机数生成基准测试 ===" << std::endl;
    
    static thread_local std::mt19937 rng(std::random_device{}());
    static thread_local std::uniform_int_distribution<uint64_t> dist(0, 1000000);
    
    bench_.run("MT19937随机数生成", [&] {
        uint64_t random_val = dist(rng);
        ankerl::nanobench::doNotOptimizeAway(random_val);
    });
    
    // 简单线性同余生成器对比
    static uint64_t seed = 12345;
    bench_.run("简单LCG随机数", [&] {
        seed = seed * 1103515245 + 12345;
        uint64_t random_val = seed % 1000000;
        ankerl::nanobench::doNotOptimizeAway(random_val);
    });
}

void PerformanceBenchmark::benchmark_stats_calculation() {
    std::cout << "\n=== 统计计算基准测试 ===" << std::endl;
    
    // 模拟统计数据
    std::atomic<uint64_t> operations{1000};
    std::atomic<uint64_t> bytes{4096000};
    double elapsed_seconds = 1.0;
    
    bench_.run("IOPS计算", [&] {
        double iops = static_cast<double>(operations.load()) / elapsed_seconds;
        ankerl::nanobench::doNotOptimizeAway(iops);
    });
    
    bench_.run("带宽计算", [&] {
        double bandwidth = (static_cast<double>(bytes.load()) / (1024.0 * 1024.0)) / elapsed_seconds;
        ankerl::nanobench::doNotOptimizeAway(bandwidth);
    });
    
    // 延迟数组处理
    std::vector<uint64_t> latencies(10000);
    std::iota(latencies.begin(), latencies.end(), 100);
    
    bench_.run("延迟平均值计算", [&] {
        uint64_t sum = 0;
        for (uint64_t lat : latencies) {
            sum += lat;
        }
        double avg = static_cast<double>(sum) / latencies.size();
        ankerl::nanobench::doNotOptimizeAway(avg);
    });
}

void PerformanceBenchmark::run_all_benchmarks() {
    std::cout << "开始运行性能基准测试..." << std::endl;
    
    benchmark_memory_allocation();
    benchmark_random_generation();
    benchmark_stats_calculation();
    benchmark_io_latency();
    
    std::cout << "\n性能基准测试完成！" << std::endl;
}

// RuntimeProfiler 实现
RuntimeProfiler::RuntimeProfiler() {
    bench_.title("运行时性能分析")
          .unit("μs")
          .warmup(10)
          .epochs(100);
}

void RuntimeProfiler::start_section(const std::string& name) {
    current_section_ = name;
}

void RuntimeProfiler::end_section() {
    current_section_.clear();
}

void RuntimeProfiler::print_summary() {
    std::cout << "\n=== 运行时性能分析总结 ===" << std::endl;
    // nanobench会自动输出结果
}

} // namespace aio_bench 