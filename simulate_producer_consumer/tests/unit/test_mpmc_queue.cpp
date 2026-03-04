#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <random>

#include "../../src/stage3_mpmc/mpmc_lockfree_queue.hpp"
#include "../../src/stage3_mpmc/aba_safe_queue.hpp"
#include "../../src/stage3_mpmc/michael_scott_queue.hpp"

using namespace stage3;

/**
 * Stage3 MPMC 队列单元测试
 * 
 * 测试内容：
 * 1. 基本功能测试（入队、出队、边界条件）
 * 2. 并发安全性测试
 * 3. ABA 问题解决方案测试
 * 4. Michael-Scott 队列测试
 * 5. 性能基准测试
 */

class MPMCQueueTest : public ::testing::Test {
protected:
    static constexpr size_t TEST_QUEUE_SIZE = 1024;
    static constexpr size_t STRESS_TEST_OPERATIONS = 10000;
    static constexpr size_t THREAD_COUNT = 4;
    
    void SetUp() override {
        // 在每个测试前执行的设置
    }
    
    void TearDown() override {
        // 在每个测试后执行的清理
    }
};

/**
 * 基础 MPMC 队列功能测试
 */
TEST_F(MPMCQueueTest, BasicOperations) {
    LockFreeArrayQueue<int> queue(TEST_QUEUE_SIZE);
    
    // 测试空队列
    EXPECT_TRUE(queue.empty());
    EXPECT_EQ(queue.size(), 0);
    EXPECT_EQ(queue.capacity(), TEST_QUEUE_SIZE);
    
    // 测试入队
    for (int i = 0; i < 100; ++i) {
        EXPECT_TRUE(queue.enqueue(i));
        EXPECT_EQ(queue.size(), i + 1);
    }
    
    EXPECT_FALSE(queue.empty());
    
    // 测试出队
    for (int i = 0; i < 100; ++i) {
        int item;
        EXPECT_TRUE(queue.dequeue(item));
        EXPECT_EQ(item, i);
        EXPECT_EQ(queue.size(), 100 - i - 1);
    }
    
    EXPECT_TRUE(queue.empty());
    
    // 测试空队列出队
    int item;
    EXPECT_FALSE(queue.dequeue(item));
}

TEST_F(MPMCQueueTest, QueueFull) {
    LockFreeArrayQueue<int> queue(4);  // 小队列测试边界
    
    // 填满队列
    for (int i = 0; i < 4; ++i) {
        EXPECT_TRUE(queue.enqueue(i));
    }
    
    // 尝试再次入队应该失败
    EXPECT_FALSE(queue.enqueue(999));
    
    // 出队一个元素后应该能再次入队
    int item;
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 0);
    EXPECT_TRUE(queue.enqueue(999));
    
    // 验证队列内容
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 1);
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 2);
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 3);
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 999);
    
    EXPECT_TRUE(queue.empty());
}

TEST_F(MPMCQueueTest, MoveSemantics) {
    LockFreeArrayQueue<std::unique_ptr<int>> queue(TEST_QUEUE_SIZE);
    
    // 测试移动语义入队
    auto ptr1 = std::make_unique<int>(42);
    auto* raw_ptr = ptr1.get();
    EXPECT_TRUE(queue.enqueue(std::move(ptr1)));
    EXPECT_EQ(ptr1.get(), nullptr);  // 移动后应该为空
    
    // 测试出队
    std::unique_ptr<int> ptr2;
    EXPECT_TRUE(queue.dequeue(ptr2));
    EXPECT_NE(ptr2.get(), nullptr);
    EXPECT_EQ(ptr2.get(), raw_ptr);
    EXPECT_EQ(*ptr2, 42);
}

/**
 * 并发安全性测试
 */
