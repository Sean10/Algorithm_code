#pragma once

#include "io_engine.h"
#include <libaio.h>
#include <memory>
#include <vector>
#include <functional>
#include <atomic>
#include <thread>

namespace aio_bench {

class Config;
class StatsCollector;

struct IORequest {
    struct iocb cb;
    void* buffer;
    uint64_t offset;
    uint32_t size;
    bool is_read;
    std::chrono::steady_clock::time_point start_time;
    uint64_t user_data;
};

class AIOEngine : public IOEngine {
private:
    io_context_t ctx_;
    int fd_;
    bool initialized_;
    
    std::vector<std::unique_ptr<IORequest>> pending_requests_;
    std::vector<struct io_event> events_;
    
    // 内存池
    std::vector<void*> buffer_pool_;
    std::atomic<size_t> buffer_index_{0};
    
public:
    AIOEngine(const Config& config, StatsCollector& stats);
    ~AIOEngine() override;
    
    bool initialize() override;
    void cleanup() override;
    
    // IO 操作
    bool submit_io(uint64_t offset, uint32_t size, bool is_read) override;
    int wait_for_completion(int timeout_ms = -1) override;
    void process_completions() override;
    
    // 辅助方法
    bool is_initialized() const override { return initialized_; }
    size_t get_pending_count() const override { return pending_requests_.size(); }
    
private:
    bool open_file();
    void close_file();
    bool setup_buffers();
    void cleanup_buffers();
    
    void* get_buffer();
    void return_buffer(void* buffer);
    
    void prepare_read_request(IORequest* req, uint64_t offset, uint32_t size);
    void prepare_write_request(IORequest* req, uint64_t offset, uint32_t size);
    void fill_write_buffer(void* buffer, uint32_t size, uint64_t offset);
    bool verify_read_buffer(const void* buffer, uint32_t size, uint64_t offset);
};

} // namespace aio_bench 