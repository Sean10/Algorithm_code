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

namespace stage7 {

/**
 * RabbitMQ 客户端接口（模拟实现）
 * 
 * 注意：这是一个模拟实现，展示了如何集成 RabbitMQ 的概念。
 * 在实际项目中，你需要链接真实的 RabbitMQ C++ 客户端库，如：
 * - SimpleAmqpClient
 * - amqpcpp
 * - rabbitmq-c
 */

struct RabbitMQMessage {
    std::string body;
    std::string routing_key;
    std::chrono::system_clock::time_point timestamp;
    std::string correlation_id;
    std::string reply_to;
    
    RabbitMQMessage() : timestamp(std::chrono::system_clock::now()) {}
    
    RabbitMQMessage(const std::string& msg_body, const std::string& key = "")
        : body(msg_body), routing_key(key), timestamp(std::chrono::system_clock::now()) {}
};

/**
 * RabbitMQ 连接配置
 */
struct RabbitMQConfig {
    std::string host = "localhost";
    int port = 5672;
    std::string username = "guest";
    std::string password = "guest";
    std::string vhost = "/";
    std::string exchange = "producer_consumer_exchange";
    std::string queue_name = "producer_consumer_queue";
    bool durable = true;
    bool auto_ack = false;
    int prefetch_count = 10;
};

/**
 * RabbitMQ 生产者客户端（模拟实现）
 */
class RabbitMQProducer {
private:
    RabbitMQConfig config_;
    std::atomic<bool> connected_{false};
    std::atomic<uint64_t> message_count_{0};
    
    // 模拟连接状态
    mutable std::mutex connection_mutex_;

public:
    explicit RabbitMQProducer(const RabbitMQConfig& config) : config_(config) {}

    /**
     * 连接到 RabbitMQ 服务器
     */
    bool connect() {
        std::lock_guard<std::mutex> lock(connection_mutex_);
        
        // 模拟连接过程
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // 在实际实现中，这里会：
        // 1. 创建 AMQP 连接
        // 2. 创建通道
        // 3. 声明交换机和队列
        // 4. 设置绑定关系
        
        connected_ = true;
        return true;
    }

    /**
     * 断开连接
     */
    void disconnect() {
        std::lock_guard<std::mutex> lock(connection_mutex_);
        connected_ = false;
    }

    /**
     * 发布消息
     */
    bool publish(const RabbitMQMessage& message) {
        if (!connected_) {
            return false;
        }

        // 模拟消息发布
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        
        // 在实际实现中，这里会：
        // channel->BasicPublish(config_.exchange, message.routing_key, message_properties, message.body);
        
        message_count_++;
        return true;
    }

    /**
     * 批量发布消息
     */
    size_t publish_batch(const std::vector<RabbitMQMessage>& messages) {
        size_t published_count = 0;
        
        for (const auto& message : messages) {
            if (publish(message)) {
                published_count++;
            } else {
                break;
            }
        }
        
        return published_count;
    }

    /**
     * 异步发布消息（带确认）
     */
    bool publish_with_confirm(const RabbitMQMessage& message, 
                             std::chrono::milliseconds timeout = std::chrono::milliseconds(5000)) {
        if (!publish(message)) {
            return false;
        }
        
        // 模拟等待确认
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        
        // 在实际实现中，这里会等待 broker 的确认
        return true;
    }

    /**
     * 获取统计信息
     */
    uint64_t get_message_count() const {
        return message_count_;
    }

    bool is_connected() const {
        return connected_;
    }
};

/**
 * RabbitMQ 消费者客户端（模拟实现）
 */
class RabbitMQConsumer {
private:
    RabbitMQConfig config_;
    std::atomic<bool> connected_{false};
    std::atomic<bool> consuming_{false};
    std::atomic<uint64_t> consumed_count_{0};
    
    // 模拟消息队列
    std::queue<RabbitMQMessage> message_queue_;
    std::mutex queue_mutex_;
    std::condition_variable queue_cv_;
    
    // 消费者线程
    std::thread consumer_thread_;
    
    // 消息处理回调
    std::function<void(const RabbitMQMessage&)> message_handler_;

public:
    explicit RabbitMQConsumer(const RabbitMQConfig& config) : config_(config) {}

    ~RabbitMQConsumer() {
        stop_consuming();
        disconnect();
    }

