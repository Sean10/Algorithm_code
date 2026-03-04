#include <gtest/gtest.h>
#include <thread>
#include <vector>
#include <chrono>
#include <atomic>

#include "../../src/stage7_distributed/rabbitmq_client.hpp"
#include "../../src/stage7_distributed/kafka_client.hpp"

using namespace stage7;

class DistributedMessagingTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

/**
 * RabbitMQ 基础功能测试
 */
TEST_F(DistributedMessagingTest, RabbitMQProducerBasicOperations) {
    RabbitMQConfig config;
    config.host = "localhost";
    config.port = 5672;
    config.queue_name = "test_queue";
    
    RabbitMQProducer producer(config);
    
    // 测试连接
    EXPECT_TRUE(producer.connect());
    EXPECT_TRUE(producer.is_connected());
    
    // 测试发布消息
    RabbitMQMessage message("Hello RabbitMQ!", "test_key");
    EXPECT_TRUE(producer.publish(message));
    
    // 测试统计信息
    EXPECT_EQ(producer.get_message_count(), 1);
    
    // 测试断开连接
    producer.disconnect();
    EXPECT_FALSE(producer.is_connected());
}

TEST_F(DistributedMessagingTest, RabbitMQConsumerBasicOperations) {
    RabbitMQConfig config;
    config.queue_name = "test_queue";
    
    RabbitMQConsumer consumer(config);
    
    // 测试连接
    EXPECT_TRUE(consumer.connect());
    EXPECT_TRUE(consumer.is_connected());
    
    std::atomic<int> received_count{0};
    std::vector<std::string> received_messages;
    
    // 设置消息处理器
    consumer.set_message_handler([&](const RabbitMQMessage& message) {
        received_messages.push_back(message.body);
        received_count++;
    });
    
    // 开始消费
    EXPECT_TRUE(consumer.start_consuming());
    EXPECT_TRUE(consumer.is_consuming());
    
    // 等待一些消息
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    // 停止消费
    consumer.stop_consuming();
    EXPECT_FALSE(consumer.is_consuming());
    
    // 验证收到了一些消息（模拟器会生成消息）
    EXPECT_GT(received_count.load(), 0);
    EXPECT_GT(consumer.get_consumed_count(), 0);
}

TEST_F(DistributedMessagingTest, RabbitMQQueueWrapper) {
    RabbitMQConfig config;
    config.queue_name = "wrapper_test_queue";
    
    RabbitMQQueue<int> queue(config);
    
    // 测试连接
    EXPECT_TRUE(queue.connect());
    EXPECT_TRUE(queue.is_connected());
    
    // 测试发送消息
    EXPECT_TRUE(queue.push(42));
    EXPECT_TRUE(queue.push(100));
    
    // 测试批量发送
    std::vector<int> batch_data = {1, 2, 3, 4, 5};
    size_t sent_count = queue.push_batch(batch_data);
    EXPECT_EQ(sent_count, batch_data.size());
    
    std::atomic<int> consumed_count{0};
    std::vector<int> consumed_values;
    
    // 开始消费
    bool consume_started = queue.start_consuming([&](const int& value) {
        consumed_values.push_back(value);
        consumed_count++;
    });
    EXPECT_TRUE(consume_started);
    
    // 等待消费一些消息
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    // 停止消费
    queue.stop_consuming();
    
    // 验证统计信息
    EXPECT_GT(queue.get_published_count(), 0);
    EXPECT_GT(consumed_count.load(), 0);
    
    queue.disconnect();
}

/**
 * Kafka 基础功能测试
 */
TEST_F(DistributedMessagingTest, KafkaProducerBasicOperations) {
    KafkaConfig config;
    config.brokers = "localhost:9092";
    config.default_topic = "test_topic";
    
    KafkaProducer producer(config);
    
    // 测试连接
    EXPECT_TRUE(producer.connect());
    EXPECT_TRUE(producer.is_connected());
    
    // 测试发送消息
    KafkaMessage message("test_topic", "Hello Kafka!", "test_key");
    EXPECT_TRUE(producer.produce(message));
    
    // 测试轮询
    int poll_result = producer.poll(100);
    EXPECT_GE(poll_result, 0);
    
    // 测试刷新
    EXPECT_TRUE(producer.flush(1000));
    
    // 测试统计信息
    EXPECT_EQ(producer.get_message_count(), 1);
    EXPECT_GT(producer.get_bytes_sent(), 0);
    
    producer.disconnect();
    EXPECT_FALSE(producer.is_connected());
}

