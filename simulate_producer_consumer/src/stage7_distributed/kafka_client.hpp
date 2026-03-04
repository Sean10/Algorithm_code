#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <chrono>
#include <thread>
#include <atomic>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <unordered_map>

namespace stage7 {

/**
 * Kafka 消息结构
 */
struct KafkaMessage {
    std::string topic;
    int32_t partition = -1;  // -1 表示自动分区
    std::string key;
    std::string value;
    std::chrono::system_clock::time_point timestamp;
    int64_t offset = -1;
    
    KafkaMessage() : timestamp(std::chrono::system_clock::now()) {}
    
    KafkaMessage(const std::string& topic_name, const std::string& msg_value, 
                const std::string& msg_key = "")
        : topic(topic_name), key(msg_key), value(msg_value), 
          timestamp(std::chrono::system_clock::now()) {}
};

/**
 * Kafka 配置
 */
struct KafkaConfig {
    std::string brokers = "localhost:9092";
    std::string group_id = "producer_consumer_group";
    std::string client_id = "cpp_client";
    
    // 生产者配置
    std::string acks = "1";  // 0, 1, all
    int32_t retries = 3;
    int32_t batch_size = 16384;
    int32_t linger_ms = 5;
    std::string compression_type = "none";  // none, gzip, snappy, lz4
    
    // 消费者配置
    std::string auto_offset_reset = "earliest";  // earliest, latest
    bool enable_auto_commit = true;
    int32_t auto_commit_interval_ms = 5000;
    int32_t session_timeout_ms = 30000;
    int32_t max_poll_records = 500;
    
    // 主题配置
    std::string default_topic = "producer_consumer_topic";
    int32_t num_partitions = 3;
    int16_t replication_factor = 1;
};

/**
 * Kafka 生产者客户端（模拟实现）
 * 
 * 注意：这是一个模拟实现，展示了如何集成 Kafka 的概念。
 * 在实际项目中，你需要链接真实的 Kafka C++ 客户端库，如：
 * - librdkafka (RdKafka)
 * - cppkafka
 */
class KafkaProducer {
private:
    KafkaConfig config_;
    std::atomic<bool> connected_{false};
    std::atomic<uint64_t> message_count_{0};
    std::atomic<uint64_t> bytes_sent_{0};
    
    // 模拟分区器
    mutable std::mutex partition_mutex_;
    std::unordered_map<std::string, int32_t> topic_partitions_;

public:
    explicit KafkaProducer(const KafkaConfig& config) : config_(config) {}

    /**
     * 连接到 Kafka 集群
     */
    bool connect() {
        if (connected_) {
            return true;
        }
        
        // 模拟连接过程
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        
        // 在实际实现中，这里会：
        // 1. 创建 RdKafka::Producer
        // 2. 设置配置参数
        // 3. 获取元数据信息
        // 4. 创建主题（如果不存在）
        
        // 模拟获取主题分区信息
        {
            std::lock_guard<std::mutex> lock(partition_mutex_);
            topic_partitions_[config_.default_topic] = config_.num_partitions;
        }
        
        connected_ = true;
        return true;
    }

    /**
     * 断开连接
     */
    void disconnect() {
        if (!connected_) {
            return;
        }
        
        // 在实际实现中，这里会调用 producer->flush() 和 delete producer
        flush();
        connected_ = false;
    }

    /**
     * 发送消息
     */
    bool produce(const KafkaMessage& message) {
        if (!connected_) {
            return false;
        }

        // 模拟分区选择
        int32_t partition = select_partition(message.topic, message.key);
        
        // 模拟消息发送
        std::this_thread::sleep_for(std::chrono::microseconds(50));
        
        // 在实际实现中，这里会：
        // RdKafka::ErrorCode err = producer->produce(
        //     topic, partition, RdKafka::Producer::RK_MSG_COPY,
        //     const_cast<char*>(message.value.data()), message.value.size(),
        //     message.key.empty() ? nullptr : &message.key, nullptr);
        
        message_count_++;
        bytes_sent_ += message.value.size();
        
        return true;
    }

