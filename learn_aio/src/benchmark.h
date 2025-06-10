#pragma once

#include "config.h"
#include "stats.h"
#include "io_engine.h"
#include <vector>
#include <thread>
#include <atomic>
#include <random>

namespace aio_bench {

class Benchmark {
private:
    const Config& config_;
    StatsCollector stats_;
    std::vector<std::unique_ptr<IOEngine>> engines_;
    std::vector<std::thread> worker_threads_;
    std::atomic<bool> should_stop_{false};
    std::atomic<bool> time_expired_{false};
    
    // 随机数生成
    thread_local static std::mt19937 rng_;
    
public:
    explicit Benchmark(const Config& config);
    ~Benchmark();
    
    bool initialize();
    void run();
    void stop();
    
private:
    void worker_thread(int thread_id);
    void monitor_thread();
    uint64_t generate_random_offset(uint64_t max_offset, uint32_t block_size);
    bool should_do_read_operation();
    void create_test_file();
    void cleanup_test_file();
    
    // 辅助方法
    void print_progress();
    void handle_signal();
};

} // namespace aio_bench 