TEST_F(DistributedMessagingTest, KafkaConsumerBasicOperations) {
    KafkaConfig config;
    config.default_topic = "test_topic";
    config.group_id = "test_group";
    
    KafkaConsumer consumer(config);
    
    // 测试连接
    EXPECT_TRUE(consumer.connect());
    EXPECT_TRUE(consumer.is_connected());
    
    // 测试订阅
    std::vector<std::string> topics = {"test_topic", "another_topic"};
    EXPECT_TRUE(consumer.subscribe(topics));
    
    std::atomic<int> received_count{0};
    
    // 设置消息处理器
    consumer.set_message_handler([&](const KafkaMessage& message) {
        EXPECT_FALSE(message.value.empty());
        received_count++;
    });
    
    // 开始消费
    EXPECT_TRUE(consumer.start_consuming());
    EXPECT_TRUE(consumer.is_consuming());
    
    // 等待一些消息
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    // 测试轮询
    auto messages = consumer.poll(1000);
    // 消息可能为空，这是正常的
    
    // 测试提交
    EXPECT_TRUE(consumer.commit_sync());
    EXPECT_TRUE(consumer.commit_async());
    
    // 停止消费
    consumer.stop_consuming();
    EXPECT_FALSE(consumer.is_consuming());
    
    // 验证收到了一些消息
    EXPECT_GT(received_count.load(), 0);
    EXPECT_GT(consumer.get_consumed_count(), 0);
    
    consumer.disconnect();
}

TEST_F(DistributedMessagingTest, KafkaQueueWrapper) {
    KafkaConfig config;
    config.default_topic = "wrapper_test_topic";
    config.group_id = "wrapper_test_group";
    
    KafkaQueue<int> queue(config);
    
    // 测试连接
    EXPECT_TRUE(queue.connect());
    EXPECT_TRUE(queue.is_connected());
    
    // 测试发送消息
    EXPECT_TRUE(queue.push(42, "key1"));
    EXPECT_TRUE(queue.push(100, "key2"));
    
    // 测试批量发送
    std::vector<int> batch_data = {1, 2, 3, 4, 5};
    size_t sent_count = queue.push_batch(batch_data);
    EXPECT_EQ(sent_count, batch_data.size());
    
    // 刷新缓冲区
    EXPECT_TRUE(queue.flush(5000));
    
    std::atomic<int> consumed_count{0};
    std::vector<int> consumed_values;
    
    // 开始消费
    bool consume_started = queue.start_consuming([&](const int& value) {
        consumed_values.push_back(value);
        consumed_count++;
    });
    EXPECT_TRUE(consume_started);
    
    // 等待消费一些消息
    std::this_thread::sleep_for(std::chrono::seconds(3));
    
    // 提交偏移量
    EXPECT_TRUE(queue.commit());
    
    // 停止消费
    queue.stop_consuming();
    
    // 验证统计信息
    EXPECT_GT(queue.get_produced_count(), 0);
    EXPECT_GT(queue.get_bytes_sent(), 0);
    EXPECT_GT(consumed_count.load(), 0);
    
    queue.disconnect();
}

/**
 * 并发测试
 */
TEST_F(DistributedMessagingTest, RabbitMQConcurrentProducers) {
    RabbitMQConfig config;
    config.queue_name = "concurrent_test_queue";
    
    const int num_producers = 4;
    const int messages_per_producer = 100;
    
    std::vector<std::thread> producers;
    std::atomic<int> total_sent{0};
    
    for (int i = 0; i < num_producers; ++i) {
        producers.emplace_back([&config, &total_sent, messages_per_producer, i]() {
            RabbitMQProducer producer(config);
            EXPECT_TRUE(producer.connect());
            
            for (int j = 0; j < messages_per_producer; ++j) {
                RabbitMQMessage message("Message from producer " + std::to_string(i) + 
                                      ", message " + std::to_string(j));
                if (producer.publish(message)) {
                    total_sent++;
                }
            }
            
            producer.disconnect();
        });
    }
    
    // 等待所有生产者完成
    for (auto& t : producers) {
        t.join();
    }
    
    EXPECT_EQ(total_sent.load(), num_producers * messages_per_producer);
}