    /**
     * 异步发送消息（带回调）
     */
    bool produce_async(const KafkaMessage& message, 
                      std::function<void(bool success, const std::string& error)> callback) {
        // 在实际实现中，这里会设置 delivery report callback
        bool success = produce(message);
        
        // 模拟异步回调
        std::thread([callback, success]() {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            callback(success, success ? "" : "Send failed");
        }).detach();
        
        return success;
    }

    /**
     * 批量发送消息
     */
    size_t produce_batch(const std::vector<KafkaMessage>& messages) {
        size_t sent_count = 0;
        
        for (const auto& message : messages) {
            if (produce(message)) {
                sent_count++;
            } else {
                break;
            }
        }
        
        // 触发批量发送
        poll(0);
        
        return sent_count;
    }

    /**
     * 轮询事件（处理回调）
     */
    int poll(int timeout_ms) {
        // 在实际实现中，这里会调用 producer->poll(timeout_ms)
        if (timeout_ms > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(timeout_ms));
        }
        return 0;
    }

    /**
     * 刷新缓冲区
     */
    bool flush(int timeout_ms = 10000) {
        // 在实际实现中，这里会调用 producer->flush(timeout_ms)
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        return true;
    }

    /**
     * 获取统计信息
     */
    uint64_t get_message_count() const {
        return message_count_;
    }

    uint64_t get_bytes_sent() const {
        return bytes_sent_;
    }

    bool is_connected() const {
        return connected_;
    }

private:
    /**
     * 分区选择器
     */
    int32_t select_partition(const std::string& topic, const std::string& key) {
        std::lock_guard<std::mutex> lock(partition_mutex_);
        
        auto it = topic_partitions_.find(topic);
        if (it == topic_partitions_.end()) {
            return 0;
        }
        
        int32_t num_partitions = it->second;
        
        if (key.empty()) {
            // 轮询分区
            static thread_local int32_t round_robin_counter = 0;
            return (round_robin_counter++) % num_partitions;
        } else {
            // 基于 key 的哈希分区
            std::hash<std::string> hasher;
            return hasher(key) % num_partitions;
        }
    }
};

/**
 * Kafka 消费者客户端（模拟实现）
 */
class KafkaConsumer {
private:
    KafkaConfig config_;
    std::atomic<bool> connected_{false};
    std::atomic<bool> consuming_{false};
    std::atomic<uint64_t> consumed_count_{0};
    std::atomic<uint64_t> bytes_received_{0};
    
    // 订阅的主题
    std::vector<std::string> subscribed_topics_;
    
    // 模拟消息队列
    std::queue<KafkaMessage> message_queue_;
    std::mutex queue_mutex_;
    std::condition_variable queue_cv_;
    
    // 消费者线程
    std::thread consumer_thread_;
    
    // 消息处理回调
    std::function<void(const KafkaMessage&)> message_handler_;
    
    // 偏移量管理
    std::unordered_map<std::string, int64_t> topic_offsets_;
    std::mutex offset_mutex_;

public:
    explicit KafkaConsumer(const KafkaConfig& config) : config_(config) {}

    ~KafkaConsumer() {
        stop_consuming();
        disconnect();
    }

    /**
     * 连接到 Kafka 集群
     */
    bool connect() {
        if (connected_) {
            return true;
        }
        
        // 模拟连接过程
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        
        // 在实际实现中，这里会：
        // 1. 创建 RdKafka::KafkaConsumer
        // 2. 设置配置参数
        // 3. 设置 rebalance callback
        
        connected_ = true;
        return true;
    }

    /**
     * 断开连接
     */
    void disconnect() {
        stop_consuming();
        
        if (connected_) {
            // 在实际实现中，这里会调用 consumer->close() 和 delete consumer
            connected_ = false;
        }
    }

