#include "../include/benchmark_framework.hpp"
#include <numeric>
#include <algorithm>
#include <vector>

using namespace tp_bench;

// 为MemoryProfiler提供空的实现以解决链接错误
void MemoryProfiler::start_monitoring() {}
void MemoryProfiler::stop_monitoring() {}
PerformanceMetrics MemoryProfiler::get_memory_metrics() const {
    return PerformanceMetrics{};
}

BenchmarkExecutor::BenchmarkExecutor(const BenchmarkConfig& config)
    : config_(config) {
    configure_task_generator();
    configure_thread_pool();
    if (config_.enable_memory_profiling) {
        memory_profiler_ = std::make_unique<MemoryProfiler>();
    }
}

void BenchmarkExecutor::configure_task_generator() {
    task_generator_ = create_task_generator(config_.task_type);
    task_generator_->configure(config_);
}

void BenchmarkExecutor::configure_thread_pool() {
    thread_pool_ = create_thread_pool_adapter(config_.pool_type);
    thread_pool_->initialize(config_.thread_count);
}

PerformanceMetrics BenchmarkExecutor::run_benchmark() {
    if (config_.enable_memory_profiling && memory_profiler_) {
        memory_profiler_->start_monitoring();
    }

    auto metrics = execute_tasks();

    if (config_.enable_memory_profiling && memory_profiler_) {
        memory_profiler_->stop_monitoring();
        auto mem_metrics = memory_profiler_->get_memory_metrics();
        metrics.memory_peak_kb = mem_metrics.memory_peak_kb;
        metrics.memory_avg_kb = mem_metrics.memory_avg_kb;
    }

    return metrics;
}

PerformanceMetrics BenchmarkExecutor::execute_tasks() {
    PerformanceMetrics metrics;
    std::vector<std::future<int>> futures;
    futures.reserve(config_.task_count);
    
    std::vector<std::chrono::nanoseconds> task_latencies;
    if (config_.enable_latency_tracking) {
        task_latencies.reserve(config_.task_count);
    }

    auto start_time = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < config_.task_count; ++i) {
        auto task = task_generator_->generate_task_with_result();
        futures.emplace_back(thread_pool_->submit_task_with_result(std::move(task)));
    }

    for (auto& f : futures) {
        try {
            f.get();
            metrics.successful_tasks++;
        } catch (...) {
            metrics.failed_tasks++;
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    metrics.total_time = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);

    collect_metrics(metrics, task_latencies);
    
    return metrics;
}

void BenchmarkExecutor::collect_metrics(PerformanceMetrics& metrics,
                                      const std::vector<std::chrono::nanoseconds>& task_times) {
    if (metrics.total_time.count() > 0) {
        metrics.throughput_tasks_per_sec = (double)config_.task_count / 
            (metrics.total_time.count() / 1e9);
    }

    if (!task_times.empty()) {
        long long total_latency_ns = 0;
        for(const auto& d : task_times) {
            total_latency_ns += d.count();
        }
        metrics.avg_task_time = std::chrono::nanoseconds(total_latency_ns / task_times.size());

        auto sorted_times = task_times;
        std::sort(sorted_times.begin(), sorted_times.end());
        
        metrics.min_task_time = sorted_times.front();
        metrics.max_task_time = sorted_times.back();
        
        metrics.latency_percentiles.push_back(sorted_times[task_times.size() * 0.50]);
        metrics.latency_percentiles.push_back(sorted_times[task_times.size() * 0.90]);
        metrics.latency_percentiles.push_back(sorted_times[task_times.size() * 0.95]);
        metrics.latency_percentiles.push_back(sorted_times[task_times.size() * 0.99]);
    }
} 