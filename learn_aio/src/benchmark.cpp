#include "benchmark.h"
#include "aio_engine.h"
#include "uring_engine.h"
#include "utils.h"
#include <signal.h>
#include <iostream>
#include <chrono>
#include <random>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <cerrno>

namespace aio_bench {

thread_local std::mt19937 Benchmark::rng_(std::random_device{}());

Benchmark::Benchmark(const Config& config) 
    : config_(config), stats_() {
}

Benchmark::~Benchmark() {
    stop();
}

bool Benchmark::initialize() {
    if (config_.verbose) {
        config_.print_config();
    }
    
    // 创建测试文件（如果需要）
    if (config_.create_file && !Utils::file_exists(config_.filename) && 
        !Utils::is_block_device(config_.filename)) {
        create_test_file();
    }
    
    // 初始化引擎
    engines_.reserve(config_.num_threads);
    for (uint32_t i = 0; i < config_.num_threads; i++) {
        std::unique_ptr<IOEngine> engine;
        
        // 根据配置创建不同类型的引擎
        switch (config_.engine_type) {
            case EngineType::LIBAIO:
                engine = std::make_unique<AIOEngine>(config_, stats_);
                break;
            case EngineType::IO_URING:
                engine = std::make_unique<UringEngine>(config_, stats_);
                break;
            default:
                std::cerr << "错误: 未知的引擎类型" << std::endl;
                return false;
        }
        
        if (!engine->initialize()) {
            std::cerr << "错误: 无法初始化引擎 " << i << std::endl;
            return false;
        }
        engines_.push_back(std::move(engine));
    }
    
    std::cout << "初始化完成，准备开始测试..." << std::endl;
    return true;
}

void Benchmark::run() {
    if (engines_.empty()) {
        std::cerr << "错误: 未初始化任何IO引擎" << std::endl;
        return;
    }
    
    // 设置信号处理
    signal(SIGINT, [](int) {
        std::cout << "\n收到中断信号，正在停止测试..." << std::endl;
    });
    
    should_stop_ = false;
    time_expired_ = false;
    
    // 启动统计收集
    stats_.start();
    
    // 启动监控线程
    std::thread monitor_thread(&Benchmark::monitor_thread, this);
    
    // 启动工作线程
    worker_threads_.reserve(config_.num_threads);
    for (uint32_t i = 0; i < config_.num_threads; i++) {
        worker_threads_.emplace_back(&Benchmark::worker_thread, this, i);
        
        // 设置线程亲和性
        if (config_.num_threads > 1) {
            int cpu_id = i % Utils::get_cpu_count();
            Utils::set_thread_affinity(cpu_id);
        }
    }
    
    // 等待工作线程完成
    for (auto& thread : worker_threads_) {
        thread.join();
    }
    
    // 停止监控
    should_stop_ = true;
    monitor_thread.join();
    
    // 输出最终报告
    if (config_.output_format == "json") {
        stats_.print_json_report();
    } else if (config_.output_format == "csv") {
        stats_.print_csv_header();
        stats_.print_csv_line();
    } else {
        stats_.print_final_report();
    }
    
    // 清理测试文件
    if (config_.create_file && !config_.verify_data) {
        cleanup_test_file();
    }
}

void Benchmark::stop() {
    should_stop_ = true;
    
    // 等待线程结束
    for (auto& thread : worker_threads_) {
        if (thread.joinable()) {
            thread.join();
        }
    }
    worker_threads_.clear();
    
    // 清理引擎
    engines_.clear();
}

void Benchmark::worker_thread(int thread_id) {
    if (thread_id >= static_cast<int>(engines_.size())) {
        return;
    }
    
    IOEngine& engine = *engines_[thread_id];
    uint64_t operations = 0;
    uint64_t max_offset;
    
    // 计算最大偏移量
    if (Utils::is_block_device(config_.filename)) {
        max_offset = Utils::get_device_size(config_.filename);
    } else {
        max_offset = config_.file_size;
    }
    
    if (max_offset < config_.block_size) {
        std::cerr << "错误: 文件/设备太小" << std::endl;
        return;
    }
    
    max_offset -= config_.block_size;
    
    std::cout << "线程 " << thread_id << " 开始工作..." << std::endl;
    
    while (!should_stop_ && !time_expired_) {
        // 检查操作数限制
        if (config_.max_operations > 0 && operations >= config_.max_operations) {
            break;
        }
        
        // 生成IO请求
        uint64_t offset = generate_random_offset(max_offset, config_.block_size);
        bool is_read = should_do_read_operation();
        
        // 保持队列深度
        while (engine.get_pending_count() >= config_.queue_depth && !should_stop_) {
            engine.wait_for_completion(10); // 10ms超时
        }
        
        // 提交IO
        if (engine.submit_io(offset, config_.block_size, is_read)) {
            operations++;
        }
        
        // 批量等待完成
        if (operations % config_.batch_size == 0) {
            engine.wait_for_completion(config_.use_polling ? 0 : 1);
        }
    }
    
    // 等待所有待处理的IO完成
    while (engine.get_pending_count() > 0) {
        engine.wait_for_completion(100);
    }
    
    std::cout << "线程 " << thread_id << " 完成，总操作数: " << operations << std::endl;
}

void Benchmark::monitor_thread() {
    auto start_time = std::chrono::steady_clock::now();
    auto last_report = start_time;
    
    while (!should_stop_) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - start_time);
        