    /**
     * 订阅主题
     */
    bool subscribe(const std::vector<std::string>& topics) {
        if (!connected_) {
            return false;
        }
        
        subscribed_topics_ = topics;
        
        // 在实际实现中，这里会调用 consumer->subscribe(topics)
        
        // 启动模拟消息生成器（在实际实现中不需要）
        start_message_simulator();
        
        return true;
    }

    /**
     * 设置消息处理器
     */
    void set_message_handler(std::function<void(const KafkaMessage&)> handler) {
        message_handler_ = std::move(handler);
    }

    /**
     * 开始消费消息
     */
    bool start_consuming() {
        if (!connected_ || consuming_ || subscribed_topics_.empty()) {
            return false;
        }
        
        consuming_ = true;
        
        // 启动消费者线程
        consumer_thread_ = std::thread([this]() {
            consume_messages();
        });
        
        return true;
    }

    /**
     * 停止消费消息
     */
    void stop_consuming() {
        consuming_ = false;
        
        if (consumer_thread_.joinable()) {
            queue_cv_.notify_all();
            consumer_thread_.join();
        }
    }

    /**
     * 轮询消息
     */
    std::vector<KafkaMessage> poll(int timeout_ms) {
        std::vector<KafkaMessage> messages;
        
        // 在实际实现中，这里会调用 consumer->consume(timeout_ms)
        std::unique_lock<std::mutex> lock(queue_mutex_);
        
        auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms);
        
        while (message_queue_.empty() && std::chrono::steady_clock::now() < deadline) {
            queue_cv_.wait_until(lock, deadline);
        }
        
        while (!message_queue_.empty()) {
            messages.push_back(message_queue_.front());
            message_queue_.pop();
        }
        
        return messages;
    }

    /**
     * 提交偏移量
     */
    bool commit_sync() {
        // 在实际实现中，这里会调用 consumer->commitSync()
        return true;
    }

    bool commit_async() {
        // 在实际实现中，这里会调用 consumer->commitAsync()
        return true;
    }

    /**
     * 手动提交特定偏移量
     */
    bool commit_offset(const std::string& topic, int32_t partition, int64_t offset) {
        std::lock_guard<std::mutex> lock(offset_mutex_);
        topic_offsets_[topic + "_" + std::to_string(partition)] = offset;
        
        // 在实际实现中，这里会创建 TopicPartition 并调用 commitSync()
        return true;
    }

    /**
     * 获取统计信息
     */
    uint64_t get_consumed_count() const {
        return consumed_count_;
    }

    uint64_t get_bytes_received() const {
        return bytes_received_;
    }

    bool is_connected() const {
        return connected_;
    }

    bool is_consuming() const {
        return consuming_;
    }

private:
    /**
     * 消息消费循环
     */
    void consume_messages() {
        while (consuming_) {
            auto messages = poll(1000);  // 1秒超时
            
            for (const auto& message : messages) {
                if (message_handler_) {
                    try {
                        message_handler_(message);
                        consumed_count_++;
                        bytes_received_ += message.value.size();
                    } catch (const std::exception& e) {
                        // 处理消息处理失败的情况
                    }
                }
            }
        }
    }

    /**
     * 模拟消息生成器（仅用于演示）
     */
    void start_message_simulator() {
        std::thread([this]() {
            int message_id = 0;
            while (connected_) {
                std::this_thread::sleep_for(std::chrono::milliseconds(300));
                
                if (consuming_ && !subscribed_topics_.empty()) {
                    for (const auto& topic : subscribed_topics_) {
                        KafkaMessage message;
                        message.topic = topic;
                        message.value = "Simulated Kafka message " + std::to_string(message_id++);
                        message.key = "key_" + std::to_string(message_id % 10);
                        message.partition = message_id % 3;  // 假设3个分区
                        message.offset = message_id;
                        
                        {
                            std::lock_guard<std::mutex> lock(queue_mutex_);
                            message_queue_.push(message);
                        }
                        queue_cv_.notify_one();
                    }
                }
            }
        }).detach();
    }
};

