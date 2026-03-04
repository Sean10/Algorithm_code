#pragma once

#include <latch>
#include <semaphore>
#include <queue>
#include <mutex>
#include <thread>
#include <vector>
#include <chrono>

namespace stage6 {

/**
 * 阶段六：C++23 新特性应用 - std::latch 和 std::semaphore
 * 
 * 本实现展示了如何使用 C++20/23 的新同步原语来优化生产者消费者模型：
 * 1. std::latch - 用于一次性同步事件
 * 2. std::semaphore - 用于资源计数和流量控制
 */
template<typename T>
class LatchSemaphoreQueue {
private:
    std::queue<T> queue_;
    std::mutex mutex_;
    
    // 使用信号量控制队列容量
    std::counting_semaphore<> empty_slots_;  // 空位信号量
    std::counting_semaphore<> filled_slots_; // 已填充位信号量
    
    const size_t capacity_;

public:
    explicit LatchSemaphoreQueue(size_t capacity) 
        : empty_slots_(capacity)    // 初始时所有位置都是空的
        , filled_slots_(0)          // 初始时没有数据
        , capacity_(capacity) {
        
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be greater than 0");
        }
    }

    /**
     * 使用信号量的入队操作
     */
    bool push(const T& item) {
        // 等待空位
        empty_slots_.acquire();
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push(item);
        }
        
        // 通知有新数据
        filled_slots_.release();
        return true;
    }

    /**
     * 带超时的入队操作
     */
    template<typename Rep, typename Period>
    bool push_for(const T& item, const std::chrono::duration<Rep, Period>& timeout) {
        // 尝试获取空位，带超时
        if (!empty_slots_.try_acquire_for(timeout)) {
            return false;
        }
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push(item);
        }
        
        filled_slots_.release();
        return true;
    }

    /**
     * 使用信号量的出队操作
     */
    bool pop(T& item) {
        // 等待数据
        filled_slots_.acquire();
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            item = queue_.front();
            queue_.pop();
        }
        
        // 释放空位
        empty_slots_.release();
        return true;
    }

    /**
     * 带超时的出队操作
     */
    template<typename Rep, typename Period>
    bool pop_for(T& item, const std::chrono::duration<Rep, Period>& timeout) {
        if (!filled_slots_.try_acquire_for(timeout)) {
            return false;
        }
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            item = queue_.front();
            queue_.pop();
        }
        
        empty_slots_.release();
        return true;
    }

    /**
     * 获取当前队列大小
     */
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

    /**
     * 检查队列是否为空
     */
    bool empty() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.empty();
    }
};

/**
 * 使用 std::latch 协调多个生产者和消费者的启动
 */
class CoordinatedProducerConsumer {
private:
    LatchSemaphoreQueue<int> queue_;
    std::latch start_latch_;        // 用于同步所有线程的开始
    std::latch producers_done_;     // 等待所有生产者完成
    std::latch consumers_done_;     // 等待所有消费者完成
    
    const int producer_count_;
    const int consumer_count_;
    const int items_per_producer_;

public:
    CoordinatedProducerConsumer(size_t queue_capacity, 
                               int producer_count, 
                               int consumer_count,
                               int items_per_producer)
        : queue_(queue_capacity)
        , start_latch_(1)                    // 1个启动信号
        , producers_done_(producer_count)    // 等待所有生产者
        , consumers_done_(consumer_count)    // 等待所有消费者
        , producer_count_(producer_count)
        , consumer_count_(consumer_count)
        , items_per_producer_(items_per_producer) {}

    /**
     * 生产者线程函数
     */
    void producer_thread(int producer_id) {
        // 等待启动信号
        start_latch_.wait();
        
        // 生产数据
        for (int i = 0; i < items_per_producer_; ++i) {
            int value = producer_id * 1000 + i;
            queue_.push(value);
            
            // 模拟生产时间
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        
        // 通知生产完成
        producers_done_.arrive_and_wait();
    }

    /**
     * 消费者线程函数
     */
    void consumer_thread(int consumer_id) {
        // 等待启动信号
        start_latch_.wait();
        
        int consumed_count = 0;
        int total_items = producer_count_ * items_per_producer_;
        int items_per_consumer = total_items / consumer_count_;
        
        // 消费数据
        for (int i = 0; i < items_per_consumer; ++i) {
            int value;
            if (queue_.pop_for(value, std::chrono::seconds(1))) {
                consumed_count++;
                
                // 模拟处理时间
                std::this_thread::sleep_for(std::chrono::microseconds(500));
            }
        }
        
        // 通知消费完成
        consumers_done_.arrive_and_wait();
    }

    /**
     * 运行协调的生产者消费者测试
     */
    void run() {
        std::vector<std::thread> producers;
        std::vector<std::thread> consumers;
        
        // 创建生产者线程
        for (int i = 0; i < producer_count_; ++i) {
            producers.emplace_back(&CoordinatedProducerConsumer::producer_thread, this, i);
        }
        
        // 创建消费者线程
        for (int i = 0; i < consumer_count_; ++i) {
            consumers.emplace_back(&CoordinatedProducerConsumer::consumer_thread, this, i);
        }
        
        // 等待一小段时间确保所有线程都准备好
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // 发出启动信号
        start_latch_.count_down();
        
        // 等待所有线程完成
        for (auto& t : producers) {
            t.join();
        }
        for (auto& t : consumers) {
            t.join();
        }
    }
};

} // namespace stage6
