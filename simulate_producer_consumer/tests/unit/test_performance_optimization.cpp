#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <random>
#include <algorithm>
#include <iomanip>

#include "../../src/stage5_performance/performance_optimized_queue.hpp"
#include "../../src/stage5_performance/performance_comparison.hpp"
#include "../../src/stage2_spsc/spsc_ring_buffer.hpp"

using namespace stage5;

/**
 * Stage5 性能优化测试
 * 
 * 测试内容：
 * 1. 缓存行对齐效果测试
 * 2. 批量操作性能测试
 * 3. 内存预取效果测试
 * 4. 伪共享避免测试
 * 5. 性能基准对比测试
 */

class PerformanceOptimizationTest : public ::testing::Test {
protected:
    static constexpr size_t QUEUE_SIZE = 8192;
    static constexpr size_t TEST_OPERATIONS = 100000;
    static constexpr size_t THREAD_COUNT = 4;
    
    void SetUp() override {
        // 每个测试前的设置
    }
    
    void TearDown() override {
        // 每个测试后的清理
    }
    
    // 辅助函数：测量操作延迟
    template<typename Func>
    double measure_latency_ns(Func&& func, size_t iterations = 1000) {
        // 预热
        for (size_t i = 0; i < 100; ++i) {
            func();
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < iterations; ++i) {
            func();
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
        
        return static_cast<double>(duration.count()) / iterations;
    }
    
    // 辅助函数：测量吞吐量
    template<typename Func>
    double measure_throughput_ops_per_sec(Func&& func, size_t operations = 10000) {
        auto start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < operations; ++i) {
            func();
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        return (operations * 1000000.0) / duration.count();
    }
};

/**
 * 缓存行对齐基本功能测试
 */
TEST_F(PerformanceOptimizationTest, CacheAlignedBasic) {
    CacheAligned<int> aligned_int(42);
    
    EXPECT_EQ(aligned_int.load(), 42);
    
    aligned_int.store(100);
    EXPECT_EQ(aligned_int.load(), 100);
    
    int expected = 100;
    bool success = aligned_int.compare_exchange_weak(expected, 200);
    EXPECT_TRUE(success);
    EXPECT_EQ(aligned_int.load(), 200);
    
    // 检查内存对齐
    uintptr_t addr = reinterpret_cast<uintptr_t>(&aligned_int);
    EXPECT_EQ(addr % get_cache_line_size(), 0) << "CacheAligned should be aligned to cache line boundary";
}

/**
 * 优化环形缓冲区基本功能测试
 */
TEST_F(PerformanceOptimizationTest, OptimizedRingBufferBasic) {
    OptimizedRingBuffer<int, 64> buffer;
    
    // 测试空缓冲区
    EXPECT_TRUE(buffer.empty());
    EXPECT_EQ(buffer.size(), 0);
    EXPECT_EQ(buffer.capacity(), 63);  // 实际容量是 N-1
    
    // 测试入队
    for (int i = 0; i < 32; ++i) {
        EXPECT_TRUE(buffer.enqueue(i));
    }
    
    EXPECT_FALSE(buffer.empty());
    EXPECT_EQ(buffer.size(), 32);
    
    // 测试出队
    for (int i = 0; i < 32; ++i) {
        int item;
        EXPECT_TRUE(buffer.dequeue(item));
        EXPECT_EQ(item, i);
    }
    
    EXPECT_TRUE(buffer.empty());
    EXPECT_EQ(buffer.size(), 0);
}

/**
 * 批量操作功能测试
 */
TEST_F(PerformanceOptimizationTest, BatchOperations) {
    OptimizedRingBuffer<int, 1024> buffer;
    
    constexpr size_t BATCH_SIZE = 64;
    std::vector<int> input_batch(BATCH_SIZE);
    std::vector<int> output_batch(BATCH_SIZE);
    
    // 准备测试数据
    for (size_t i = 0; i < BATCH_SIZE; ++i) {
        input_batch[i] = static_cast<int>(i + 100);
    }
    
    // 测试批量入队
    size_t enqueued = buffer.enqueue_batch(input_batch.data(), BATCH_SIZE);
    EXPECT_EQ(enqueued, BATCH_SIZE);
    EXPECT_EQ(buffer.size(), BATCH_SIZE);
    
    // 测试批量出队
    size_t dequeued = buffer.dequeue_batch(output_batch.data(), BATCH_SIZE);
    EXPECT_EQ(dequeued, BATCH_SIZE);
    EXPECT_TRUE(buffer.empty());
    
    // 验证数据正确性
    for (size_t i = 0; i < BATCH_SIZE; ++i) {
        EXPECT_EQ(output_batch[i], input_batch[i]);
    }
    
    // 测试部分批量操作
    size_t partial_size = 20;
    size_t partial_enqueued = buffer.enqueue_batch(input_batch.data(), partial_size);
    EXPECT_EQ(partial_enqueued, partial_size);
    
    size_t partial_dequeued = buffer.dequeue_batch(output_batch.data(), partial_size);
    EXPECT_EQ(partial_dequeued, partial_size);
    
    for (size_t i = 0; i < partial_size; ++i) {
        EXPECT_EQ(output_batch[i], input_batch[i]);
    }
}

/**
 * 环绕边界测试
 */
TEST_F(PerformanceOptimizationTest, WrapAroundTest) {
    OptimizedRingBuffer<int, 8> buffer;  // 小缓冲区测试边界情况
    
    // 填充缓冲区到接近满
    for (int i = 0; i < 6; ++i) {
        EXPECT_TRUE(buffer.enqueue(i));
    }
    
    // 消费一些元素
    for (int i = 0; i < 3; ++i) {
        int item;
        EXPECT_TRUE(buffer.dequeue(item));
        EXPECT_EQ(item, i);
    }
    
    // 再添加元素，这应该导致环绕
    for (int i = 100; i < 104; ++i) {
        EXPECT_TRUE(buffer.enqueue(i));
    }
    
    // 验证剩余的元素
    std::vector<int> expected = {3, 4, 5, 100, 101, 102, 103};
    for (int expected_value : expected) {
        int item;
        EXPECT_TRUE(buffer.dequeue(item));
        EXPECT_EQ(item, expected_value);
    }
    
    EXPECT_TRUE(buffer.empty());
}

/**
 * 伪共享避免测试
 */
TEST_F(PerformanceOptimizationTest, FalseSharingAvoidance) {
    // 模拟伪共享场景
    struct UnalignedCounters {
        std::atomic<size_t> counter1{0};
        std::atomic<size_t> counter2{0};
    };
    
    struct AlignedCounters {
        alignas(64) std::atomic<size_t> counter1{0};
        alignas(64) std::atomic<size_t> counter2{0};
    };
    
    constexpr size_t iterations = 100000;
    
    // 测试未对齐的情况
    UnalignedCounters unaligned;
    auto unaligned_start = std::chrono::high_resolution_clock::now();
    
    std::thread t1([&]() {
        for (size_t i = 0; i < iterations; ++i) {
            unaligned.counter1.fetch_add(1, std::memory_order_relaxed);
        }
    });
    
    std::thread t2([&]() {
        for (size_t i = 0; i < iterations; ++i) {
            unaligned.counter2.fetch_add(1, std::memory_order_relaxed);
        }
    });
    
    t1.join();
    t2.join();
    
    auto unaligned_end = std::chrono::high_resolution_clock::now();
    
    // 测试对齐的情况
    AlignedCounters aligned;
    auto aligned_start = std::chrono::high_resolution_clock::now();
    
    std::thread t3([&]() {
        for (size_t i = 0; i < iterations; ++i) {
            aligned.counter1.fetch_add(1, std::memory_order_relaxed);
        }
    });
    
    std::thread t4([&]() {
        for (size_t i = 0; i < iterations; ++i) {
            aligned.counter2.fetch_add(1, std::memory_order_relaxed);
        }
    });
    
    t3.join();
    t4.join();
    
    auto aligned_end = std::chrono::high_resolution_clock::now();
    
    auto unaligned_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        unaligned_end - unaligned_start);
    auto aligned_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        aligned_end - aligned_start);
    
    // 验证计数正确性
    EXPECT_EQ(unaligned.counter1.load(), iterations);
    EXPECT_EQ(unaligned.counter2.load(), iterations);
    EXPECT_EQ(aligned.counter1.load(), iterations);
    EXPECT_EQ(aligned.counter2.load(), iterations);
    
    std::cout << "伪共享测试结果:" << std::endl;
    std::cout << "- 未对齐: " << unaligned_duration.count() << " μs" << std::endl;
    std::cout << "- 对齐: " << aligned_duration.count() << " μs" << std::endl;
    
    // 对齐版本应该不会显著慢于未对齐版本
    // 注意：在某些系统上差异可能不明显
    double ratio = static_cast<double>(unaligned_duration.count()) / aligned_duration.count();
    EXPECT_GE(ratio, 0.8) << "Aligned version should not be significantly slower";
}

