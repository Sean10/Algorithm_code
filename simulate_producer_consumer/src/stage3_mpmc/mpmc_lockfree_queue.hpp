
#pragma once

#include <atomic>
#include <memory>
#include <stdexcept>

namespace stage3 {

/**
 * 阶段三：MPMC（多生产者多消费者）无锁队列
 * 
 * 基于循环数组的无锁队列，支持多个生产者和多个消费者同时操作。
 * 
 * 关键技术：
 * 1. 使用 Compare-And-Swap (CAS) 操作来保证原子性
 * 2. 正确的内存序处理
 * 3. 避免 ABA 问题（在此简化版本中通过单调递增索引避免）
 * 
 * 注意：这是一个学习版本的实现，实际生产环境建议使用经过充分测试的库
 */
template <typename T>  
class LockFreeArrayQueue {  
private:  
    std::unique_ptr<T[]> buffer_;
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;
    const size_t capacity_;
  
public:  
    /**
     * 构造函数
     * @param capacity 队列容量
     */
    explicit LockFreeArrayQueue(size_t capacity)  
        : buffer_(std::make_unique<T[]>(capacity))
        , head_(0)
        , tail_(0)
        , capacity_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be greater than 0");
        }
    }  
  
    /**
     * 入队操作（多生产者安全）
     * @param item 要入队的元素
     * @return true 成功，false 队列已满
     */
    bool enqueue(const T& item) {  
        while (true) {
            // 1. 获取当前 tail 位置
            size_t currTail = tail_.load(std::memory_order_acquire);
            size_t nextTail = (currTail + 1) % capacity_;
            
            // 2. 检查队列是否已满
            if (nextTail == head_.load(std::memory_order_acquire)) {
                return false; // 队列满
            }
            
            // 3. 尝试原子地移动 tail 指针
            if (tail_.compare_exchange_weak(currTail, nextTail, 
                                          std::memory_order_release, 
                                          std::memory_order_relaxed)) {
                // 4. 成功获得了 currTail 位置，写入数据
                buffer_[currTail] = item;
                return true;
            }
            // CAS 失败，说明其他线程抢先了，重试
        }  
    }
    
    /**
     * 入队操作（移动语义）
     */
    bool enqueue(T&& item) {
        while (true) {
            size_t currTail = tail_.load(std::memory_order_acquire);
            size_t nextTail = (currTail + 1) % capacity_;
            
            if (nextTail == head_.load(std::memory_order_acquire)) {
                return false; // 队列满
            }
            
            if (tail_.compare_exchange_weak(currTail, nextTail, 
                                          std::memory_order_release, 
                                          std::memory_order_relaxed)) {
                buffer_[currTail] = std::move(item);
                return true;
            }
        }
    }
  
    /**
     * 出队操作（多消费者安全）
     * @param item 存储出队元素的引用
     * @return true 成功，false 队列为空
     */
    bool dequeue(T& item) {  
        while (true) {
            // 1. 获取当前 head 位置
            size_t currHead = head_.load(std::memory_order_acquire);
            
            // 2. 检查队列是否为空
            if (currHead == tail_.load(std::memory_order_acquire)) {
                return false; // 队列空
            }
            
            size_t nextHead = (currHead + 1) % capacity_;
            
            // 3. 尝试原子地移动 head 指针
            if (head_.compare_exchange_weak(currHead, nextHead,
                                          std::memory_order_release,
                                          std::memory_order_relaxed)) {
                // 4. 成功获得了 currHead 位置，读取数据
                // 使用 swap 以支持 move-only 类型
                std::swap(item, buffer_[currHead]);
                return true;
            }
            // CAS 失败，说明其他线程抢先了，重试
        }  
    }
    
    /**
     * 获取队列当前大小（近似值）
     * 注意：在多线程环境下，这个值可能不精确，仅供参考
     */
    size_t size() const {
        size_t currTail = tail_.load(std::memory_order_acquire);
        size_t currHead = head_.load(std::memory_order_acquire);
        return (currTail >= currHead) ? 
               (currTail - currHead) : 
               (capacity_ + currTail - currHead);
    }
    
    /**
     * 检查队列是否为空（近似值）
     */
    bool empty() const {
        return head_.load(std::memory_order_acquire) == 
               tail_.load(std::memory_order_acquire);
    }
    
    /**
     * 获取队列容量
     */
    size_t capacity() const {
        return capacity_;
    }
};

} // namespace stage3
