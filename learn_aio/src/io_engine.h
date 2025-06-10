#pragma once

#include <cstdint>
#include <cstddef>

namespace aio_bench {

class Config;
class StatsCollector;

class IOEngine {
public:
    IOEngine(const Config& config, StatsCollector& stats) 
        : config_(config), stats_(stats) {}
    virtual ~IOEngine() = default;
    
    virtual bool initialize() = 0;
    virtual void cleanup() = 0;
    
    // IO 操作
    virtual bool submit_io(uint64_t offset, uint32_t size, bool is_read) = 0;
    virtual int wait_for_completion(int timeout_ms = -1) = 0;
    virtual void process_completions() = 0;
    
    // 辅助方法
    virtual bool is_initialized() const = 0;
    virtual size_t get_pending_count() const = 0;

protected:
    const Config& config_;
    StatsCollector& stats_;
};

} // namespace aio_bench 