    /**
     * 连接到 RabbitMQ 服务器
     */
    bool connect() {
        if (connected_) {
            return true;
        }
        
        // 模拟连接过程
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // 在实际实现中，这里会：
        // 1. 创建 AMQP 连接
        // 2. 创建通道
        // 3. 声明队列
        // 4. 设置 QoS（prefetch）
        
        connected_ = true;
        
        // 启动模拟消息生成器（在实际实现中不需要）
        start_message_simulator();
        
        return true;
    }

    /**
     * 断开连接
     */
    void disconnect() {
        stop_consuming();
        connected_ = false;
    }

    /**
     * 设置消息处理器
     */
    void set_message_handler(std::function<void(const RabbitMQMessage&)> handler) {
        message_handler_ = std::move(handler);
    }

    /**
     * 开始消费消息
     */
    bool start_consuming() {
        if (!connected_ || consuming_) {
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
     * 手动确认消息
     */
    bool ack_message(const std::string& delivery_tag) {
        // 在实际实现中，这里会调用 channel->BasicAck(delivery_tag)
        return true;
    }

    /**
     * 拒绝消息
     */
    bool nack_message(const std::string& delivery_tag, bool requeue = true) {
        // 在实际实现中，这里会调用 channel->BasicNack(delivery_tag, false, requeue)
        return true;
    }

    /**
     * 获取统计信息
     */
    uint64_t get_consumed_count() const {
        return consumed_count_;
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
            std::unique_lock<std::mutex> lock(queue_mutex_);
            
            // 等待消息或停止信号
            queue_cv_.wait(lock, [this] {
                return !message_queue_.empty() || !consuming_;
            });
            
            if (!consuming_) {
                break;
            }
            
            if (!message_queue_.empty()) {
                RabbitMQMessage message = message_queue_.front();
                message_queue_.pop();
                lock.unlock();
                
                // 处理消息
                if (message_handler_) {
                    try {
                        message_handler_(message);
                        consumed_count_++;
                    } catch (const std::exception& e) {
                        // 在实际实现中，这里应该处理消息处理失败的情况
                        // 可能需要 nack 消息或将其发送到死信队列
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
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                
                if (consuming_) {
                    RabbitMQMessage message;
                    message.body = "Simulated message " + std::to_string(message_id++);
                    message.routing_key = config_.queue_name;
                    
                    {
                        std::lock_guard<std::mutex> lock(queue_mutex_);
                        message_queue_.push(message);
                    }
                    queue_cv_.notify_one();
                }
            }
        }).detach();
    }
};

/**
 * RabbitMQ 生产者消费者包装器
 */
template<typename T>
class RabbitMQQueue {
private:
    std::unique_ptr<RabbitMQProducer> producer_;
    std::unique_ptr<RabbitMQConsumer> consumer_;
    RabbitMQConfig config_;
    
    // 序列化/反序列化函数
    std::function<std::string(const T&)> serializer_;
    std::function<T(const std::string&)> deserializer_;

public:
    explicit RabbitMQQueue(const RabbitMQConfig& config) : config_(config) {
        producer_ = std::make_unique<RabbitMQProducer>(config_);
        consumer_ = std::make_unique<RabbitMQConsumer>(config_);
        
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
     * 连接到 RabbitMQ
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
    bool push(const T& item) {
        RabbitMQMessage message;
        message.body = serializer_(item);
        message.routing_key = config_.queue_name;
        
        return producer_->publish(message);
    }

    /**
     * 批量发送消息
     */
    size_t push_batch(const std::vector<T>& items) {
        std::vector<RabbitMQMessage> messages;
        messages.reserve(items.size());
        
        for (const auto& item : items) {
            RabbitMQMessage message;
            message.body = serializer_(item);
            message.routing_key = config_.queue_name;
            messages.push_back(message);
        }
        
        return producer_->publish_batch(messages);
    }

    /**
     * 开始消费消息
     */
    bool start_consuming(std::function<void(const T&)> handler) {
        consumer_->set_message_handler([this, handler](const RabbitMQMessage& message) {
            try {
                T item = deserializer_(message.body);
                handler(item);
            } catch (const std::exception& e) {
                // 处理反序列化错误
            }
        });
        
        return consumer_->start_consuming();
    }

    /**
     * 停止消费消息
     */
    void stop_consuming() {
        consumer_->stop_consuming();
    }

    /**
     * 获取统计信息
     */
    uint64_t get_published_count() const {
        return producer_->get_message_count();
    }

    uint64_t get_consumed_count() const {
        return consumer_->get_consumed_count();
    }

    bool is_connected() const {
        return producer_->is_connected() && consumer_->is_connected();
    }
};

} // namespace stage7
