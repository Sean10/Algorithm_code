#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <random>
#include <algorithm>
#include "stage1_basics/mutex_queue.hpp"
#include "stage2_spsc/spsc_ring_buffer.hpp"

using namespace std::chrono_literals;

class ProducerConsumerIntegrationTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 测试开始前的设置
    }
};

// 测试多种队列类型的基本生产者-消费者模式
TEST_F(ProducerConsumerIntegrationTest, BasicProducerConsumer) {
    const int num_items = 1000;
    const int num_producers = 2;
    const int num_consumers = 3;
    
    // 测试互斥锁队列
    {
        stage1::MutexQueue<int> queue(100);
        std::atomic<int> total_produced{0};
        std::atomic<int> total_consumed{0};
        std::vector<std::thread> threads;
        std::atomic<bool> should_stop{false};
        
        // 启动生产者
        for (int p = 0; p < num_producers; ++p) {
            threads.emplace_back([&, p]() {
                for (int i = 0; i < num_items / num_producers; ++i) {
                    int value = p * 10000 + i; // 确保唯一性
                    queue.push(value);
                    total_produced.fetch_add(1);
                }
            });
        }
        
        // 启动消费者
        for (int c = 0; c < num_consumers; ++c) {
            threads.emplace_back([&]() {
                int value;
                while (total_consumed.load() < num_items) {
                    if (queue.pop_for(value, 10ms)) {
                        total_consumed.fetch_add(1);
                    }
                }
            });
        }
        
        // 等待所有线程完成
        for (auto& t : threads) {
            t.join();
        }
        
        EXPECT_EQ(total_produced.load(), num_items);
        EXPECT_EQ(total_consumed.load(), num_items);
    }
}

// 测试SPSC队列在单生产者单消费者场景下的正确性
TEST_F(ProducerConsumerIntegrationTest, SPSCCorrectness) {
    const int num_items = 10000;
    stage2::SPSCRingBuffer<int> queue(1024); // 2的幂
    
    std::vector<int> produced_values;
    std::vector<int> consumed_values;
    std::atomic<bool> producer_done{false};
    
    // 生产者线程
    std::thread producer([&]() {
        for (int i = 0; i < num_items; ++i) {
            produced_values.push_back(i);
            while (!queue.push(i)) {
                std::this_thread::yield();
            }
        }
        producer_done.store(true);
    });
    
    // 消费者线程
    std::thread consumer([&]() {
        int value;
        while (!producer_done.load() || !queue.empty()) {
            if (queue.pop(value)) {
                consumed_values.push_back(value);
            } else {
                std::this_thread::yield();
            }
        }
    });
    
    producer.join();
    consumer.join();
    
    EXPECT_EQ(produced_values.size(), num_items);
    EXPECT_EQ(consumed_values.size(), num_items);
    EXPECT_EQ(produced_values, consumed_values);
}

// 高负载压力测试
TEST_F(ProducerConsumerIntegrationTest, HighLoadStressTest) {
    const int num_items = 5000;
    const int num_producers = 4;
    const int num_consumers = 4;
    
    stage1::MutexQueue<std::pair<int, int>> queue(200);
    std::atomic<int> total_produced{0};
    std::atomic<int> total_consumed{0};
    std::vector<std::thread> threads;
    
    // 生产者：产生带有生产者ID的数据
    for (int p = 0; p < num_producers; ++p) {
        threads.emplace_back([&, p]() {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution<> delay(1, 10);
            
            for (int i = 0; i < num_items / num_producers; ++i) {
                queue.push({p, i});
                total_produced.fetch_add(1);
                
                // 随机延迟模拟真实工作负载
                if (i % 100 == 0) {
                    std::this_thread::sleep_for(std::chrono::microseconds(delay(gen)));
                }
            }
        });
    }
    
    // 消费者：统计每个生产者的数据
    std::vector<std::atomic<int>> per_producer_count(num_producers);
    for (auto& count : per_producer_count) {
        count.store(0);
    }
    
    for (int c = 0; c < num_consumers; ++c) {
        threads.emplace_back([&]() {
            std::pair<int, int> value;
            while (total_consumed.load() < num_items) {
                if (queue.pop_for(value, 50ms)) {
                    total_consumed.fetch_add(1);
                    if (value.first >= 0 && value.first < num_producers) {
                        per_producer_count[value.first].fetch_add(1);
                    }
                }
            }
        });
    }
    
    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }
    
    // 验证结果
    EXPECT_EQ(total_produced.load(), num_items);
    EXPECT_EQ(total_consumed.load(), num_items);
    
    // 验证每个生产者的数据都被正确消费
    for (int p = 0; p < num_producers; ++p) {
        EXPECT_EQ(per_producer_count[p].load(), num_items / num_producers) 
            << "Producer " << p << " data count mismatch";
    }
}

