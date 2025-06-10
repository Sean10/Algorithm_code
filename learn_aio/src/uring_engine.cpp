#include "uring_engine.h"
#include "config.h"
#include "stats.h"
#include "utils.h"
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <chrono>

namespace aio_bench {

UringEngine::UringEngine(const Config& config, StatsCollector& stats)
    : IOEngine(config, stats), fd_(-1), initialized_(false) {
    memset(&ring_, 0, sizeof(ring_));
}

UringEngine::~UringEngine() {
    cleanup();
}

bool UringEngine::initialize() {
    if (initialized_) {
        return true;
    }
    
    // 初始化io_uring
    int ret = io_uring_queue_init(config_.queue_depth, &ring_, 0);
    if (ret < 0) {
        std::cerr << "错误: 无法初始化io_uring: " << strerror(-ret) << std::endl;
        return false;
    }
    
    // 打开文件
    if (!open_file()) {
        io_uring_queue_exit(&ring_);
        return false;
    }
    
    // 设置内存缓冲区
    if (!setup_buffers()) {
        close_file();
        io_uring_queue_exit(&ring_);
        return false;
    }
    
    initialized_ = true;
    return true;
}

void UringEngine::cleanup() {
    if (!initialized_) {
        return;
    }
    
    cleanup_buffers();
    close_file();
    
    io_uring_queue_exit(&ring_);
    
    initialized_ = false;
}

bool UringEngine::submit_io(uint64_t offset, uint32_t size, bool is_read) {
    if (!initialized_) {
        return false;
    }
    
    // 获取SQE
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring_);
    if (!sqe) {
        if (config_.verbose) {
            std::cerr << "警告: 无法获取SQE" << std::endl;
        }
        return false;
    }
    
    // 创建IO请求
    auto req = std::make_unique<UringIORequest>();
    req->buffer = get_buffer();
    if (!req->buffer) {
        return false;
    }
    
    req->offset = offset;
    req->size = size;
    req->is_read = is_read;
    req->start_time = std::chrono::steady_clock::now();
    req->user_data = reinterpret_cast<uint64_t>(req.get());
    
    // 准备IO操作
    if (is_read) {
        io_uring_prep_read(sqe, fd_, req->buffer, size, offset);
    } else {
        fill_write_buffer(req->buffer, size, offset);
        io_uring_prep_write(sqe, fd_, req->buffer, size, offset);
    }
    
    // 设置用户数据
    io_uring_sqe_set_data(sqe, req.get());
    
    // 提交IO请求
    int ret = io_uring_submit(&ring_);
    if (ret < 0) {
        return_buffer(req->buffer);
        if (config_.verbose) {
            std::cerr << "警告: IO提交失败: " << strerror(-ret) << std::endl;
        }
        return false;
    }
    
    // 保存请求引用
    pending_requests_.push_back(std::move(req));
    return true;
}

int UringEngine::wait_for_completion(int timeout_ms) {
    if (!initialized_ || pending_requests_.empty()) {
        return 0;
    }
    
    struct __kernel_timespec timeout_spec;
    struct __kernel_timespec* timeout_ptr = nullptr;
    
    if (timeout_ms >= 0) {
        timeout_spec.tv_sec = timeout_ms / 1000;
        timeout_spec.tv_nsec = (timeout_ms % 1000) * 1000000;
        timeout_ptr = &timeout_spec;
    }
    
    struct io_uring_cqe *cqe;
    int ret;
    
    if (config_.use_polling) {
        // 轮询模式
        ret = io_uring_peek_cqe(&ring_, &cqe);
        if (ret == 0) {
            process_completions();
            return 1;
        }
        return 0;
    } else {
        // 等待模式
        ret = io_uring_wait_cqe_timeout(&ring_, &cqe, timeout_ptr);
        if (ret == 0) {
            process_completions();
            return 1;
        }
        return ret;
    }
}

