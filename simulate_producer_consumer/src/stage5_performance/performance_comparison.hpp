#pragma once

#include "performance_optimized_queue.hpp"
#include "../stage2_spsc/spsc_ring_buffer.hpp"
#include "../stage3_mpmc/mpmc_lockfree_queue.hpp"
#include <chrono>
#include <thread>
#include <vector>
#include <iostream>
#include <iomanip>

namespace stage5 {

/**
 * 性能对比测试套件
 * 
 * 比较不同优化级别的队列实现：
 * 1. 基础 SPSC 队列
 * 2. 优化后的高性能队列
 * 3. 不同内存序策略的影响
 * 4. 批量操作 vs 单个操作的性能差异
 */
class PerformanceComparison {
private:
    static constexpr size_t QUEUE_SIZE = 8192;
    static constexpr size_t TEST_OPERATIONS = 1000000;
    static constexpr size_t WARMUP_OPERATIONS = 10000;
    
    struct BenchmarkResult {
        std::string name;
        double avg_latency_ns;
        double throughput_ops_sec;
        double cpu_usage_percent;
        size_t cache_misses;
    };
    
    /**
     * 基准测试框架
     */
    template<typename Queue, typename T>
    BenchmarkResult benchmark_single_threaded(Queue& queue, const std::string& name) {
        BenchmarkResult result;
        result.name = name;
        
        std::vector<T> test_data(TEST_OPERATIONS);
        for (size_t i = 0; i < TEST_OPERATIONS; ++i) {
            test_data[i] = static_cast<T>(i);
        }
        
        // 预热
        for (size_t i = 0; i < WARMUP_OPERATIONS; ++i) {
            T item = static_cast<T>(i);
            queue.enqueue(item);
            T dequeued;
            queue.dequeue(dequeued);
        }
        
        // 测量入队延迟
        auto enqueue_start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < TEST_OPERATIONS; ++i) {
            while (!queue.enqueue(test_data[i])) {
                std::this_thread::yield();
            }
        }
        
        auto enqueue_end = std::chrono::high_resolution_clock::now();
        
        // 测量出队延迟
        auto dequeue_start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < TEST_OPERATIONS; ++i) {
            T item;
            while (!queue.dequeue(item)) {
                std::this_thread::yield();
            }
        }
        
        auto dequeue_end = std::chrono::high_resolution_clock::now();
        
        // 计算结果
        auto enqueue_duration = std::chrono::duration_cast<std::chrono::nanoseconds>(
            enqueue_end - enqueue_start);
        auto dequeue_duration = std::chrono::duration_cast<std::chrono::nanoseconds>(
            dequeue_end - dequeue_start);
        
        result.avg_latency_ns = static_cast<double>(enqueue_duration.count() + dequeue_duration.count()) 
                               / (2 * TEST_OPERATIONS);
        result.throughput_ops_sec = (2.0 * TEST_OPERATIONS * 1000000000.0) / 
                                   (enqueue_duration.count() + dequeue_duration.count());
        result.cpu_usage_percent = 0.0;  // 简化，实际需要系统调用获取
        result.cache_misses = 0;         // 简化，实际需要性能计数器
        