        // 检查时间限制
        if (config_.runtime_seconds > 0 && elapsed.count() >= config_.runtime_seconds) {
            time_expired_ = true;
            break;
        }
        
        // 定期报告
        auto report_elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - last_report);
        if (report_elapsed.count() >= config_.report_interval_seconds) {
            if (config_.output_format == "text" && config_.verbose) {
                stats_.print_report();
            } else if (config_.output_format == "csv") {
                stats_.print_csv_line();
            }
            last_report = now;
        }
    }
}

uint64_t Benchmark::generate_random_offset(uint64_t max_offset, uint32_t block_size) {
    switch (config_.pattern) {
        case IOPattern::RANDOM_READ:
        case IOPattern::RANDOM_WRITE:
        case IOPattern::RANDOM_READ_WRITE: {
            std::uniform_int_distribution<uint64_t> dist(0, max_offset / block_size);
            return dist(rng_) * block_size;
        }
        case IOPattern::SEQUENTIAL_READ:
        case IOPattern::SEQUENTIAL_WRITE: {
            static thread_local uint64_t seq_offset = 0;
            uint64_t offset = seq_offset;
            seq_offset = (seq_offset + block_size) % (max_offset + block_size);
            return offset;
        }
        default:
            return 0;
    }
}

bool Benchmark::should_do_read_operation() {
    switch (config_.pattern) {
        case IOPattern::RANDOM_READ:
        case IOPattern::SEQUENTIAL_READ:
            return true;
        case IOPattern::RANDOM_WRITE:
        case IOPattern::SEQUENTIAL_WRITE:
            return false;
        case IOPattern::RANDOM_READ_WRITE: {
            std::uniform_int_distribution<int> dist(0, 1);
            return dist(rng_) == 0;
        }
        default:
            return true;
    }
}

void Benchmark::create_test_file() {
    std::cout << "创建测试文件: " << config_.filename << ", 大小: " << config_.file_size << " 字节" << std::endl;
    
    int fd = open(config_.filename.c_str(), O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (fd < 0) {
        std::cerr << "错误: 无法创建测试文件: " << strerror(errno) << std::endl;
        return;
    }
    
    if (ftruncate(fd, config_.file_size) != 0) {
        std::cerr << "错误: 无法设置文件大小: " << strerror(errno) << std::endl;
    }
    
    close(fd);
}

void Benchmark::cleanup_test_file() {
    if (config_.create_file && Utils::file_exists(config_.filename) && 
        !Utils::is_block_device(config_.filename)) {
        std::cout << "清理测试文件: " << config_.filename << std::endl;
        unlink(config_.filename.c_str());
    }
}

void Benchmark::print_progress() {
    // 进度输出逻辑（可选）
}

void Benchmark::handle_signal() {
    // 信号处理逻辑（可选）
}

} // namespace aio_bench 