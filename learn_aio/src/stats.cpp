#include "stats.h"
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <sstream>

namespace aio_bench {

void IOStats::add_latency(uint64_t latency_us) {
    std::lock_guard<std::mutex> lock(latency_mutex);
    latencies.push_back(latency_us);
}

void IOStats::reset() {
    operations = 0;
    bytes = 0;
    read_operations = 0;
    write_operations = 0;
    read_bytes = 0;
    write_bytes = 0;
    errors = 0;
    
    std::lock_guard<std::mutex> lock(latency_mutex);
    latencies.clear();
}

IOStatsSnapshot IOStats::snapshot() const {
    IOStatsSnapshot result;
    result.operations = operations.load();
    result.bytes = bytes.load();
    result.read_operations = read_operations.load();
    result.write_operations = write_operations.load();
    result.read_bytes = read_bytes.load();
    result.write_bytes = write_bytes.load();
    result.errors = errors.load();
    
    std::lock_guard<std::mutex> lock(latency_mutex);
    result.latencies = latencies;
    
    return result;
}

StatsCollector::StatsCollector() {
    start_time_ = std::chrono::steady_clock::now();
    last_report_time_ = start_time_;
}

void StatsCollector::start() {
    start_time_ = std::chrono::steady_clock::now();
    last_report_time_ = start_time_;
    stats_.reset();
}

void StatsCollector::record_io(bool is_read, uint64_t bytes, uint64_t latency_us) {
    stats_.operations++;
    stats_.bytes += bytes;
    
    if (is_read) {
        stats_.read_operations++;
        stats_.read_bytes += bytes;
    } else {
        stats_.write_operations++;
        stats_.write_bytes += bytes;
    }
    
    stats_.add_latency(latency_us);
}

void StatsCollector::record_error() {
    stats_.errors++;
}

IOStatsSnapshot StatsCollector::get_stats() const {
    return stats_.snapshot();
}

double StatsCollector::get_iops() const {
    double elapsed = get_elapsed_seconds();
    if (elapsed <= 0) return 0.0;
    return static_cast<double>(stats_.operations) / elapsed;
}

double StatsCollector::get_bandwidth_mbps() const {
    double elapsed = get_elapsed_seconds();
    if (elapsed <= 0) return 0.0;
    return (static_cast<double>(stats_.bytes) / (1024.0 * 1024.0)) / elapsed;
}

double StatsCollector::get_avg_latency_us() const {
    std::lock_guard<std::mutex> lock(stats_.latency_mutex);
    if (stats_.latencies.empty()) return 0.0;
    
    uint64_t sum = 0;
    for (uint64_t latency : stats_.latencies) {
        sum += latency;
    }
    return static_cast<double>(sum) / stats_.latencies.size();
}

double StatsCollector::get_p99_latency_us() const {
    return get_percentile_latency(99.0);
}

double StatsCollector::get_p95_latency_us() const {
    return get_percentile_latency(95.0);
}

void StatsCollector::print_report() const {
    double elapsed = get_elapsed_seconds();
    double iops = get_iops();
    double bandwidth = get_bandwidth_mbps();
    double avg_latency = get_avg_latency_us();
    double p95_latency = get_p95_latency_us();
    double p99_latency = get_p99_latency_us();
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "运行时间: " << elapsed << "s, "
              << "IOPS: " << iops << ", "
              << "带宽: " << bandwidth << " MB/s, "
              << "平均延迟: " << avg_latency << "μs, "
              << "P95延迟: " << p95_latency << "μs, "
              << "P99延迟: " << p99_latency << "μs, "
              << "错误: " << stats_.errors << std::endl;
}

void StatsCollector::print_final_report() const {
    std::cout << "\n=== 最终统计报告 ===" << std::endl;
    
    double elapsed = get_elapsed_seconds();
    double iops = get_iops();
    double bandwidth = get_bandwidth_mbps();
    double avg_latency = get_avg_latency_us();
    double p95_latency = get_p95_latency_us();
    double p99_latency = get_p99_latency_us();
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "总运行时间: " << elapsed << " 秒" << std::endl;
    std::cout << "总操作数: " << stats_.operations << std::endl;
    std::cout << "读操作数: " << stats_.read_operations << std::endl;
    std::cout << "写操作数: " << stats_.write_operations << std::endl;
    std::cout << "总字节数: " << stats_.bytes << " (" << (stats_.bytes / (1024.0 * 1024.0)) << " MB)" << std::endl;
    std::cout << "读取字节: " << stats_.read_bytes << " (" << (stats_.read_bytes / (1024.0 * 1024.0)) << " MB)" << std::endl;
    std::cout << "写入字节: " << stats_.write_bytes << " (" << (stats_.write_bytes / (1024.0 * 1024.0)) << " MB)" << std::endl;
    std::cout << "错误数: " << stats_.errors << std::endl;
    std::cout << std::endl;
    std::cout << "平均 IOPS: " << iops << std::endl;
    std::cout << "平均带宽: " << bandwidth << " MB/s" << std::endl;
    std::cout << "平均延迟: " << avg_latency << " μs" << std::endl;
    std::cout << "P95延迟: " << p95_latency << " μs" << std::endl;
    std::cout << "P99延迟: " << p99_latency << " μs" << std::endl;
    std::cout << "=================" << std::endl;
}

void StatsCollector::print_json_report() const {
    double elapsed = get_elapsed_seconds();
    double iops = get_iops();
    double bandwidth = get_bandwidth_mbps();
    double avg_latency = get_avg_latency_us();
    double p95_latency = get_p95_latency_us();
    double p99_latency = get_p99_latency_us();
    
    std::cout << "{" << std::endl;
    std::cout << "  \"elapsed_seconds\": " << elapsed << "," << std::endl;
    std::cout << "  \"total_operations\": " << stats_.operations << "," << std::endl;
    std::cout << "  \"read_operations\": " << stats_.read_operations << "," << std::endl;
    std::cout << "  \"write_operations\": " << stats_.write_operations << "," << std::endl;
    std::cout << "  \"total_bytes\": " << stats_.bytes << "," << std::endl;
    std::cout << "  \"read_bytes\": " << stats_.read_bytes << "," << std::endl;
    std::cout << "  \"write_bytes\": " << stats_.write_bytes << "," << std::endl;
    std::cout << "  \"errors\": " << stats_.errors << "," << std::endl;
    std::cout << "  \"iops\": " << std::fixed << std::setprecision(2) << iops << "," << std::endl;
    std::cout << "  \"bandwidth_mbps\": " << bandwidth << "," << std::endl;
    std::cout << "  \"avg_latency_us\": " << avg_latency << "," << std::endl;
    std::cout << "  \"p95_latency_us\": " << p95_latency << "," << std::endl;
    std::cout << "  \"p99_latency_us\": " << p99_latency << std::endl;
    std::cout << "}" << std::endl;
}

void StatsCollector::print_csv_header() const {
    std::cout << "time,operations,read_ops,write_ops,bytes,read_bytes,write_bytes,errors,iops,bandwidth_mbps,avg_latency_us,p95_latency_us,p99_latency_us" << std::endl;
}

void StatsCollector::print_csv_line() const {
    double elapsed = get_elapsed_seconds();
    double iops = get_iops();
    double bandwidth = get_bandwidth_mbps();
    double avg_latency = get_avg_latency_us();
    double p95_latency = get_p95_latency_us();
    double p99_latency = get_p99_latency_us();
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << elapsed << ","
              << stats_.operations << ","
              << stats_.read_operations << ","
              << stats_.write_operations << ","
              << stats_.bytes << ","
              << stats_.read_bytes << ","
              << stats_.write_bytes << ","
              << stats_.errors << ","
              << iops << ","
              << bandwidth << ","
              << avg_latency << ","
              << p95_latency << ","
              << p99_latency << std::endl;
}

double StatsCollector::get_elapsed_seconds() const {
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - start_time_);
    return static_cast<double>(duration.count()) / 1000000.0;
}

uint64_t StatsCollector::get_percentile_latency(double percentile) const {
    std::lock_guard<std::mutex> lock(stats_.latency_mutex);
    if (stats_.latencies.empty()) return 0;
    
    std::vector<uint64_t> sorted_latencies = stats_.latencies;
    std::sort(sorted_latencies.begin(), sorted_latencies.end());
    
    size_t index = static_cast<size_t>((percentile / 100.0) * (sorted_latencies.size() - 1));
    return sorted_latencies[index];
}

} // namespace aio_bench 