        return result;
    }
    
    /**
     * 多线程基准测试
     */
    template<typename Queue, typename T>
    BenchmarkResult benchmark_multi_threaded(Queue& queue, const std::string& name,
                                            size_t producer_count, size_t consumer_count) {
        BenchmarkResult result;
        result.name = name + " (MT)";
        
        std::atomic<bool> start_flag{false};
        std::atomic<bool> stop_flag{false};
        std::atomic<size_t> total_produced{0};
        std::atomic<size_t> total_consumed{0};
        
        // 启动生产者线程
        std::vector<std::thread> producers;
        for (size_t i = 0; i < producer_count; ++i) {
            producers.emplace_back([&, i]() {
                while (!start_flag.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }
                
                size_t produced = 0;
                T item = static_cast<T>(i);
                
                while (!stop_flag.load(std::memory_order_acquire) && 
                       produced < TEST_OPERATIONS / producer_count) {
                    if (queue.enqueue(item)) {
                        ++produced;
                        item = static_cast<T>(i * TEST_OPERATIONS + produced);
                    } else {
                        std::this_thread::yield();
                    }
                }
                
                total_produced.fetch_add(produced, std::memory_order_relaxed);
            });
        }
        
        // 启动消费者线程
        std::vector<std::thread> consumers;
        for (size_t i = 0; i < consumer_count; ++i) {
            consumers.emplace_back([&]() {
                while (!start_flag.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }
                
                size_t consumed = 0;
                T item;
                
                while (!stop_flag.load(std::memory_order_acquire) || !queue.empty()) {
                    if (queue.dequeue(item)) {
                        ++consumed;
                    } else {
                        std::this_thread::yield();
                    }
                }
                
                total_consumed.fetch_add(consumed, std::memory_order_relaxed);
            });
        }
        
        // 开始测试
        auto start_time = std::chrono::high_resolution_clock::now();
        start_flag.store(true, std::memory_order_release);
        
        // 运行指定时间
        std::this_thread::sleep_for(std::chrono::seconds(5));
        
        stop_flag.store(true, std::memory_order_release);
        auto end_time = std::chrono::high_resolution_clock::now();
        
        // 等待所有线程结束
        for (auto& t : producers) t.join();
        for (auto& t : consumers) t.join();
        
        // 计算结果
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end_time - start_time);
        
        size_t total_ops = total_produced.load() + total_consumed.load();
        result.throughput_ops_sec = (total_ops * 1000000.0) / duration.count();
        result.avg_latency_ns = (duration.count() * 1000.0) / total_ops;
        result.cpu_usage_percent = 0.0;
        result.cache_misses = 0;
        
        return result;
    }
    
    void print_result(const BenchmarkResult& result) {
        std::cout << std::left << std::setw(25) << result.name 
                  << std::right << std::setw(12) << std::fixed << std::setprecision(2) 
                  << result.avg_latency_ns << " ns"
                  << std::setw(15) << std::scientific << std::setprecision(2) 
                  << result.throughput_ops_sec << " ops/s" 
                  << std::endl;
    }

