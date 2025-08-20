#pragma once

#include <vector>
#include <mutex>
#include <condition_variable>
#include <chrono>

namespace stage1 {

/**
 * 阶段一：基于互斥锁的线程安全队列
 * 
 * 这是经典的生产者-消费者队列实现，使用互斥锁和条件变量来保证线程安全。
 * 优点：实现简单，逻辑清晰，公平性好
 * 缺点：锁竞争开销大，可能成为性能瓶颈
 */
template<typename T>
class MutexQueue {
private:
    mutable std::mutex mutex_;
    std::condition_variable not_empty_;
    std::condition_variable not_full_;
    std::vector<T> buffer_;
    size_t head_;
    size_t tail_;
    size_t count_;
    const size_t capacity_;

public:
    explicit MutexQueue(size_t capacity) 
        : buffer_(capacity), head_(0), tail_(0), count_(0), capacity_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Queue capacity must be greater than 0");
        }
    }

    /**
     * 阻塞式入队
     * @param item 要入队的元素
     * @return true 成功，false 失败（不应该发生在阻塞模式下）
     */
    bool push(const T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_.wait(lock, [this] { return count_ < capacity_; });
        
        buffer_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_;
        ++count_;
        
        not_empty_.notify_one();
        return true;
    }

    /**
     * 带超时的入队
     * @param item 要入队的元素
     * @param timeout_ms 超时时间（毫秒）
     * @return true 成功，false 超时
     */
    template<typename Rep, typename Period>
    bool push_for(const T& item, const std::chrono::duration<Rep, Period>& timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!not_full_.wait_for(lock, timeout, [this] { return count_ < capacity_; })) {
            return false; // 超时
        }
        
        buffer_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_;
        ++count_;
        
        not_empty_.notify_one();
        return true;
    }

    /**
     * 阻塞式出队
     * @param item 存储出队元素的引用
     * @return true 成功，false 失败（不应该发生在阻塞模式下）
     */
    bool pop(T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_.wait(lock, [this] { return count_ > 0; });
        
        item = buffer_[head_];
        head_ = (head_ + 1) % capacity_;
        --count_;
        
        not_full_.notify_one();
        return true;
    }

    /**
     * 带超时的出队
     * @param item 存储出队元素的引用
     * @param timeout_ms 超时时间（毫秒）
     * @return true 成功，false 超时
     */
    template<typename Rep, typename Period>
    bool pop_for(T& item, const std::chrono::duration<Rep, Period>& timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!not_empty_.wait_for(lock, timeout, [this] { return count_ > 0; })) {
            return false; // 超时
        }
        
        item = buffer_[head_];
        head_ = (head_ + 1) % capacity_;
        --count_;
        
        not_full_.notify_one();
        return true;
    }

    /**
     * 获取队列当前大小
     */
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

    /**
     * 检查队列是否为空
     */
    bool empty() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_ == 0;
    }

    /**
     * 检查队列是否已满
     */
    bool full() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_ == capacity_;
    }

    /**
     * 获取队列容量
     */
    size_t capacity() const {
        return capacity_;
    }
};

} // namespace stage1
