#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include "stage1_basics/mutex_queue.hpp"

using namespace stage1;

class MutexQueueTest : public ::testing::Test {
protected:
    void SetUp() override {
        queue = std::make_unique<MutexQueue<int>>(10);
    }

    std::unique_ptr<MutexQueue<int>> queue;
};

TEST_F(MutexQueueTest, BasicOperations) {
    // 测试基本的push和pop操作
    EXPECT_TRUE(queue->empty());
    EXPECT_FALSE(queue->full());
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

TEST_F(MutexQueueTest, CapacityLimits) {
    // 填满队列
    for (int i = 0; i < 10; ++i) {
        EXPECT_TRUE(queue->push(i));
    }
    EXPECT_TRUE(queue->full());
    EXPECT_EQ(queue->size(), 10);

    // 验证所有元素
    for (int i = 0; i < 10; ++i) {
        int value;
        EXPECT_TRUE(queue->pop(value));
        EXPECT_EQ(value, i);
    }
    EXPECT_TRUE(queue->empty());
}

TEST_F(MutexQueueTest, TimeoutOperations) {
    // 测试超时操作
    auto start = std::chrono::steady_clock::now();
    
    int value;
    bool result = queue->pop_for(value, std::chrono::milliseconds(100));
    
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    EXPECT_FALSE(result);
    EXPECT_GE(duration.count(), 90); // 允许一些误差
    EXPECT_LE(duration.count(), 150);
}

TEST_F(MutexQueueTest, ProducerConsumerSimple) {
    const int num_items = 100;
    std::vector<int> consumed;
    std::atomic<bool> done{false};

    // 消费者线程
    std::thread consumer([&]() {
        int value;
        while (!done.load() || !queue->empty()) {
            if (queue->pop_for(value, std::chrono::milliseconds(10))) {
                consumed.push_back(value);
            }
        }
    });

    // 生产者线程
    std::thread producer([&]() {
        for (int i = 0; i < num_items; ++i) {
            queue->push(i);
            std::this_thread::sleep_for(std::chrono::microseconds(10));
        }
        done.store(true);
    });

    producer.join();
    consumer.join();

    // 验证结果
    EXPECT_EQ(consumed.size(), num_items);
    for (int i = 0; i < num_items; ++i) {
        EXPECT_EQ(consumed[i], i);
    }
}

TEST_F(MutexQueueTest, MultipleProducersConsumers) {
    const int num_producers = 4;
    const int num_consumers = 2;
    const int items_per_producer = 25;
    const int total_items = num_producers * items_per_producer;
    
    std::atomic<int> produced{0};
    std::atomic<int> consumed{0};
    std::vector<std::thread> threads;

    // 启动生产者
    for (int p = 0; p < num_producers; ++p) {
        threads.emplace_back([&, p]() {
            for (int i = 0; i < items_per_producer; ++i) {
                int value = p * items_per_producer + i;
                queue->push(value);
                produced.fetch_add(1);
            }
        });
    }

    // 启动消费者
    for (int c = 0; c < num_consumers; ++c) {
        threads.emplace_back([&]() {
            int value;
            while (consumed.load() < total_items) {
                if (queue->pop_for(value, std::chrono::milliseconds(10))) {
                    consumed.fetch_add(1);
                }
            }
        });
    }

    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }

    EXPECT_EQ(produced.load(), total_items);
    EXPECT_EQ(consumed.load(), total_items);
    EXPECT_TRUE(queue->empty());
}

TEST_F(MutexQueueTest, ExceptionSafety) {
    // 测试异常安全性
    EXPECT_THROW(MutexQueue<int>(0), std::invalid_argument);
}

// 性能基准测试（简化版）
TEST_F(MutexQueueTest, PerformanceBenchmark) {
    const int num_operations = 10000;
    auto start = std::chrono::high_resolution_clock::now();

    // 简单的push/pop循环
    for (int i = 0; i < num_operations; ++i) {
        queue->push(i);
        int value;
        queue->pop(value);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    // 输出性能信息（仅用于观察）
    std::cout << "MutexQueue: " << num_operations << " operations in " 
              << duration.count() << " microseconds" << std::endl;
    std::cout << "Average: " << (duration.count() / (double)num_operations) 
              << " microseconds per operation" << std::endl;
}