/**
 * 并发性能测试
 */
TEST_F(PerformanceOptimizationTest, ConcurrentPerformance) {
    OptimizedRingBuffer<int, QUEUE_SIZE> buffer;
    
    const size_t operations_per_thread = TEST_OPERATIONS / THREAD_COUNT;
    std::atomic<size_t> total_enqueued{0};
    std::atomic<size_t> total_dequeued{0};
    
    std::vector<std::thread> threads;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // 生产者线程
    for (size_t i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&, i]() {
            size_t enqueued = 0;
            for (size_t j = 0; j < operations_per_thread; ++j) {
                int value = static_cast<int>(i * operations_per_thread + j);
                while (!buffer.enqueue(value)) {
                    std::this_thread::yield();
                }
                ++enqueued;
            }
            total_enqueued.fetch_add(enqueued);
        });
    }
    
    // 消费者线程
    for (size_t i = 0; i < THREAD_COUNT / 2; ++i) {
        threads.emplace_back([&]() {
            size_t dequeued = 0;
            int value;
            
            while (dequeued < operations_per_thread) {
                if (buffer.dequeue(value)) {
                    ++dequeued;
                } else {
                    std::this_thread::yield();
                }
            }
            total_dequeued.fetch_add(dequeued);
        });
    }
    
    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    
    // 验证正确性
    size_t expected_total = (THREAD_COUNT / 2) * operations_per_thread;
    EXPECT_EQ(total_enqueued.load(), expected_total);
    EXPECT_EQ(total_dequeued.load(), expected_total);
    EXPECT_TRUE(buffer.empty());
    
    // 输出性能统计
    double throughput = (2.0 * expected_total * 1000000.0) / duration.count();
    std::cout << "并发性能测试结果:" << std::endl;
    std::cout << "- 操作总数: " << (2 * expected_total) << std::endl;
    std::cout << "- 总时间: " << duration.count() << " μs" << std::endl;
    std::cout << "- 吞吐量: " << std::fixed << std::setprecision(0) << throughput << " ops/sec" << std::endl;
}

