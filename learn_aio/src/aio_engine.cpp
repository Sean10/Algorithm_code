#include "aio_engine.h"
#include "config.h"
#include "stats.h"
#include "utils.h"
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <chrono>

namespace aio_bench {

AIOEngine::AIOEngine(const Config& config, StatsCollector& stats)
    : IOEngine(config, stats), ctx_{0}, fd_(-1), initialized_(false) {
    events_.resize(config_.queue_depth);
}

AIOEngine::~AIOEngine() {
    cleanup();
}

bool AIOEngine::initialize() {
    if (initialized_) {
        return true;
    }
    
    // 初始化AIO上下文
    if (io_setup(config_.queue_depth, &ctx_) != 0) {
        std::cerr << "错误: 无法初始化AIO上下文: " << strerror(errno) << std::endl;
        return false;
    }
    
    // 打开文件
    if (!open_file()) {
        io_destroy(ctx_);
        return false;
    }
    
    // 设置内存缓冲区
    if (!setup_buffers()) {
        close_file();
        io_destroy(ctx_);
        return false;
    }
    
    initialized_ = true;
    return true;
}

void AIOEngine::cleanup() {
    if (!initialized_) {
        return;
    }
    
    cleanup_buffers();
    close_file();
    
    if (ctx_) {
        io_destroy(ctx_);
        ctx_ = 0;
    }
    
    initialized_ = false;
}

bool AIOEngine::submit_io(uint64_t offset, uint32_t size, bool is_read) {
    if (!initialized_) {
        return false;
    }
    
    // 创建IO请求
    auto req = std::make_unique<IORequest>();
    req->buffer = get_buffer();
    if (!req->buffer) {
        return false;
    }
    
    req->offset = offset;
    req->size = size;
    req->is_read = is_read;
    req->start_time = std::chrono::steady_clock::now();
    req->user_data = reinterpret_cast<uint64_t>(req.get());
    
    // 准备IO控制块
    if (is_read) {
        prepare_read_request(req.get(), offset, size);
    } else {
        prepare_write_request(req.get(), offset, size);
    }
    
    // 提交IO请求
    struct iocb* cbs[] = {&req->cb};
    int ret = io_submit(ctx_, 1, cbs);
    if (ret != 1) {
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

int AIOEngine::wait_for_completion(int timeout_ms) {
    if (!initialized_ || pending_requests_.empty()) {
        return 0;
    }
    
    struct timespec timeout_spec;
    struct timespec* timeout_ptr = nullptr;
    
    if (timeout_ms >= 0) {
        timeout_spec.tv_sec = timeout_ms / 1000;
        timeout_spec.tv_nsec = (timeout_ms % 1000) * 1000000;
        timeout_ptr = &timeout_spec;
    }
    
    int num_events = io_getevents(ctx_, 1, events_.size(), events_.data(), timeout_ptr);
    if (num_events <= 0) {
        return num_events;
    }
    
    process_completions();
    return num_events;
}

void AIOEngine::process_completions() {
    auto now = std::chrono::steady_clock::now();
    
    for (size_t i = 0; i < events_.size() && events_[i].data != 0; i++) {
        struct io_event& event = events_[i];
        IORequest* req = reinterpret_cast<IORequest*>(event.data);
        
        // 计算延迟
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - req->start_time);
        uint64_t latency_us = duration.count();
        
        // 检查IO结果
        if (event.res == req->size) {
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
                std::cerr << "警告: IO操作失败, 预期: " << req->size << ", 实际: " << event.res << std::endl;
            }
            stats_.record_error();
        }
        
        // 归还缓冲区
        return_buffer(req->buffer);
        
        // 从待处理列表中移除
        auto it = std::find_if(pending_requests_.begin(), pending_requests_.end(),
                              [req](const std::unique_ptr<IORequest>& ptr) {
                                  return ptr.get() == req;
                              });
        if (it != pending_requests_.end()) {
            pending_requests_.erase(it);
        }
        
        // 清空事件数据
        events_[i].data = 0;
    }
}

bool AIOEngine::open_file() {
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

void AIOEngine::close_file() {
    if (fd_ >= 0) {
        close(fd_);
        fd_ = -1;
    }
}

bool AIOEngine::setup_buffers() {
    size_t buffer_size = config_.block_size;
    size_t num_buffers = config_.queue_depth * 2;  // 双倍缓冲
    
    buffer_pool_.reserve(num_buffers);
    
    for (size_t i = 0; i < num_buffers; i++) {
        void* buffer = Utils::aligned_alloc(buffer_size, 4096);
        if (!buffer) {
            std::cerr << "错误: 无法分配对齐内存" << std::endl;
            cleanup_buffers();
            return false;
        }
        buffer_pool_.push_back(buffer);
    }
    
    return true;
}

void AIOEngine::cleanup_buffers() {
    for (void* buffer : buffer_pool_) {
        Utils::aligned_free(buffer);
    }
    buffer_pool_.clear();
    buffer_index_ = 0;
}

void* AIOEngine::get_buffer() {
    if (buffer_pool_.empty()) {
        return nullptr;
    }
    
    size_t index = buffer_index_.fetch_add(1) % buffer_pool_.size();
    return buffer_pool_[index];
}

void AIOEngine::return_buffer(void* buffer) {
    // 简单的轮询分配，不需要显式归还
    // 实际应用中可以实现更复杂的内存池管理
}

void AIOEngine::prepare_read_request(IORequest* req, uint64_t offset, uint32_t size) {
    memset(&req->cb, 0, sizeof(req->cb));
    req->cb.aio_fildes = fd_;
    req->cb.aio_lio_opcode = IO_CMD_PREAD;
    req->cb.u.c.buf = req->buffer;
    req->cb.u.c.nbytes = size;
    req->cb.u.c.offset = offset;
    req->cb.data = reinterpret_cast<void*>(req->user_data);
}

void AIOEngine::prepare_write_request(IORequest* req, uint64_t offset, uint32_t size) {
    // 填充写入数据
    fill_write_buffer(req->buffer, size, offset);
    
    memset(&req->cb, 0, sizeof(req->cb));
    req->cb.aio_fildes = fd_;
    req->cb.aio_lio_opcode = IO_CMD_PWRITE;
    req->cb.u.c.buf = req->buffer;
    req->cb.u.c.nbytes = size;
    req->cb.u.c.offset = offset;
    req->cb.data = reinterpret_cast<void*>(req->user_data);
}

void AIOEngine::fill_write_buffer(void* buffer, uint32_t size, uint64_t offset) {
    uint32_t* data = static_cast<uint32_t*>(buffer);
    uint32_t pattern = static_cast<uint32_t>(offset / sizeof(uint32_t));
    
    for (size_t i = 0; i < size / sizeof(uint32_t); i++) {
        data[i] = pattern + i;
    }
}

bool AIOEngine::verify_read_buffer(const void* buffer, uint32_t size, uint64_t offset) {
    const uint32_t* data = static_cast<const uint32_t*>(buffer);
    uint32_t expected_pattern = static_cast<uint32_t>(offset / sizeof(uint32_t));
    
    for (size_t i = 0; i < size / sizeof(uint32_t); i++) {
        if (data[i] != expected_pattern + i) {
            if (config_.verbose) {
                std::cerr << "数据验证失败: 偏移=" << offset + i * sizeof(uint32_t) 
                         << ", 期望=" << (expected_pattern + i) 
                         << ", 实际=" << data[i] << std::endl;
            }
            return false;
        }
    }
    
    return true;
}

} // namespace aio_bench 