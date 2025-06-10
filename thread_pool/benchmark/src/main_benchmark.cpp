#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"
#include <iostream>

using namespace tp_bench;

int main(int argc, char** argv) {
    std::cout << "=== 线程池性能基准测试套件 ===" << std::endl;
    std::cout << "支持CPU密集型、IO密集型、混合负载等多种测试场景" << std::endl;
    std::cout << "支持不同内存分配器和线程池实现的对比" << std::endl;
    
    // 基础配置
    BenchmarkConfig base_config;
    base_config.task_count = 10000;
    base_config.iterations = 5;
    base_config.enable_memory_profiling = true;
    base_config.enable_latency_tracking = true;
    
    std::vector<PerformanceMetrics> results;
    std::vector<std::string> test_names;
    
    // 测试1: CPU密集型任务 - 不同线程数
    std::cout << "\n=== CPU密集型任务测试 ===" << std::endl;
    for (size_t threads : {1, 2, 4, 8, 16}) {
        auto config = base_config;
        config.thread_count = threads;
        config.task_type = TaskType::CPU_INTENSIVE;
        config.cpu_work_size = 50000;
        
        BenchmarkExecutor executor(config);
        auto metrics = executor.run_benchmark();
        
        results.push_back(metrics);
        test_names.push_back("CPU_Intensive_" + std::to_string(threads) + "_threads");
        
        std::cout << "线程数: " << threads 
                  << ", 吞吐量: " << metrics.throughput_tasks_per_sec << " tasks/sec"
                  << ", 平均延迟: " << metrics.avg_task_time.count() << " ns"
                  << ", 内存峰值: " << metrics.memory_peak_kb << " KB" << std::endl;
    }
    
    // 测试2: IO密集型任务
    std::cout << "\n=== IO密集型任务测试 ===" << std::endl;
    for (size_t delay : {1, 5, 10, 20}) {
        auto config = base_config;
        config.task_type = TaskType::IO_INTENSIVE;
        config.io_delay_ms = delay;
        config.thread_count = 8;
        
        BenchmarkExecutor executor(config);
        auto metrics = executor.run_benchmark();
        
        results.push_back(metrics);
        test_names.push_back("IO_Intensive_" + std::to_string(delay) + "ms_delay");
        
        std::cout << "IO延迟: " << delay << "ms"
                  << ", 吞吐量: " << metrics.throughput_tasks_per_sec << " tasks/sec"
                  << ", 平均延迟: " << metrics.avg_task_time.count() << " ns" << std::endl;
    }
    
    // 测试3: 内存密集型任务
    std::cout << "\n=== 内存密集型任务测试 ===" << std::endl;
    for (size_t mem_size : {64, 256, 1024, 4096}) {
        auto config = base_config;
        config.task_type = TaskType::MEMORY_INTENSIVE;
        config.memory_size_kb = mem_size;
        config.thread_count = 8;
        
        BenchmarkExecutor executor(config);
        auto metrics = executor.run_benchmark();
        
        results.push_back(metrics);
        test_names.push_back("Memory_Intensive_" + std::to_string(mem_size) + "KB");
        
        std::cout << "内存大小: " << mem_size << "KB"
                  << ", 吞吐量: " << metrics.throughput_tasks_per_sec << " tasks/sec"
                  << ", 内存峰值: " << metrics.memory_peak_kb << " KB" << std::endl;
    }
    
    // 测试4: 不同线程池实现对比
    std::cout << "\n=== 线程池实现对比测试 ===" << std::endl;
    std::vector<ThreadPoolType> pool_types = {
        ThreadPoolType::TP_CUSTOM,
        ThreadPoolType::TP_STD_ASYNC
    };
    
    for (auto pool_type : pool_types) {
        auto config = base_config;
        config.pool_type = pool_type;
        config.task_type = TaskType::CPU_INTENSIVE;
        config.thread_count = 8;
        
        BenchmarkExecutor executor(config);
        auto metrics = executor.run_benchmark();
        
        results.push_back(metrics);
        std::string pool_name = (pool_type == ThreadPoolType::TP_CUSTOM) ? "Custom" : "StdAsync";
        test_names.push_back("ThreadPool_" + pool_name);
        
        std::cout << "线程池类型: " << pool_name
                  << ", 吞吐量: " << metrics.throughput_tasks_per_sec << " tasks/sec"
                  << ", 平均延迟: " << metrics.avg_task_time.count() << " ns" << std::endl;
    }
    
    // 生成最终报告
    std::cout << "\n=== 生成测试报告 ===" << std::endl;
    ResultReporter::print_summary(results, test_names);
    ResultReporter::save_to_json(results, test_names, "benchmark_results.json");
    ResultReporter::save_to_csv(results, test_names, "benchmark_results.csv");
    
    std::cout << "\n测试完成！结果已保存到 benchmark_results.json 和 benchmark_results.csv" << std::endl;
    std::cout << "可以使用 analyze_results.py 脚本进行进一步分析和可视化" << std::endl;
    
    return 0;
} 