TEST_F(MPMCQueueTest, ConcurrentProducerConsumer) {
    LockFreeArrayQueue<int> queue(TEST_QUEUE_SIZE);
    
    std::atomic<bool> start_flag{false};
    std::atomic<bool> stop_flag{false};
    std::atomic<int> total_produced{0};
    std::atomic<int> total_consumed{0};
    
    const int operations_per_thread = STRESS_TEST_OPERATIONS / THREAD_COUNT;
    
    // 启动生产者线程
    std::vector<std::thread> producers;
    for (size_t i = 0; i < THREAD_COUNT; ++i) {
        producers.emplace_back([&, i]() {
            while (!start_flag.load()) {
                std::this_thread::yield();
            }
            
            int produced = 0;
            for (int j = 0; j < operations_per_thread; ++j) {
                int value = i * operations_per_thread + j;
                while (!queue.enqueue(value) && !stop_flag.load()) {
                    std::this_thread::yield();
                }
                if (!stop_flag.load()) {
                    ++produced;
                }
            }
            
            total_produced.fetch_add(produced);
        });
    }
    
    // 启动消费者线程
    std::vector<std::thread> consumers;
    std::vector<std::vector<int>> consumed_values(THREAD_COUNT);
    
    for (size_t i = 0; i < THREAD_COUNT; ++i) {
        consumers.emplace_back([&, i]() {
            while (!start_flag.load()) {
                std::this_thread::yield();
            }
            
            int consumed = 0;
            int value;
            
            while (consumed < operations_per_thread) {
                if (queue.dequeue(value)) {
                    consumed_values[i].push_back(value);
                    ++consumed;
                } else {
                    std::this_thread::yield();
                }
            }
            
            total_consumed.fetch_add(consumed);
        });
    }
    
    // 开始测试
    start_flag.store(true);
    
    // 等待所有线程完成
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    // 验证结果
    EXPECT_EQ(total_produced.load(), STRESS_TEST_OPERATIONS);
    EXPECT_EQ(total_consumed.load(), STRESS_TEST_OPERATIONS);
    
    // 验证所有值都被正确消费
    std::vector<bool> value_seen(STRESS_TEST_OPERATIONS, false);
    for (const auto& thread_values : consumed_values) {
        for (int value : thread_values) {
            EXPECT_GE(value, 0);
            EXPECT_LT(value, STRESS_TEST_OPERATIONS);
            EXPECT_FALSE(value_seen[value]) << "Value " << value << " consumed multiple times";
            value_seen[value] = true;
        }
    }
    
    // 确保所有值都被消费
    for (size_t i = 0; i < STRESS_TEST_OPERATIONS; ++i) {
        EXPECT_TRUE(value_seen[i]) << "Value " << i << " was not consumed";
    }
}

/**
 * ABA 安全队列测试
 */
TEST_F(MPMCQueueTest, ABASafeQueue) {
    ABASafeQueue<int> queue(TEST_QUEUE_SIZE);
    
    // 基本功能测试
    EXPECT_TRUE(queue.empty());
    
    // 版本号应该随操作递增
    size_t initial_head_version = queue.head_version();
    size_t initial_tail_version = queue.tail_version();
    
    // 入队操作应该增加尾指针版本号
    EXPECT_TRUE(queue.enqueue(42));
    EXPECT_GT(queue.tail_version(), initial_tail_version);
    
    // 出队操作应该增加头指针版本号
    int item;
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 42);
    EXPECT_GT(queue.head_version(), initial_head_version);
}

