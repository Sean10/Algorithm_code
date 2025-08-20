#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include "stage2_spsc/spsc_ring_buffer.hpp"

using namespace stage2;

class SPSCQueueTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 使用2的幂作为容量
        queue = std::make_unique<SPSCRingBuffer<int>>(16);
    }

    std::unique_ptr<SPSCRingBuffer<int>> queue;
};

TEST_F(SPSCQueueTest, BasicOperations) {
    // 测试基本的push和pop操作
    EXPECT_TRUE(queue->empty());
    EXPECT_EQ(queue->size(), 0);

    // 入队
    EXPECT_TRUE(queue->push(42));
    EXPECT_FALSE(queue->empty());
    EXPECT_EQ(queue->size(), 1);

    // 出队
    int value;
    EXPECT_TRUE(queue->pop(value));
    EXPECT_EQ(value, 42);
    EXPECT_TRUE(queue->empty());
    EXPECT_EQ(queue->size(), 0);
}

TEST_F(SPSCQueueTest, CapacityValidation) {
    // 测试非2的幂容量应该抛出异常
    EXPECT_THROW(SPSCRingBuffer<int>(15), std::invalid_argument);
    EXPECT_THROW(SPSCRingBuffer<int>(0), std::invalid_argument);
    
    // 测试2的幂容量应该正常
    EXPECT_NO_THROW(SPSCRingBuffer<int>(1));
    EXPECT_NO_THROW(SPSCRingBuffer<int>(2));
    EXPECT_NO_THROW(SPSCRingBuffer<int>(4));
    EXPECT_NO_THROW(SPSCRingBuffer<int>(8));
}

TEST_F(SPSCQueueTest, CapacityLimits) {
    // 注意：SPSC队列实际可用容量是capacity-1
    const size_t effective_capacity = queue->capacity() - 1;
    
    // 填满队列到有效容量
    for (size_t i = 0; i < effective_capacity; ++i) {
        EXPECT_TRUE(queue->push(static_cast<int>(i))) << "Failed at push " << i;
    }
    
    // 此时应该无法再push
    EXPECT_FALSE(queue->push(999));
    
    // 验证所有元素
    for (size_t i = 0; i < effective_capacity; ++i) {
        int value;
        EXPECT_TRUE(queue->pop(value)) << "Failed at pop " << i;
        EXPECT_EQ(value, static_cast<int>(i));
    }
    
    // 队列应该为空
    EXPECT_TRUE(queue->empty());
    
    // 空队列无法pop
    int dummy;
    EXPECT_FALSE(queue->pop(dummy));
}

TEST_F(SPSCQueueTest, MoveSemantics) {
    // 测试移动语义 - 使用简单类型
    auto queue_string = std::make_unique<SPSCRingBuffer<std::string>>(16);
    
    std::string original = "Hello World";
    std::string copy = original;
    
    // 移动入队
    EXPECT_TRUE(queue_string->push(std::move(copy)));
    
    // 验证原字符串被移动（应该为空或不等于原值）
    EXPECT_TRUE(copy.empty() || copy != original);
    
    // 出队并验证
    std::string result;
    EXPECT_TRUE(queue_string->pop(result));
    EXPECT_EQ(result, original);
}

TEST_F(SPSCQueueTest, SingleProducerSingleConsumer) {
    const int num_items = 1000;
    std::vector<int> consumed;
    std::atomic<bool> producer_done{false};

    // 消费者线程
    std::thread consumer([&]() {
        int value;
        while (!producer_done.load(std::memory_order_acquire) || !queue->empty()) {
            if (queue->pop(value)) {
                consumed.push_back(value);
            } else {
                // 短暂休眠避免空转
                std::this_thread::sleep_for(std::chrono::microseconds(1));
            }
        }
    });

    // 生产者线程
    std::thread producer([&]() {
        for (int i = 0; i < num_items; ++i) {
            // 自旋直到成功push
            while (!queue->push(i)) {
                std::this_thread::sleep_for(std::chrono::microseconds(1));
            }
        }
        producer_done.store(true, std::memory_order_release);
    });

    producer.join();
    consumer.join();

    // 验证结果
    EXPECT_EQ(consumed.size(), num_items);
    for (int i = 0; i < num_items; ++i) {
        EXPECT_EQ(consumed[i], i) << "Mismatch at index " << i;
    }
}

TEST_F(SPSCQueueTest, PerformanceBenchmark) {
    const int num_operations = 100000;
    auto start = std::chrono::high_resolution_clock::now();

    // 注意：这是单线程性能测试，不是真正的SPSC测试
    // 真正的SPSC性能应该在多线程环境下测试
    for (int i = 0; i < num_operations; ++i) {
        while (!queue->push(i)) {
            // 队列满时自旋等待
        }
        int value;
        while (!queue->pop(value)) {
            // 队列空时自旋等待
        }
        EXPECT_EQ(value, i);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "SPSCRingBuffer: " << num_operations << " operations in " 
              << duration.count() << " microseconds" << std::endl;
    std::cout << "Average: " << (duration.count() / (double)num_operations) 
              << " microseconds per operation" << std::endl;
}

TEST_F(SPSCQueueTest, StressTest) {
    // 压力测试：快速的生产者和消费者
    const int num_items = 10000;
    std::atomic<int> total_consumed{0};
    std::atomic<bool> producer_done{false};

    std::thread consumer([&]() {
        int value;
        int local_consumed = 0;
        while (!producer_done.load() || !queue->empty()) {
            if (queue->pop(value)) {
                ++local_consumed;
            }
        }
        total_consumed.store(local_consumed);
    });

    std::thread producer([&]() {
        for (int i = 0; i < num_items; ++i) {
            while (!queue->push(i)) {
                // 继续尝试
            }
        }
        producer_done.store(true);
    });

    producer.join();
    consumer.join();

    EXPECT_EQ(total_consumed.load(), num_items);
}

// 测试内存顺序的正确性（这个测试可能需要运行多次才能发现问题）
TEST_F(SPSCQueueTest, MemoryOrderingCorrectness) {
    const int iterations = 1000;
    
    for (int iter = 0; iter < iterations; ++iter) {
        std::atomic<bool> start{false};
        std::atomic<int> consumer_read{-1};
        
        std::thread producer([&]() {
            while (!start.load()) {
                std::this_thread::yield();
            }
            queue->push(iter);
        });
        
        std::thread consumer([&]() {
            while (!start.load()) {
                std::this_thread::yield();
            }
            int value;
            while (!queue->pop(value)) {
                std::this_thread::yield();
            }
            consumer_read.store(value);
        });
        
        start.store(true);
        producer.join();
        consumer.join();
        
        EXPECT_EQ(consumer_read.load(), iter) << "Memory ordering issue at iteration " << iter;
    }
}