TEST_F(DistributedMessagingTest, KafkaConcurrentProducers) {
    KafkaConfig config;
    config.default_topic = "concurrent_kafka_topic";
    
    const int num_producers = 3;
    const int messages_per_producer = 50;
    
    std::vector<std::thread> producers;
    std::atomic<int> total_sent{0};
    
    for (int i = 0; i < num_producers; ++i) {
        producers.emplace_back([&config, &total_sent, messages_per_producer, i]() {
            KafkaProducer producer(config);
            EXPECT_TRUE(producer.connect());
            
            for (int j = 0; j < messages_per_producer; ++j) {
                KafkaMessage message(config.default_topic, 
                                   "Message from producer " + std::to_string(i) + 
                                   ", message " + std::to_string(j),
                                   "key_" + std::to_string(i));
                if (producer.produce(message)) {
                    total_sent++;
                }
            }
            
            producer.flush(5000);
            producer.disconnect();
        });
    }
    
    // 等待所有生产者完成
    for (auto& t : producers) {
        t.join();
    }
    
    EXPECT_EQ(total_sent.load(), num_producers * messages_per_producer);
}

/**
 * 性能测试
 */
TEST_F(DistributedMessagingTest, RabbitMQPerformance) {
    RabbitMQConfig config;
    config.queue_name = "performance_test_queue";
    
    RabbitMQProducer producer(config);
    EXPECT_TRUE(producer.connect());
    
    const int num_messages = 10000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_messages; ++i) {
        RabbitMQMessage message("Performance test message " + std::to_string(i));
        producer.publish(message);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // 计算吞吐量
    double messages_per_second = (double)num_messages / (duration.count() / 1000.0);
    
    // 验证性能（模拟实现应该很快）
    EXPECT_GT(messages_per_second, 1000);  // 期望至少1K msg/s
    EXPECT_EQ(producer.get_message_count(), num_messages);
    
    producer.disconnect();
}

TEST_F(DistributedMessagingTest, KafkaPerformance) {
    KafkaConfig config;
    config.default_topic = "performance_kafka_topic";
    
    KafkaProducer producer(config);
    EXPECT_TRUE(producer.connect());
    
    const int num_messages = 5000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_messages; ++i) {
        KafkaMessage message(config.default_topic, 
                           "Performance test message " + std::to_string(i),
                           "perf_key_" + std::to_string(i % 100));
        producer.produce(message);
    }
    
    producer.flush(10000);
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // 计算吞吐量
    double messages_per_second = (double)num_messages / (duration.count() / 1000.0);
    
    // 验证性能
    EXPECT_GT(messages_per_second, 500);  // 期望至少500 msg/s
    EXPECT_EQ(producer.get_message_count(), num_messages);
    
    producer.disconnect();
}

/**
 * 错误处理测试
 */
TEST_F(DistributedMessagingTest, RabbitMQErrorHandling) {
    RabbitMQConfig config;
    RabbitMQProducer producer(config);
    
    // 测试未连接时发送消息
    RabbitMQMessage message("Test message");
    EXPECT_FALSE(producer.publish(message));
    
    // 连接后应该成功
    EXPECT_TRUE(producer.connect());
    EXPECT_TRUE(producer.publish(message));
    
    producer.disconnect();
}

TEST_F(DistributedMessagingTest, KafkaErrorHandling) {
    KafkaConfig config;
    KafkaProducer producer(config);
    
    // 测试未连接时发送消息
    KafkaMessage message("test_topic", "Test message");
    EXPECT_FALSE(producer.produce(message));
    
    // 连接后应该成功
    EXPECT_TRUE(producer.connect());
    EXPECT_TRUE(producer.produce(message));
    
    producer.disconnect();
}

/**
 * 序列化测试
 */
TEST_F(DistributedMessagingTest, CustomSerialization) {
    struct CustomData {
        int id;
        std::string name;
        double value;
    };
    
    KafkaConfig config;
    config.default_topic = "custom_data_topic";
    
    KafkaQueue<CustomData> queue(config);
    
    // 设置自定义序列化器
    queue.set_serializer(
        [](const CustomData& data) {
            return std::to_string(data.id) + "," + data.name + "," + std::to_string(data.value);
        },
        [](const std::string& str) {
            CustomData data;
            // 简单的解析实现
            size_t pos1 = str.find(',');
            size_t pos2 = str.find(',', pos1 + 1);
            
            if (pos1 != std::string::npos && pos2 != std::string::npos) {
                data.id = std::stoi(str.substr(0, pos1));
                data.name = str.substr(pos1 + 1, pos2 - pos1 - 1);
                data.value = std::stod(str.substr(pos2 + 1));
            }
            
            return data;
        }
    );
    
    EXPECT_TRUE(queue.connect());
    
    // 测试发送自定义数据
    CustomData test_data{42, "test_name", 3.14};
    EXPECT_TRUE(queue.push(test_data, "custom_key"));
    
    queue.disconnect();
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