TEST_F(MPMCQueueTest, ABASafeQueueStressTest) {
    ABASafeQueue<int> queue(256);  // 较小的队列增加竞争
    
    std::atomic<int> total_enqueued{0};
    std::atomic<int> total_dequeued{0};
    
    const int operations_per_thread = 1000;
    const int thread_count = 8;
    
    std::vector<std::thread> threads;
    
    // 启动混合的生产者/消费者线程
    for (int i = 0; i < thread_count; ++i) {
        threads.emplace_back([&, i]() {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution<> dis(0, 1);
            
            int enqueued = 0, dequeued = 0;
            
            for (int j = 0; j < operations_per_thread; ++j) {
                if (dis(gen) == 0 || dequeued >= enqueued) {
                    // 尝试入队
                    int value = i * operations_per_thread + j;
                    if (queue.enqueue(value)) {
                        ++enqueued;
                    }
                } else {
                    // 尝试出队
                    int item;
                    if (queue.dequeue(item)) {
                        ++dequeued;
                    }
                }
            }
            
            total_enqueued.fetch_add(enqueued);
            total_dequeued.fetch_add(dequeued);
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    // 消费剩余的元素
    int remaining = 0;
    int item;
    while (queue.dequeue(item)) {
        ++remaining;
    }
    
    total_dequeued.fetch_add(remaining);
    
    EXPECT_EQ(total_enqueued.load(), total_dequeued.load());
    EXPECT_TRUE(queue.empty());
}

/**
 * Michael-Scott 队列测试
 */
TEST_F(MPMCQueueTest, MichaelScottQueueBasic) {
    MichaelScottQueue<int> queue;
    
    // 测试空队列
    EXPECT_TRUE(queue.empty());
    
    int item;
    EXPECT_FALSE(queue.dequeue(item));
    
    // 测试入队出队
    queue.enqueue(1);
    queue.enqueue(2);
    queue.enqueue(3);
    
    EXPECT_FALSE(queue.empty());
    EXPECT_EQ(queue.size(), 3);
    
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 1);
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 2);
    EXPECT_TRUE(queue.dequeue(item));
    EXPECT_EQ(item, 3);
    
    EXPECT_TRUE(queue.empty());
    EXPECT_EQ(queue.size(), 0);
}

TEST_F(MPMCQueueTest, MichaelScottQueueConcurrent) {
    MichaelScottQueue<int> queue;
    
    const int thread_count = 4;
    const int operations_per_thread = 1000;
    
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    std::atomic<int> total_consumed{0};
    std::vector<std::vector<int>> consumed_values(thread_count);
    
    // 生产者线程
    for (int i = 0; i < thread_count; ++i) {
        producers.emplace_back([&, i]() {
            for (int j = 0; j < operations_per_thread; ++j) {
                int value = i * operations_per_thread + j;
                queue.enqueue(value);
            }
        });
    }
    
    // 消费者线程
    for (int i = 0; i < thread_count; ++i) {
        consumers.emplace_back([&, i]() {
            int consumed = 0;
            int value;
            
            while (consumed < operations_per_thread) {
                if (queue.dequeue(value)) {
                    consumed_values[i].push_back(value);
                    ++consumed;
                } else {
                    std::this_thread::yield();
                }
            }
            
            total_consumed.fetch_add(consumed);
        });
    }
    
    // 等待所有线程完成
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    // 验证结果
    const int total_expected = thread_count * operations_per_thread;
    EXPECT_EQ(total_consumed.load(), total_expected);
    EXPECT_TRUE(queue.empty());
    
    // 验证所有值都被正确消费
    std::vector<bool> value_seen(total_expected, false);
    for (const auto& thread_values : consumed_values) {
        for (int value : thread_values) {
            EXPECT_GE(value, 0);
            EXPECT_LT(value, total_expected);
            EXPECT_FALSE(value_seen[value]) << "Value " << value << " consumed multiple times";
            value_seen[value] = true;
        }
    }
    
    for (size_t i = 0; i < total_expected; ++i) {
        EXPECT_TRUE(value_seen[i]) << "Value " << i << " was not consumed";
    }
}

/**
 * 优化版本测试
 */
TEST_F(MPMCQueueTest, OptimizedMichaelScottQueue) {
    OptimizedMichaelScottQueue<int> queue;
    
    // 基本功能测试
    EXPECT_TRUE(queue.empty());
    
    for (int i = 0; i < 100; ++i) {
        queue.enqueue(i);
    }
    
    EXPECT_FALSE(queue.empty());
    
    for (int i = 0; i < 100; ++i) {
        int item;
        EXPECT_TRUE(queue.dequeue(item));
        EXPECT_EQ(item, i);
    }
    
    EXPECT_TRUE(queue.empty());
}

/**
 * 性能对比测试
 */
TEST_F(MPMCQueueTest, PerformanceComparison) {
    const int operations = 10000;
    
    // 基础队列性能
    {
        LockFreeArrayQueue<int> queue(TEST_QUEUE_SIZE);
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < operations; ++i) {
            while (!queue.enqueue(i)) {
                // 重试直到成功
            }
        }
        
        for (int i = 0; i < operations; ++i) {
            int item;
            while (!queue.dequeue(item)) {
                // 重试直到成功
            }
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "基础 MPMC 队列: " << duration.count() << " μs" << std::endl;
    }
    
    // Michael-Scott 队列性能
    {
        MichaelScottQueue<int> queue;
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < operations; ++i) {
            queue.enqueue(i);
        }
        
        for (int i = 0; i < operations; ++i) {
            int item;
            while (!queue.dequeue(item)) {
                // 重试直到成功
            }
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Michael-Scott 队列: " << duration.count() << " μs" << std::endl;
    }
}

// 运行所有测试的入口点
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