/**
 * Kafka 生产者消费者包装器
 */
template<typename T>
class KafkaQueue {
private:
    std::unique_ptr<KafkaProducer> producer_;
    std::unique_ptr<KafkaConsumer> consumer_;
    KafkaConfig config_;
    
    // 序列化/反序列化函数
    std::function<std::string(const T&)> serializer_;
    std::function<T(const std::string&)> deserializer_;

public:
    explicit KafkaQueue(const KafkaConfig& config) : config_(config) {
        producer_ = std::make_unique<KafkaProducer>(config_);
        consumer_ = std::make_unique<KafkaConsumer>(config_);
        
        // 默认序列化器（仅适用于基本类型）
        serializer_ = [](const T& item) {
            return std::to_string(item);
        };
        
        deserializer_ = [](const std::string& str) {
            if constexpr (std::is_same_v<T, int>) {
                return std::stoi(str);
            } else if constexpr (std::is_same_v<T, double>) {
                return std::stod(str);
            } else {
                return T{}; // 需要特化
            }
        };
    }

    /**
     * 设置自定义序列化器
     */
    void set_serializer(std::function<std::string(const T&)> serializer,
                       std::function<T(const std::string&)> deserializer) {
        serializer_ = std::move(serializer);
        deserializer_ = std::move(deserializer);
    }

    /**
     * 连接到 Kafka
     */
    bool connect() {
        return producer_->connect() && consumer_->connect();
    }

    /**
     * 断开连接
     */
    void disconnect() {
        producer_->disconnect();
        consumer_->disconnect();
    }

    /**
     * 发送消息
     */
    bool push(const T& item, const std::string& key = "") {
        KafkaMessage message;
        message.topic = config_.default_topic;
        message.value = serializer_(item);
        message.key = key;
        
        return producer_->produce(message);
    }

    /**
     * 批量发送消息
     */
    size_t push_batch(const std::vector<T>& items) {
        std::vector<KafkaMessage> messages;
        messages.reserve(items.size());
        
        for (size_t i = 0; i < items.size(); ++i) {
            KafkaMessage message;
            message.topic = config_.default_topic;
            message.value = serializer_(items[i]);
            message.key = "batch_" + std::to_string(i);
            messages.push_back(message);
        }
        
        return producer_->produce_batch(messages);
    }

    /**
     * 订阅主题并开始消费
     */
    bool start_consuming(std::function<void(const T&)> handler) {
        consumer_->set_message_handler([this, handler](const KafkaMessage& message) {
            try {
                T item = deserializer_(message.value);
                handler(item);
            } catch (const std::exception& e) {
                // 处理反序列化错误
            }
        });
        
        std::vector<std::string> topics = {config_.default_topic};
        return consumer_->subscribe(topics) && consumer_->start_consuming();
    }

    /**
     * 停止消费消息
     */
    void stop_consuming() {
        consumer_->stop_consuming();
    }

    /**
     * 刷新生产者缓冲区
     */
    bool flush(int timeout_ms = 10000) {
        return producer_->flush(timeout_ms);
    }

    /**
     * 提交消费者偏移量
     */
    bool commit() {
        return consumer_->commit_sync();
    }

    /**
     * 获取统计信息
     */
    uint64_t get_produced_count() const {
        return producer_->get_message_count();
    }

    uint64_t get_consumed_count() const {
        return consumer_->get_consumed_count();
    }

    uint64_t get_bytes_sent() const {
        return producer_->get_bytes_sent();
    }

    uint64_t get_bytes_received() const {
        return consumer_->get_bytes_received();
    }

    bool is_connected() const {
        return producer_->is_connected() && consumer_->is_connected();
    }
};

} // namespace stage7
