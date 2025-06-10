#pragma once

#include <atomic>
#include <chrono>
#include <vector>
#include <mutex>

namespace aio_bench {

// 可拷贝的统计数据结构
struct IOStatsSnapshot {
    uint64_t operations = 0;
    uint64_t bytes = 0;
    uint64_t read_operations = 0;
    uint64_t write_operations = 0;
    uint64_t read_bytes = 0;
    uint64_t write_bytes = 0;
    uint64_t errors = 0;
    std::vector<uint64_t> latencies;
};

// 线程安全的统计数据收集器
struct IOStats {
    std::atomic<uint64_t> operations{0};
    std::atomic<uint64_t> bytes{0};
    std::atomic<uint64_t> read_operations{0};
    std::atomic<uint64_t> write_operations{0};
    std::atomic<uint64_t> read_bytes{0};
    std::atomic<uint64_t> write_bytes{0};
    std::atomic<uint64_t> errors{0};
    
    // 延迟统计
    std::vector<uint64_t> latencies;
    mutable std::mutex latency_mutex;
    
    void add_latency(uint64_t latency_us);
    void reset();
    
    // 生成可拷贝的快照
    IOStatsSnapshot snapshot() const;
};

class StatsCollector {
private:
    IOStats stats_;
    std::chrono::steady_clock::time_point start_time_;
    std::chrono::steady_clock::time_point last_report_time_;
    
public:
    StatsCollector();
    
    void start();
    void record_io(bool is_read, uint64_t bytes, uint64_t latency_us);
    void record_error();
    
    // 获取统计信息
    IOStatsSnapshot get_stats() const;
    double get_iops() const;
    double get_bandwidth_mbps() const;
    double get_avg_latency_us() const;
    double get_p99_latency_us() const;
    double get_p95_latency_us() const;
    
    // 打印报告
    void print_report() const;
    void print_final_report() const;
    void print_json_report() const;
    void print_csv_header() const;
    void print_csv_line() const;
    
private:
    double get_elapsed_seconds() const;
    uint64_t get_percentile_latency(double percentile) const;
};

} // namespace aio_bench 