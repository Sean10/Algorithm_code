#pragma once

#include <string>
#include <cstdint>
#include <vector>
#include <algorithm>

namespace aio_bench {

class Utils {
public:
    // 文件操作
    static bool file_exists(const std::string& filename);
    static bool is_block_device(const std::string& filename);
    static uint64_t get_file_size(const std::string& filename);
    static uint64_t get_device_size(const std::string& device);
    
    // 内存对齐
    static void* aligned_alloc(size_t size, size_t alignment = 4096);
    static void aligned_free(void* ptr);
    
    // 时间工具
    static uint64_t get_time_us();
    static std::string format_bytes(uint64_t bytes);
    static std::string format_duration(double seconds);
    
    // 字符串工具
    static std::string to_lower(const std::string& str);
    static std::vector<std::string> split(const std::string& str, char delimiter);
    
    // 系统信息
    static int get_cpu_count();
    static void set_thread_affinity(int cpu_id);
    static void set_high_priority();
    
private:
    Utils() = default;
};

} // namespace aio_bench 