#include "../include/benchmark_framework.hpp"
#include <vector>
#include <thread>
#include <cmath>

using namespace tp_bench;

// --- CPUIntensiveTaskGenerator ---
std::function<void()> CPUIntensiveTaskGenerator::generate_task() {
    return [work_size = this->work_size_]() {
        double result = 0.0;
        for (size_t i = 0; i < work_size; ++i) {
            result += std::sqrt(static_cast<double>(i));
        }
        benchmark::DoNotOptimize(result);
    };
}

std::function<int()> CPUIntensiveTaskGenerator::generate_task_with_result() {
    return [work_size = this->work_size_]() {
        double result = 0.0;
        for (size_t i = 0; i < work_size; ++i) {
            result += std::sqrt(static_cast<double>(i));
        }
        benchmark::DoNotOptimize(result);
        return static_cast<int>(result) % 100;
    };
}


// --- IOIntensiveTaskGenerator ---
std::function<void()> IOIntensiveTaskGenerator::generate_task() {
    return [delay_ms = this->delay_ms_]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    };
}

std::function<int()> IOIntensiveTaskGenerator::generate_task_with_result() {
    return [delay_ms = this->delay_ms_]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
        return 1;
    };
}


// --- MemoryIntensiveTaskGenerator ---
std::function<void()> MemoryIntensiveTaskGenerator::generate_task() {
    return [memory_size = this->memory_size_]() {
        std::vector<char> buffer(memory_size);
        benchmark::DoNotOptimize(buffer.data());
        for (size_t i = 0; i < memory_size; ++i) {
            buffer[i] = static_cast<char>(i % 256);
        }
        benchmark::ClobberMemory();
    };
}

std::function<int()> MemoryIntensiveTaskGenerator::generate_task_with_result() {
    return [memory_size = this->memory_size_]() {
        std::vector<char> buffer(memory_size);
        benchmark::DoNotOptimize(buffer.data());
        for (size_t i = 0; i < memory_size; ++i) {
            buffer[i] = static_cast<char>(i % 256);
        }
        benchmark::ClobberMemory();
        return static_cast<int>(buffer.size());
    };
} 