/**
 * 批量操作性能对比测试
 */
TEST_F(PerformanceOptimizationTest, BatchVsSinglePerformance) {
    OptimizedRingBuffer<int, QUEUE_SIZE> buffer;
    
    constexpr size_t total_operations = 50000;
    constexpr size_t batch_size = 64;
    constexpr size_t batch_count = total_operations / batch_size;
    
    std::vector<int> test_data(batch_size);
    std::vector<int> output_data(batch_size);
    
    for (size_t i = 0; i < batch_size; ++i) {
        test_data[i] = static_cast<int>(i);
    }
    
    // 测试单个操作性能
    auto single_start = std::chrono::high_resolution_clock::now();
    
    for (size_t i = 0; i < total_operations; ++i) {
        while (!buffer.enqueue(static_cast<int>(i))) {
            std::this_thread::yield();
        }
    }
    
    for (size_t i = 0; i < total_operations; ++i) {
        int item;
        while (!buffer.dequeue(item)) {
            std::this_thread::yield();
        }
    }
    
    auto single_end = std::chrono::high_resolution_clock::now();
    
    // 测试批量操作性能
    auto batch_start = std::chrono::high_resolution_clock::now();
    
    for (size_t i = 0; i < batch_count; ++i) {
        while (buffer.enqueue_batch(test_data.data(), batch_size) != batch_size) {
            std::this_thread::yield();
        }
    }
    
    for (size_t i = 0; i < batch_count; ++i) {
        while (buffer.dequeue_batch(output_data.data(), batch_size) != batch_size) {
            std::this_thread::yield();
        }
    }
    
    auto batch_end = std::chrono::high_resolution_clock::now();
    
    auto single_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        single_end - single_start);
    auto batch_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        batch_end - batch_start);
    
    double improvement = static_cast<double>(single_duration.count()) / batch_duration.count();
    
    std::cout << "批量操作性能测试结果:" << std::endl;
    std::cout << "- 单个操作时间: " << single_duration.count() << " μs" << std::endl;
    std::cout << "- 批量操作时间: " << batch_duration.count() << " μs" << std::endl;
    std::cout << "- 性能提升: " << std::fixed << std::setprecision(2) << improvement << "x" << std::endl;
    
    // 批量操作应该显著快于单个操作
    EXPECT_GT(improvement, 1.5) << "Batch operations should be significantly faster";
    EXPECT_TRUE(buffer.empty());
}