// 测试队列在不同配置下的行为
TEST_F(ProducerConsumerIntegrationTest, VariousConfigurations) {
    struct TestConfig {
        size_t queue_size;
        int num_producers;
        int num_consumers;
        int items_per_producer;
    };
    
    std::vector<TestConfig> configs = {
        {10, 1, 1, 100},    // 小队列，单对单
        {100, 2, 2, 200},   // 中等队列，多对多
        {50, 5, 2, 50},     // 多生产者，少消费者
        {50, 2, 5, 50},     // 少生产者，多消费者
    };
    
    for (const auto& config : configs) {
        stage1::MutexQueue<int> queue(config.queue_size);
        std::atomic<int> total_produced{0};
        std::atomic<int> total_consumed{0};
        std::vector<std::thread> threads;
        
        const int expected_total = config.num_producers * config.items_per_producer;
        
        // 生产者
        for (int p = 0; p < config.num_producers; ++p) {
            threads.emplace_back([&, p, config]() {
                for (int i = 0; i < config.items_per_producer; ++i) {
                    int value = p * 100000 + i;
                    queue.push(value);
                    total_produced.fetch_add(1);
                }
            });
        }
        
        // 消费者
        for (int c = 0; c < config.num_consumers; ++c) {
            threads.emplace_back([&, expected_total]() {
                int value;
                while (total_consumed.load() < expected_total) {
                    if (queue.pop_for(value, 100ms)) {
                        total_consumed.fetch_add(1);
                    }
                }
            });
        }
        
        // 等待完成
        for (auto& t : threads) {
            t.join();
        }
        
        EXPECT_EQ(total_produced.load(), expected_total) 
            << "Config: queue=" << config.queue_size 
            << ", producers=" << config.num_producers 
            << ", consumers=" << config.num_consumers;
            
        EXPECT_EQ(total_consumed.load(), expected_total)
            << "Config: queue=" << config.queue_size 
            << ", producers=" << config.num_producers 
            << ", consumers=" << config.num_consumers;
    }
}

// 测试队列的错误恢复能力
TEST_F(ProducerConsumerIntegrationTest, ErrorRecovery) {
    const int num_items = 1000;
    stage1::MutexQueue<int> queue(50);
    
    std::atomic<int> successful_ops{0};
    std::atomic<int> timeout_ops{0};
    std::atomic<bool> should_stop{false};
    
    // 快速生产者（可能遇到队列满）
    std::thread fast_producer([&]() {
        for (int i = 0; i < num_items; ++i) {
            if (queue.push_for(i, 1ms)) {
                successful_ops.fetch_add(1);
            } else {
                timeout_ops.fetch_add(1);
                // 遇到超时后稍微休息
                std::this_thread::sleep_for(std::chrono::microseconds(100));
                // 重试
                while (!queue.push_for(i, 10ms)) {
                    std::this_thread::sleep_for(std::chrono::microseconds(100));
                }
                successful_ops.fetch_add(1);
            }
        }
        should_stop.store(true);
    });
    
    // 慢消费者
    std::thread slow_consumer([&]() {
        int consumed = 0;
        int value;
        while (!should_stop.load() || !queue.empty()) {
            if (queue.pop_for(value, 10ms)) {
                consumed++;
                // 模拟慢处理
                std::this_thread::sleep_for(std::chrono::microseconds(50));
            }
        }
        EXPECT_EQ(consumed, num_items);
    });
    
    fast_producer.join();
    slow_consumer.join();
    
    EXPECT_EQ(successful_ops.load(), num_items);
    // 应该有一些超时操作（说明错误恢复机制工作了）
    std::cout << "Timeout operations: " << timeout_ops.load() << std::endl;
}