void UringEngine::process_completions() {
    auto now = std::chrono::steady_clock::now();
    struct io_uring_cqe *cqe;
    unsigned head;
    unsigned count = 0;
    
    io_uring_for_each_cqe(&ring_, head, cqe) {
        UringIORequest* req = static_cast<UringIORequest*>(io_uring_cqe_get_data(cqe));
        if (!req) {
            continue;
        }
        
        // 计算延迟
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - req->start_time);
        uint64_t latency_us = duration.count();
        
        // 检查IO结果
        if (cqe->res == static_cast<int>(req->size)) {
            // IO成功
            if (config_.verify_data && req->is_read) {
                if (!verify_read_buffer(req->buffer, req->size, req->offset)) {
                    stats_.record_error();
                }
            }
            stats_.record_io(req->is_read, req->size, latency_us);
        } else {
            // IO失败
            if (config_.verbose) {
                std::cerr << "警告: IO操作失败, 预期: " << req->size << ", 实际: " << cqe->res << std::endl;
            }
            stats_.record_error();
        }
        
        // 归还缓冲区
        return_buffer(req->buffer);
        
        // 从待处理列表中移除
        auto it = std::find_if(pending_requests_.begin(), pending_requests_.end(),
                              [req](const std::unique_ptr<UringIORequest>& ptr) {
                                  return ptr.get() == req;
                              });
        if (it != pending_requests_.end()) {
            pending_requests_.erase(it);
        }
        
        count++;
    }
    
    io_uring_cq_advance(&ring_, count);
}

size_t UringEngine::get_pending_count() const {
    return pending_requests_.size();
}

bool UringEngine::open_file() {
    int flags = O_RDWR;
    
    if (config_.direct_io) {
        flags |= O_DIRECT;
    }
    
    if (config_.create_file && !Utils::file_exists(config_.filename)) {
        flags |= O_CREAT;
    }
    
    fd_ = open(config_.filename.c_str(), flags, 0644);
    if (fd_ < 0) {
        std::cerr << "错误: 无法打开文件 " << config_.filename << ": " << strerror(errno) << std::endl;
        return false;
    }
    
    // 如果是新文件，预分配空间
    if (config_.create_file && !Utils::is_block_device(config_.filename)) {
        if (ftruncate(fd_, config_.file_size) != 0) {
            std::cerr << "警告: 无法设置文件大小: " << strerror(errno) << std::endl;
        }
    }
    
    return true;
}

void UringEngine::close_file() {
    if (fd_ >= 0) {
        close(fd_);
        fd_ = -1;
    }
}

bool UringEngine::setup_buffers() {
    size_t buffer_count = config_.queue_depth * 2; // 额外缓冲区
    size_t buffer_size = config_.block_size;
    
    buffer_pool_.reserve(buffer_count);
    
    for (size_t i = 0; i < buffer_count; i++) {
        void* buffer;
        if (posix_memalign(&buffer, 4096, buffer_size) != 0) {
            std::cerr << "错误: 无法分配对齐内存" << std::endl;
            cleanup_buffers();
            return false;
        }
        buffer_pool_.push_back(buffer);
    }
    
    return true;
}

void UringEngine::cleanup_buffers() {
    for (void* buffer : buffer_pool_) {
        free(buffer);
    }
    buffer_pool_.clear();
    buffer_index_ = 0;
}

void* UringEngine::get_buffer() {
    if (buffer_pool_.empty()) {
        return nullptr;
    }
    
    size_t index = buffer_index_.fetch_add(1) % buffer_pool_.size();
    return buffer_pool_[index];
}

void UringEngine::return_buffer(void* buffer) {
    // 在这个简单实现中，我们不需要显式归还缓冲区
    // 因为我们使用循环缓冲池
    (void)buffer;
}

void UringEngine::fill_write_buffer(void* buffer, uint32_t size, uint64_t offset) {
    // 填充写入数据模式（用于数据验证）
    uint32_t* data = static_cast<uint32_t*>(buffer);
    uint32_t pattern = static_cast<uint32_t>(offset / config_.block_size);
    
    for (uint32_t i = 0; i < size / sizeof(uint32_t); i++) {
        data[i] = pattern + i;
    }
}

bool UringEngine::verify_read_buffer(const void* buffer, uint32_t size, uint64_t offset) {
    // 验证读取数据的正确性
    const uint32_t* data = static_cast<const uint32_t*>(buffer);
    uint32_t pattern = static_cast<uint32_t>(offset / config_.block_size);
    
    for (uint32_t i = 0; i < size / sizeof(uint32_t); i++) {
        if (data[i] != pattern + i) {
            return false;
        }
    }
    return true;
}

} // namespace aio_bench 