/**
 * 内存序优化测试
 */
TEST_F(PerformanceOptimizationTest, MemoryOrderingOptimization) {
    // 这个测试主要验证不同内存序的编译和基本功能
    // 实际性能差异需要在特定架构上测试
    
    using MO = ArchOptimizedMemoryOrder;
    
    std::atomic<int> test_var{0};
    
    // 测试不同内存序的基本操作
    test_var.store(42, MO::release);
    int value = test_var.load(MO::acquire);
    EXPECT_EQ(value, 42);
    
    int expected = 42;
    bool success = test_var.compare_exchange_strong(expected, 100, MO::release, MO::relaxed);
    EXPECT_TRUE(success);
    EXPECT_EQ(test_var.load(MO::acquire), 100);
    
    std::cout << "内存序优化测试通过" << std::endl;
}

/**
 * 性能调优工具测试
 */
TEST_F(PerformanceOptimizationTest, PerformanceTuner) {
    // 测试延迟测量
    double latency = PerformanceTuner::measure_latency([]() {
        volatile int x = 42 * 2;  // 简单操作
        (void)x;  // 避免编译器警告
    });
    
    EXPECT_GT(latency, 0.0);
    std::cout << "简单操作延迟: " << latency << " ns" << std::endl;
    
    // 测试吞吐量测量
    std::atomic<int> counter{0};
    double throughput = PerformanceTuner::measure_throughput([&]() {
        counter.fetch_add(1, std::memory_order_relaxed);
    });
    
    EXPECT_GT(throughput, 0.0);
    std::cout << "原子增量吞吐量: " << std::scientific << throughput << " ops/sec" << std::endl;
}

/**
 * 综合性能对比测试
 */
TEST_F(PerformanceOptimizationTest, ComprehensiveComparison) {
    constexpr size_t test_size = 4096;
    
    std::cout << "\n=== 综合性能对比测试 ===" << std::endl;
    
    // 基础 SPSC 队列
    {
        stage2::SPSCRingBuffer<int> queue(test_size);
        
        double latency = measure_latency_ns([&]() {
            static int value = 0;
            if (queue.push(value++)) {
                int item;
                queue.pop(item);
            }
        });
        
        std::cout << "基础 SPSC 队列延迟: " << std::fixed << std::setprecision(2) << latency << " ns" << std::endl;
    }
    
    // 优化后的环形缓冲区
    {
        OptimizedRingBuffer<int, test_size> buffer;
        
        double latency = measure_latency_ns([&]() {
            static int value = 0;
            if (buffer.enqueue(value++)) {
                int item;
                buffer.dequeue(item);
            }
        });
        
        std::cout << "优化环形缓冲区延迟: " << std::fixed << std::setprecision(2) << latency << " ns" << std::endl;
    }
    
    // 性能提升建议
    std::cout << "\n性能优化建议:" << std::endl;
    std::cout << "1. 使用缓存行对齐避免伪共享" << std::endl;
    std::cout << "2. 采用批量操作减少函数调用开销" << std::endl;
    std::cout << "3. 利用内存预取提高缓存命中率" << std::endl;
    std::cout << "4. 选择合适的内存序以平衡性能和正确性" << std::endl;
}
