#pragma once

#include <string>
#include <cstdint>
#include <cstddef>

namespace aio_bench {

enum class IOPattern {
    RANDOM_READ,
    RANDOM_WRITE,
    RANDOM_READ_WRITE,
    SEQUENTIAL_READ,
    SEQUENTIAL_WRITE
};

enum class IOMode {
    SYNC,
    ASYNC
};

enum class EngineType {
    LIBAIO,
    IO_URING
};

struct Config {
    // 文件/设备配置
    std::string filename;
    uint64_t file_size = 1ULL << 30;  // 1GB 默认
    bool direct_io = true;
    bool create_file = true;
    
    // IO 模式配置
    IOPattern pattern = IOPattern::RANDOM_READ_WRITE;
    IOMode mode = IOMode::ASYNC;
    EngineType engine_type = EngineType::LIBAIO;
    uint32_t block_size = 4096;  // 4KB
    uint32_t queue_depth = 32;
    uint32_t num_threads = 1;
    
    // 测试配置
    uint32_t runtime_seconds = 30;
    uint64_t max_operations = 0;  // 0 表示无限制
    bool verify_data = false;
    
    // 性能配置
    uint32_t batch_size = 16;  // 批量提交IO数量
    bool use_polling = false;
    uint32_t polling_timeout_us = 1000;
    
    // 输出配置
    bool verbose = false;
    uint32_t report_interval_seconds = 5;
    std::string output_format = "text";  // text, json, csv
    
    // 性能分析配置
    bool enable_perf_benchmark = false;
    bool enable_runtime_profiling = false;
    
    // 解析命令行参数
    bool parse_args(int argc, char* argv[]);
    void print_help() const;
    void print_config() const;
    
private:
    IOPattern parse_pattern(const std::string& pattern_str) const;
    EngineType parse_engine_type(const std::string& engine_str) const;
};

} // namespace aio_bench 