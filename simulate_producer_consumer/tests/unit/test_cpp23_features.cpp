#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <chrono>
#include <ranges>

#include "../../src/stage6_cpp23/latch_semaphore_queue.hpp"
#include "../../src/stage6_cpp23/ranges_coroutine_queue.hpp"

using namespace stage6;

class Cpp23FeaturesTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

/**
 * 测试 std::latch 和 std::semaphore 队列
 */
TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueueBasicOperations) {
    LatchSemaphoreQueue<int> queue(5);
    
    // 测试基本入队出队
    EXPECT_TRUE(queue.push(42));
    EXPECT_EQ(queue.size(), 1);
    
    int value;
    EXPECT_TRUE(queue.pop(value));
    EXPECT_EQ(value, 42);
    EXPECT_EQ(queue.size(), 0);
}

TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueueTimeout) {
    LatchSemaphoreQueue<int> queue(1);
    
    // 填满队列
    EXPECT_TRUE(queue.push(1));
    
    // 测试超时入队
    auto start = std::chrono::steady_clock::now();
    bool result = queue.push_for(2, std::chrono::milliseconds(100));
    auto duration = std::chrono::steady_clock::now() - start;
    
    EXPECT_FALSE(result);
    EXPECT_GE(duration, std::chrono::milliseconds(90));
    EXPECT_LE(duration, std::chrono::milliseconds(150));
}

TEST_F(Cpp23FeaturesTest, CoordinatedProducerConsumer) {
    const int producer_count = 2;
    const int consumer_count = 2;
    const int items_per_producer = 10;
    
    CoordinatedProducerConsumer coordinator(20, producer_count, consumer_count, items_per_producer);
    
    // 运行协调测试
    auto start = std::chrono::steady_clock::now();
    coordinator.run();
    auto duration = std::chrono::steady_clock::now() - start;
    
    // 验证执行时间合理（应该在几秒内完成）
    EXPECT_LE(duration, std::chrono::seconds(10));
}

/**
 * 测试 Ranges 库优化队列
 */
TEST_F(Cpp23FeaturesTest, RangesOptimizedQueueBasicOperations) {
    RangesOptimizedQueue<int> queue(10);
    
    // 测试基本操作
    EXPECT_TRUE(queue.push(42));
    
    int value;
    EXPECT_TRUE(queue.pop(value));
    EXPECT_EQ(value, 42);
}

TEST_F(Cpp23FeaturesTest, RangesOptimizedQueueBatchOperations) {
    RangesOptimizedQueue<int> queue(20);
    
    // 测试批量入队
    std::vector<int> input_data = {1, 2, 3, 4, 5, -1, 0, 6, 7, 8};
    queue.push_batch(input_data);
    
    // 测试批量出队
    auto result = queue.pop_batch(5);
    
    // 验证结果（经过 ranges 处理：*2 然后过滤 >0）
    // 期望结果：[2, 4, 6, 8, 10] （前5个正数*2）
    EXPECT_EQ(result.size(), 5);
    for (size_t i = 0; i < result.size(); ++i) {
        EXPECT_GT(result[i], 0);
        EXPECT_EQ(result[i] % 2, 0);  // 应该都是偶数
    }
}

TEST_F(Cpp23FeaturesTest, RangesQueueAnalysis) {
    RangesOptimizedQueue<int> queue(10);
    
    // 添加测试数据
    for (int i = 1; i <= 5; ++i) {
        queue.push(i);
    }
    
    // 测试数据分析
    auto [average, count] = queue.analyze_queue_data();
    
    EXPECT_GT(count, 0);
    EXPECT_GT(average, 0);
}

/**
 * 测试协程队列
 */
TEST_F(Cpp23FeaturesTest, CoroutineQueueBasicOperations) {
    CoroutineQueue<int> queue(5);
    
    // 测试同步操作
    EXPECT_TRUE(queue.push(42));
    EXPECT_EQ(queue.size(), 1);
    
    int value;
    EXPECT_TRUE(queue.pop(value));
    EXPECT_EQ(value, 42);
    EXPECT_EQ(queue.size(), 0);
}

/**
 * 测试生成器协程
 */
TEST_F(Cpp23FeaturesTest, FibonacciGenerator) {
    auto fib_gen = fibonacci_generator(10);
    
    std::vector<int> expected = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34};
    std::vector<int> actual;
    
    while (fib_gen.move_next()) {
        actual.push_back(fib_gen.current_value());
    }
    
    EXPECT_EQ(actual.size(), expected.size());
    for (size_t i = 0; i < expected.size(); ++i) {
        EXPECT_EQ(actual[i], expected[i]);
    }
}

/**
 * 测试异步处理管道
 */
