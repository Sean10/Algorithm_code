#include "../include/benchmark_framework.hpp"
#include <iostream>
#include <fstream>
#include <iomanip>

using namespace tp_bench;

// --- Factory Functions ---

std::unique_ptr<TaskGenerator> tp_bench::create_task_generator(TaskType type) {
    switch (type) {
        case TaskType::CPU_INTENSIVE:
            return std::make_unique<CPUIntensiveTaskGenerator>();
        case TaskType::IO_INTENSIVE:
            return std::make_unique<IOIntensiveTaskGenerator>();
        case TaskType::MEMORY_INTENSIVE:
            return std::make_unique<MemoryIntensiveTaskGenerator>();
        default:
            // 默认返回CPU密集型
            return std::make_unique<CPUIntensiveTaskGenerator>();
    }
}

std::unique_ptr<ThreadPoolAdapter> tp_bench::create_thread_pool_adapter(ThreadPoolType type) {
    switch (type) {
        case ThreadPoolType::TP_CUSTOM_OPTIMIZED:
            return std::make_unique<CustomThreadPoolAdapter>();
        case ThreadPoolType::TP_CUSTOM_ORIGINAL:
            return std::make_unique<OriginalThreadPoolAdapter>();
        case ThreadPoolType::TP_STD_ASYNC:
            return std::make_unique<StdAsyncAdapter>();
        default:
             // 默认返回我们的优化后实现
            return std::make_unique<CustomThreadPoolAdapter>();
    }
}


// --- ResultReporter ---

void ResultReporter::print_summary(const std::vector<PerformanceMetrics>& results,
                                   const std::vector<std::string>& test_names) {
    std::cout << "\n--- Benchmark Summary ---\n";
    std::cout << std::left << std::setw(30) << "Test Name"
              << std::setw(20) << "Throughput (ops/s)"
              << std::setw(20) << "Avg Latency (us)"
              << std::setw(20) << "Peak Memory (KB)"
              << "\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        std::cout << std::left << std::setw(30) << test_names[i]
                  << std::setw(20) << std::fixed << std::setprecision(2) << r.throughput_tasks_per_sec
                  << std::setw(20) << std::fixed << std::setprecision(3) << (r.avg_task_time.count() / 1000.0)
                  << std::setw(20) << r.memory_peak_kb
                  << "\n";
    }
}

void ResultReporter::save_to_json(const std::vector<PerformanceMetrics>& results,
                                  const std::vector<std::string>& test_names,
                                  const std::string& filename) {
    // 简单的JSON输出实现
    std::ofstream ofs(filename);
    ofs << "{\n";
    ofs << "  \"results\": [\n";
    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        ofs << "    {\n";
        ofs << "      \"test_name\": \"" << test_names[i] << "\",\n";
        ofs << "      \"throughput_ops_per_sec\": " << r.throughput_tasks_per_sec << ",\n";
        ofs << "      \"avg_latency_ns\": " << r.avg_task_time.count() << ",\n";
        // ... 其他指标
        ofs << "      \"memory_peak_kb\": " << r.memory_peak_kb << "\n";
        ofs << "    }" << (i == results.size() - 1 ? "" : ",") << "\n";
    }
    ofs << "  ]\n";
    ofs << "}\n";
}

void ResultReporter::save_to_csv(const std::vector<PerformanceMetrics>& results,
                                 const std::vector<std::string>& test_names,
                                 const std::string& filename) {
    std::ofstream ofs(filename);
    // CSV Header
    ofs << "TestName,Throughput,AvgLatency_ns,MinLatency_ns,MaxLatency_ns,P50,P90,P95,P99,PeakMemory_KB\n";
    
    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        ofs << test_names[i] << ",";
        ofs << r.throughput_tasks_per_sec << ",";
        ofs << r.avg_task_time.count() << ",";
        // ... 其他指标
        ofs << r.memory_peak_kb << "\n";
    }
}

void ResultReporter::generate_comparison_chart(const std::vector<PerformanceMetrics>&,
                                               const std::vector<std::string>&,
                                               const std::string&) {
    std::cout << "Chart generation is not implemented yet. Use analyze_results.py.\n";
} 