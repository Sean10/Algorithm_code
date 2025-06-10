#ifndef THREAD_POOL_BENCHMARK_FRAMEWORK_HPP
#define THREAD_POOL_BENCHMARK_FRAMEWORK_HPP

#include "thread_pool/thread_pool.hpp"
#include "thread_pool/thread_pool_original.hpp"

#include <benchmark/benchmark.h>
#include <chrono>
#include <vector>
#include <memory>
#include <functional>
#include <string>
#include <map>
#include <thread>
#include <atomic>
#include <future>
#include <random>

namespace tp_bench {

// 任务类型枚举
enum class TaskType {
    CPU_INTENSIVE,
    IO_INTENSIVE,
    MEMORY_INTENSIVE,
    MIXED
};

// 内存分配器类型
enum class AllocatorType {
    STANDARD,
    TCMALLOC,
    JEMALLOC
};

// 线程池实现类型
enum class ThreadPoolType {
    TP_CUSTOM_OPTIMIZED, // 优化后的线程池 (工作窃取)
    TP_CUSTOM_ORIGINAL,  // 优化前的线程池 (单队列)
    TP_STD_ASYNC,      // std::async
    TP_TBB,            // Intel TBB
    TP_OPENMP,         // OpenMP
    TP_THREADPOOL_H    // 其他开源实现
};

// 基准测试配置
struct BenchmarkConfig {
    size_t thread_count = std::thread::hardware_concurrency();
    size_t task_count = 1000;
    size_t iterations = 10;
    TaskType task_type = TaskType::CPU_INTENSIVE;
    AllocatorType allocator = AllocatorType::STANDARD;
    ThreadPoolType pool_type = ThreadPoolType::TP_CUSTOM_OPTIMIZED;
    
    // 任务特定参数
    size_t cpu_work_size = 10000;     // CPU密集型任务的工作量
    size_t io_delay_ms = 10;          // IO密集型任务的延迟
    size_t memory_size_kb = 64;       // 内存密集型任务的内存大小
    
    // 高级配置
    bool enable_memory_profiling = false;
    bool enable_cpu_profiling = false;
    bool enable_latency_tracking = false;
};

// 性能指标结构
struct PerformanceMetrics {
    std::chrono::nanoseconds total_time{0};
    std::chrono::nanoseconds avg_task_time{0};
    std::chrono::nanoseconds min_task_time{std::chrono::nanoseconds::max()};
    std::chrono::nanoseconds max_task_time{0};
    
    size_t memory_peak_kb = 0;
    size_t memory_avg_kb = 0;
    double cpu_utilization = 0.0;
    double throughput_tasks_per_sec = 0.0;
    
    size_t successful_tasks = 0;
    size_t failed_tasks = 0;
    
    // 延迟分布
    std::vector<std::chrono::nanoseconds> latency_percentiles; // P50, P90, P95, P99
};

// 任务生成器接口
class TaskGenerator {
public:
    virtual ~TaskGenerator() = default;
    virtual std::function<void()> generate_task() = 0;
    virtual std::function<int()> generate_task_with_result() = 0;
    virtual void configure(const BenchmarkConfig& config) = 0;
};

// CPU密集型任务生成器
class CPUIntensiveTaskGenerator : public TaskGenerator {
private:
    size_t work_size_;
    mutable std::mt19937 rng_;
    
public:
    CPUIntensiveTaskGenerator() : rng_(std::random_device{}()) {}
    
    void configure(const BenchmarkConfig& config) override {
        work_size_ = config.cpu_work_size;
    }
    
    std::function<void()> generate_task() override;
    std::function<int()> generate_task_with_result() override;
};

// IO密集型任务生成器
class IOIntensiveTaskGenerator : public TaskGenerator {
private:
    size_t delay_ms_;
    mutable std::mt19937 rng_;
    
public:
    IOIntensiveTaskGenerator() : rng_(std::random_device{}()) {}
    
    void configure(const BenchmarkConfig& config) override {
        delay_ms_ = config.io_delay_ms;
    }
    
    std::function<void()> generate_task() override;
    std::function<int()> generate_task_with_result() override;
};

// 内存密集型任务生成器
class MemoryIntensiveTaskGenerator : public TaskGenerator {
private:
    size_t memory_size_;
    mutable std::mt19937 rng_;
    
public:
    MemoryIntensiveTaskGenerator() : rng_(std::random_device{}()) {}
    
    void configure(const BenchmarkConfig& config) override {
        memory_size_ = config.memory_size_kb * 1024;
    }
    