public:
    /**
     * 运行完整的性能对比测试
     */
    void run_comprehensive_benchmark() {
        std::cout << "\n=== 性能对比测试 ===\n" << std::endl;
        std::cout << std::left << std::setw(25) << "队列类型" 
                  << std::right << std::setw(15) << "平均延迟" 
                  << std::setw(20) << "吞吐量" << std::endl;
        std::cout << std::string(60, '-') << std::endl;
        
        // 测试1：基础 SPSC 队列
        {
            stage2::SPSCRingBuffer<int> queue(QUEUE_SIZE);
            auto result = benchmark_single_threaded<stage2::SPSCRingBuffer<int>, int>(
                queue, "基础 SPSC 队列");
            print_result(result);
        }
        
        // 测试2：高性能优化队列
        {
            OptimizedRingBuffer<int, QUEUE_SIZE> queue;
            auto result = benchmark_single_threaded<OptimizedRingBuffer<int, QUEUE_SIZE>, int>(
                queue, "高性能优化队列");
            print_result(result);
        }
        
        // 测试3：批量操作性能
        test_batch_operations();
        
        // 测试4：内存序对性能的影响
        test_memory_ordering_impact();
        
        // 测试5：缓存行对齐的影响
        test_cache_alignment_impact();
        
        std::cout << std::endl;
    }
    
    /**
     * 测试批量操作的性能优势
     */
    void test_batch_operations() {
        std::cout << "\n--- 批量操作性能测试 ---" << std::endl;
        
        OptimizedRingBuffer<int, QUEUE_SIZE> queue;
        constexpr size_t BATCH_SIZE = 64;
        constexpr size_t BATCH_COUNT = TEST_OPERATIONS / BATCH_SIZE;
        
        std::vector<int> batch_data(BATCH_SIZE);
        for (size_t i = 0; i < BATCH_SIZE; ++i) {
            batch_data[i] = static_cast<int>(i);
        }
        
        // 测试单个操作
        auto single_start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < TEST_OPERATIONS; ++i) {
            while (!queue.enqueue(static_cast<int>(i))) {
                std::this_thread::yield();
            }
        }
        
        for (size_t i = 0; i < TEST_OPERATIONS; ++i) {
            int item;
            while (!queue.dequeue(item)) {
                std::this_thread::yield();
            }
        }
        auto single_end = std::chrono::high_resolution_clock::now();
        
        // 测试批量操作
        auto batch_start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < BATCH_COUNT; ++i) {
            while (queue.enqueue_batch(batch_data.data(), BATCH_SIZE) != BATCH_SIZE) {
                std::this_thread::yield();
            }
        }
        
        std::vector<int> dequeued_batch(BATCH_SIZE);
        for (size_t i = 0; i < BATCH_COUNT; ++i) {
            while (queue.dequeue_batch(dequeued_batch.data(), BATCH_SIZE) != BATCH_SIZE) {
                std::this_thread::yield();
            }
        }
        auto batch_end = std::chrono::high_resolution_clock::now();
        
        auto single_duration = std::chrono::duration_cast<std::chrono::microseconds>(
            single_end - single_start);
        auto batch_duration = std::chrono::duration_cast<std::chrono::microseconds>(
            batch_end - batch_start);
        
        double improvement = static_cast<double>(single_duration.count()) / batch_duration.count();
        
        std::cout << "单个操作时间: " << single_duration.count() << " μs" << std::endl;
        std::cout << "批量操作时间: " << batch_duration.count() << " μs" << std::endl;
        std::cout << "性能提升倍数: " << std::fixed << std::setprecision(2) << improvement << "x" << std::endl;
    }
    
    /**
     * 测试不同内存序对性能的影响
     */
    void test_memory_ordering_impact() {
        std::cout << "\n--- 内存序性能影响测试 ---" << std::endl;
        
        // 这里可以测试不同内存序的性能差异
        // 实际实现中需要创建使用不同内存序的队列版本
        
        std::cout << "seq_cst vs acquire-release vs relaxed 的性能对比：" << std::endl;
        std::cout << "- seq_cst: 最安全但性能最低" << std::endl;
        std::cout << "- acquire-release: 平衡安全性和性能" << std::endl;
        std::cout << "- relaxed: 最高性能但需要小心使用" << std::endl;
    }
    
    /**
     * 测试缓存行对齐的性能影响
     */
    void test_cache_alignment_impact() {
        std::cout << "\n--- 缓存行对齐性能影响测试 ---" << std::endl;
        
        // 模拟伪共享情况
        struct UnalignedCounters {
            std::atomic<size_t> counter1{0};
            std::atomic<size_t> counter2{0};
        };
        
        struct AlignedCounters {
            alignas(64) std::atomic<size_t> counter1{0};
            alignas(64) std::atomic<size_t> counter2{0};
        };
        
        constexpr size_t ITERATIONS = 1000000;
        
        // 测试未对齐的情况（可能发生伪共享）
        UnalignedCounters unaligned;
        auto unaligned_start = std::chrono::high_resolution_clock::now();
        
        std::thread t1([&]() {
            for (size_t i = 0; i < ITERATIONS; ++i) {
                unaligned.counter1.fetch_add(1, std::memory_order_relaxed);
            }
        });
        
        std::thread t2([&]() {
            for (size_t i = 0; i < ITERATIONS; ++i) {
                unaligned.counter2.fetch_add(1, std::memory_order_relaxed);
            }
        });
        
        t1.join();
        t2.join();
        
        auto unaligned_end = std::chrono::high_resolution_clock::now();
        
        // 测试对齐的情况（避免伪共享）
        AlignedCounters aligned;
        auto aligned_start = std::chrono::high_resolution_clock::now();
        
        std::thread t3([&]() {
            for (size_t i = 0; i < ITERATIONS; ++i) {
                aligned.counter1.fetch_add(1, std::memory_order_relaxed);
            }
        });
        
        std::thread t4([&]() {
            for (size_t i = 0; i < ITERATIONS; ++i) {
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
        
        double improvement = static_cast<double>(unaligned_duration.count()) / aligned_duration.count();
        
        std::cout << "未对齐计数器: " << unaligned_duration.count() << " μs" << std::endl;
        std::cout << "缓存行对齐计数器: " << aligned_duration.count() << " μs" << std::endl;
        std::cout << "对齐优化提升: " << std::fixed << std::setprecision(2) << improvement << "x" << std::endl;
    }
    
    /**
     * 输出性能调优建议
     */
    void print_performance_tips() {
        std::cout << "\n=== 性能优化建议 ===" << std::endl;
        std::cout << "1. 缓存行对齐：避免伪共享，提升多线程性能" << std::endl;
        std::cout << "2. 批量操作：减少系统调用开销，提高吞吐量" << std::endl;
        std::cout << "3. 内存预取：预先加载数据到缓存，减少延迟" << std::endl;
        std::cout << "4. NUMA 感知：在正确的内存节点分配数据" << std::endl;
        std::cout << "5. 内存序优化：使用最小必要的内存序" << std::endl;
        std::cout << "6. 数据局部性：保持相关数据在空间和时间上的局部性" << std::endl;
        std::cout << "7. 避免锁竞争：使用无锁算法或减少锁粒度" << std::endl;
        std::cout << "8. CPU 亲和性：绑定线程到特定 CPU 核心" << std::endl;
    }
};

/**
 * 便利函数：运行所有性能测试
 */
inline void run_all_performance_tests() {
    PerformanceComparison comparison;
    comparison.run_comprehensive_benchmark();
    comparison.print_performance_tips();
    
    // 运行系统级性能分析
    PerformanceTuner::analyze_cache_performance();
}

} // namespace stage5
