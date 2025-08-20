#pragma once

#include <atomic>
#include <memory>

namespace stage2 {

/**
 * 阶段二：SPSC（单生产者单消费者）无锁环形缓冲区
 * 
 * 这是最简单的无锁队列实现，因为只有一个生产者和一个消费者，
 * 所以不需要使用复杂的CAS操作，只需要合适的内存序即可。
 * 
 * 关键点：
 * 1. 生产者独占tail指针，消费者独占head指针
 * 2. 使用acquire-release内存序来建立同步关系
 * 3. 避免伪共享：head和tail应该在不同的缓存行上
 */
template<typename T>
class SPSCRingBuffer {
private:
    struct alignas(64) AlignedAtomic {
        std::atomic<size_t> value{0};
    };

    std::unique_ptr<T[]> buffer_;
    const size_t capacity_;
    const size_t mask_; // capacity_ - 1，用于快速取模（要求capacity为2的幂）
    
    // 使用缓存行对齐避免伪共享
    AlignedAtomic head_;  // 消费者独占
    AlignedAtomic tail_;  // 生产者独占

public:
    /**
     * 构造函数
     * @param capacity 队列容量，必须是2的幂
     */
    explicit SPSCRingBuffer(size_t capacity) 
        : buffer_(std::make_unique<T[]>(capacity))
        , capacity_(capacity)
        , mask_(capacity - 1) {
        
        // 验证capacity是2的幂
        if (capacity == 0 || (capacity & (capacity - 1)) != 0) {
            throw std::invalid_argument("Capacity must be a power of 2");
        }
    }

    /**
     * 生产者入队（非阻塞）
     * @param item 要入队的元素
     * @return true 成功，false 队列已满
     */
    bool push(const T& item) {
        const size_t current_tail = tail_.value.load(std::memory_order_relaxed);
        const size_t next_tail = (current_tail + 1) & mask_;
        
        // 检查队列是否已满
        if (next_tail == head_.value.load(std::memory_order_acquire)) {
            return false;
        }
        
        // 写入数据
        buffer_[current_tail] = item;
        
        // 发布新的tail值，使用release语义确保数据写入对消费者可见
        tail_.value.store(next_tail, std::memory_order_release);
        return true;
    }

    /**
     * 生产者入队（移动语义）
     */
    bool push(T&& item) {
        const size_t current_tail = tail_.value.load(std::memory_order_relaxed);
        const size_t next_tail = (current_tail + 1) & mask_;
        
        if (next_tail == head_.value.load(std::memory_order_acquire)) {
            return false;
        }
        
        buffer_[current_tail] = std::move(item);
        tail_.value.store(next_tail, std::memory_order_release);
        return true;
    }

    /**
     * 消费者出队（非阻塞）
     * @param item 存储出队元素的引用
     * @return true 成功，false 队列为空
     */
    bool pop(T& item) {
        const size_t current_head = head_.value.load(std::memory_order_relaxed);
        
        // 检查队列是否为空，使用acquire语义确保能看到生产者的数据
        if (current_head == tail_.value.load(std::memory_order_acquire)) {
            return false;
        }
        
        // 读取数据
        item = buffer_[current_head];
        
        // 更新head位置，使用release语义确保空间释放对生产者可见
        head_.value.store((current_head + 1) & mask_, std::memory_order_release);
        return true;
    }

    /**
     * 获取队列当前大小（近似值）
     * 注意：在多线程环境下，这个值可能不精确，仅供参考
     */
    size_t size() const {
        const size_t current_tail = tail_.value.load(std::memory_order_acquire);
        const size_t current_head = head_.value.load(std::memory_order_acquire);
        return (current_tail - current_head) & mask_;
    }

    /**
     * 检查队列是否为空（近似值）
     */
    bool empty() const {
        return head_.value.load(std::memory_order_acquire) == 
               tail_.value.load(std::memory_order_acquire);
    }

    /**
     * 获取队列容量
     */
    size_t capacity() const {
        return capacity_;
    }
};

} // namespace stage2
