#include "utils.h"
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <unistd.h>
#include <fcntl.h>
#include <chrono>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cstdlib>
#include <vector>
#include <sched.h>

namespace aio_bench {

bool Utils::file_exists(const std::string& filename) {
    struct stat st;
    return stat(filename.c_str(), &st) == 0;
}

bool Utils::is_block_device(const std::string& filename) {
    struct stat st;
    if (stat(filename.c_str(), &st) != 0) {
        return false;
    }
    return S_ISBLK(st.st_mode);
}

uint64_t Utils::get_file_size(const std::string& filename) {
    struct stat st;
    if (stat(filename.c_str(), &st) != 0) {
        return 0;
    }
    return static_cast<uint64_t>(st.st_size);
}

uint64_t Utils::get_device_size(const std::string& device) {
    int fd = open(device.c_str(), O_RDONLY);
    if (fd < 0) {
        return 0;
    }
    
    uint64_t size = 0;
    if (ioctl(fd, BLKGETSIZE64, &size) != 0) {
        close(fd);
        return 0;
    }
    
    close(fd);
    return size;
}

void* Utils::aligned_alloc(size_t size, size_t alignment) {
    void* ptr = nullptr;
    if (posix_memalign(&ptr, alignment, size) != 0) {
        return nullptr;
    }
    return ptr;
}

void Utils::aligned_free(void* ptr) {
    if (ptr) {
        free(ptr);
    }
}

uint64_t Utils::get_time_us() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
}

std::string Utils::format_bytes(uint64_t bytes) {
    const char* units[] = {"B", "KB", "MB", "GB", "TB"};
    const size_t num_units = sizeof(units) / sizeof(units[0]);
    
    double size = static_cast<double>(bytes);
    size_t unit_index = 0;
    
    while (size >= 1024.0 && unit_index < num_units - 1) {
        size /= 1024.0;
        unit_index++;
    }
    
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(2) << size << " " << units[unit_index];
    return oss.str();
}

std::string Utils::format_duration(double seconds) {
    std::ostringstream oss;
    
    if (seconds < 60) {
        oss << std::fixed << std::setprecision(2) << seconds << "s";
    } else if (seconds < 3600) {
        int mins = static_cast<int>(seconds / 60);
        double secs = seconds - mins * 60;
        oss << mins << "m" << std::fixed << std::setprecision(2) << secs << "s";
    } else {
        int hours = static_cast<int>(seconds / 3600);
        int mins = static_cast<int>((seconds - hours * 3600) / 60);
        double secs = seconds - hours * 3600 - mins * 60;
        oss << hours << "h" << mins << "m" << std::fixed << std::setprecision(2) << secs << "s";
    }
    
    return oss.str();
}

std::string Utils::to_lower(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(), 
                   [](unsigned char c) { return std::tolower(c); });
    return result;
}

std::vector<std::string> Utils::split(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;
    
    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    
    return tokens;
}

int Utils::get_cpu_count() {
    return static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN));
}

void Utils::set_thread_affinity(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    pthread_t current_thread = pthread_self();
    int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
    
    if (result != 0) {
        std::cerr << "警告: 无法设置线程亲和性到CPU " << cpu_id << std::endl;
    }
}

void Utils::set_high_priority() {
    struct sched_param param;
    param.sched_priority = sched_get_priority_max(SCHED_FIFO);
    
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        // 如果无法设置实时调度，尝试设置nice值
        if (nice(-20) == -1) {
            std::cerr << "警告: 无法设置高优先级" << std::endl;
        }
    }
}

} // namespace aio_bench 