    std::function<void()> generate_task() override;
    std::function<int()> generate_task_with_result() override;
};

// 内存性能监控器
class MemoryProfiler {
private:
    std::atomic<bool> monitoring_{false};
    std::thread monitor_thread_;
    std::vector<size_t> memory_samples_;
    std::chrono::milliseconds sample_interval_{10};
    
public:
    void start_monitoring();
    void stop_monitoring();
    PerformanceMetrics get_memory_metrics() const;
    
private:
    size_t get_current_memory_usage() const;
};

// 线程池适配器接口
class ThreadPoolAdapter {
public:
    virtual ~ThreadPoolAdapter() = default;
    virtual void initialize(size_t thread_count) = 0;
    virtual void shutdown() = 0;
    virtual std::future<void> submit_task(std::function<void()> task) = 0;
    virtual std::future<int> submit_task_with_result(std::function<int()> task) = 0;
    virtual std::string get_name() const = 0;
    virtual ThreadPoolType get_type() const = 0;
};

// 我们的线程池适配器
class CustomThreadPoolAdapter : public ThreadPoolAdapter {
private:
    std::unique_ptr<tp::ThreadPool> pool_;
    
public:
    void initialize(size_t thread_count) override;
    void shutdown() override;
    std::future<void> submit_task(std::function<void()> task) override;
    std::future<int> submit_task_with_result(std::function<int()> task) override;
    std::string get_name() const override { return "Optimized ThreadPool"; }
    ThreadPoolType get_type() const override { return ThreadPoolType::TP_CUSTOM_OPTIMIZED; }
};

// 优化前版本的适配器
class OriginalThreadPoolAdapter : public ThreadPoolAdapter {
private:
    std::unique_ptr<tp_original::ThreadPool> pool_;

public:
    void initialize(size_t thread_count) override;
    void shutdown() override;
    std::future<void> submit_task(std::function<void()> task) override;
    std::future<int> submit_task_with_result(std::function<int()> task) override;
    std::string get_name() const override { return "Original ThreadPool"; }
    ThreadPoolType get_type() const override { return ThreadPoolType::TP_CUSTOM_ORIGINAL; }
};

// std::async适配器
class StdAsyncAdapter : public ThreadPoolAdapter {
public:
    void initialize(size_t thread_count) override;
    void shutdown() override;
    std::future<void> submit_task(std::function<void()> task) override;
    std::future<int> submit_task_with_result(std::function<int()> task) override;
    std::string get_name() const override { return "std::async"; }
    ThreadPoolType get_type() const override { return ThreadPoolType::TP_STD_ASYNC; }
};

// 基准测试执行器
class BenchmarkExecutor {
private:
    BenchmarkConfig config_;
    std::unique_ptr<TaskGenerator> task_generator_;
    std::unique_ptr<ThreadPoolAdapter> thread_pool_;
    std::unique_ptr<MemoryProfiler> memory_profiler_;
    
public:
    explicit BenchmarkExecutor(const BenchmarkConfig& config);
    
    PerformanceMetrics run_benchmark();
    void configure_task_generator();
    void configure_thread_pool();
    
private:
    PerformanceMetrics execute_tasks();
    void collect_metrics(PerformanceMetrics& metrics, 
                        const std::vector<std::chrono::nanoseconds>& task_times);
};

// 结果报告器
class ResultReporter {
public:
    static void print_summary(const std::vector<PerformanceMetrics>& results,
                             const std::vector<std::string>& test_names);
    static void save_to_json(const std::vector<PerformanceMetrics>& results,
                            const std::vector<std::string>& test_names,
                            const std::string& filename);
    static void save_to_csv(const std::vector<PerformanceMetrics>& results,
                           const std::vector<std::string>& test_names,
                           const std::string& filename);
    static void generate_comparison_chart(const std::vector<PerformanceMetrics>& results,
                                         const std::vector<std::string>& test_names,
                                         const std::string& output_path);
};

// 工厂函数
std::unique_ptr<TaskGenerator> create_task_generator(TaskType type);
std::unique_ptr<ThreadPoolAdapter> create_thread_pool_adapter(ThreadPoolType type);

// Google Benchmark集成宏
#define THREAD_POOL_BENCHMARK(name, config) \
    static void BM_##name(benchmark::State& state) { \
        BenchmarkExecutor executor(config); \
        for (auto _ : state) { \
            auto metrics = executor.run_benchmark(); \
            state.counters["throughput"] = benchmark::Counter( \
                metrics.throughput_tasks_per_sec, benchmark::Counter::kIsRate); \
            state.counters["avg_latency_ns"] = benchmark::Counter( \
                metrics.avg_task_time.count()); \
            state.counters["memory_peak_kb"] = benchmark::Counter( \
                metrics.memory_peak_kb); \
        } \
    } \
    BENCHMARK(BM_##name)

} // namespace tp_bench

#endif // THREAD_POOL_BENCHMARK_FRAMEWORK_HPP 