TEST_F(Cpp23FeaturesTest, AsyncProcessingPipeline) {
    AsyncProcessingPipeline<int> pipeline(10);
    
    // 启动处理管道（在实际使用中需要协程运行时支持）
    // auto task = pipeline.process_pipeline();
    
    // 测试输入输出
    EXPECT_TRUE(pipeline.push_input(21));
    EXPECT_EQ(pipeline.input_size(), 1);
    
    // 在实际实现中，这里会通过协程处理数据
    // 这里只测试基本的队列功能
}

/**
 * 并发测试
 */
TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueueConcurrency) {
    const int queue_capacity = 100;
    const int num_producers = 4;
    const int num_consumers = 2;
    const int items_per_producer = 250;
    
    LatchSemaphoreQueue<int> queue(queue_capacity);
    std::atomic<int> total_produced{0};
    std::atomic<int> total_consumed{0};
    
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    
    // 创建生产者线程
    for (int i = 0; i < num_producers; ++i) {
        producers.emplace_back([&queue, &total_produced, items_per_producer, i]() {
            for (int j = 0; j < items_per_producer; ++j) {
                int value = i * 1000 + j;
                if (queue.push(value)) {
                    total_produced++;
                }
            }
        });
    }
    
    // 创建消费者线程
    for (int i = 0; i < num_consumers; ++i) {
        consumers.emplace_back([&queue, &total_consumed, items_per_producer, num_producers]() {
            int expected_items = (num_producers * items_per_producer) / 2;  // 每个消费者处理一半
            
            for (int j = 0; j < expected_items; ++j) {
                int value;
                if (queue.pop_for(value, std::chrono::seconds(5))) {
                    total_consumed++;
                }
            }
        });
    }
    
    // 等待所有线程完成
    for (auto& t : producers) {
        t.join();
    }
    for (auto& t : consumers) {
        t.join();
    }
    
    // 验证结果
    int expected_total = num_producers * items_per_producer;
    EXPECT_EQ(total_produced.load(), expected_total);
    EXPECT_EQ(total_consumed.load(), expected_total);
}

/**
 * 性能测试
 */
TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueuePerformance) {
    const int queue_capacity = 1000;
    const int num_operations = 100000;
    
    LatchSemaphoreQueue<int> queue(queue_capacity);
    
    // 测试入队性能
    auto start = std::chrono::high_resolution_clock::now();
    
    std::thread producer([&queue, num_operations]() {
        for (int i = 0; i < num_operations; ++i) {
            queue.push(i);
        }
    });
    
    std::thread consumer([&queue, num_operations]() {
        for (int i = 0; i < num_operations; ++i) {
            int value;
            queue.pop(value);
        }
    });
    
    producer.join();
    consumer.join();
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // 验证性能（应该在合理时间内完成）
    EXPECT_LE(duration.count(), 5000);  // 应该在5秒内完成
    
    // 计算吞吐量
    double ops_per_second = (2.0 * num_operations) / (duration.count() / 1000.0);
    EXPECT_GT(ops_per_second, 10000);  // 期望至少10K ops/s
}

/**
 * 边界条件测试
 */
TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueueEdgeCases) {
    // 测试容量为1的队列
    LatchSemaphoreQueue<int> small_queue(1);
    
    EXPECT_TRUE(small_queue.push(1));
    EXPECT_EQ(small_queue.size(), 1);
    
    // 队列已满，超时入队应该失败
    EXPECT_FALSE(small_queue.push_for(2, std::chrono::milliseconds(10)));
    
    int value;
    EXPECT_TRUE(small_queue.pop(value));
    EXPECT_EQ(value, 1);
    EXPECT_TRUE(small_queue.empty());
    
    // 空队列，超时出队应该失败
    EXPECT_FALSE(small_queue.pop_for(value, std::chrono::milliseconds(10)));
}

/**
 * 异常处理测试
 */
TEST_F(Cpp23FeaturesTest, LatchSemaphoreQueueExceptions) {
    // 测试无效容量
    EXPECT_THROW(LatchSemaphoreQueue<int>(0), std::invalid_argument);
}

/**
 * Ranges 库高级功能测试
 */
TEST_F(Cpp23FeaturesTest, RangesAdvancedFeatures) {
    RangesOptimizedQueue<int> queue(50);
    
    // 创建复杂的测试数据
    std::vector<int> complex_data;
    for (int i = -10; i <= 10; ++i) {
        complex_data.push_back(i);
    }
    
    // 使用 ranges 进行复杂处理
    queue.push_batch(complex_data);
    
    // 获取处理后的数据
    auto processed_data = queue.pop_batch(20);
    
    // 验证所有数据都是正数且为偶数（经过 *2 和 >0 过滤）
    for (const auto& value : processed_data) {
        EXPECT_GT(value, 0);
        EXPECT_EQ(value % 2, 0);
    }
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
