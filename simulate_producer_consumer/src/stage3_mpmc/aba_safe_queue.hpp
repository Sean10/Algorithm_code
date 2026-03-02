#pragma once

#include <atomic>
#include <memory>
#include <stdexcept>

namespace stage3 {

/**
 * ABA 安全的 MPMC 队列实现
 * 
 * 这个实现展示了如何使用版本号/计数器来解决 ABA 问题。
 * 虽然在基于数组的队列中 ABA 问题风险较低，但这种技术在链表结构中至关重要。
 * 
 * ABA 问题：
 * 1. 线程 A 读取指针 P，值为 A
 * 2. 线程 B 将 P 改为 B，然后又改回 A（可能是不同的 A）
 * 3. 线程 A 执行 CAS，发现值还是 A，误以为没有变化
 * 
 * 解决方案：
 * 1. 使用版本号标记每次修改
 * 2. CAS 操作同时检查值和版本号
 */

template <typename T>
class ABASafeQueue {
private:
    /**
     * 带版本号的原子索引结构
     */
    struct VersionedIndex {
        size_t index;
        size_t version;
        
        VersionedIndex() : index(0), version(0) {}
        VersionedIndex(size_t idx, size_t ver) : index(idx), version(ver) {}
        
        bool operator==(const VersionedIndex& other) const {
            return index == other.index && version == other.version;
        }
        
        bool operator!=(const VersionedIndex& other) const {
            return !(*this == other);
        }
    };
    
    std::unique_ptr<T[]> buffer_;
    std::atomic<VersionedIndex> head_;
    std::atomic<VersionedIndex> tail_;
    const size_t capacity_;
    
public:
    /**
     * 构造函数
     * @param capacity 队列容量
     */
    explicit ABASafeQueue(size_t capacity)
        : buffer_(std::make_unique<T[]>(capacity))
        , head_(VersionedIndex{0, 0})
        , tail_(VersionedIndex{0, 0})
        , capacity_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be greater than 0");
        }
    }
    
    /**
     * 入队操作（ABA 安全）
     * @param item 要入队的元素
     * @return true 成功，false 队列已满
     */
    bool enqueue(const T& item) {
        while (true) {
            // 1. 原子地读取当前 tail 的值和版本号
            VersionedIndex currTail = tail_.load(std::memory_order_acquire);
            size_t nextIndex = (currTail.index + 1) % capacity_;
            
            // 2. 检查队列是否已满
            VersionedIndex currHead = head_.load(std::memory_order_acquire);
            if (nextIndex == currHead.index) {
                return false; // 队列满
            }
            
            // 3. 创建新的 tail 值，版本号递增
            VersionedIndex newTail{nextIndex, currTail.version + 1};
            
            // 4. 尝试原子地更新 tail，同时检查值和版本号
            if (tail_.compare_exchange_weak(currTail, newTail, 
                                          std::memory_order_release, 
                                          std::memory_order_relaxed)) {
                // 5. 成功获得了 currTail.index 位置，写入数据
                buffer_[currTail.index] = item;
                return true;
            }
            // CAS 失败，可能是因为：
            // - 其他线程修改了 tail（正常竞争）
            // - ABA 问题（版本号不匹配）
            // 无论哪种情况，都需要重试
        }
    }
    
    /**
     * 入队操作（移动语义，ABA 安全）
     */
    bool enqueue(T&& item) {
        while (true) {
            VersionedIndex currTail = tail_.load(std::memory_order_acquire);
            size_t nextIndex = (currTail.index + 1) % capacity_;
            
            VersionedIndex currHead = head_.load(std::memory_order_acquire);
            if (nextIndex == currHead.index) {
                return false; // 队列满
            }
            
            VersionedIndex newTail{nextIndex, currTail.version + 1};
            
            if (tail_.compare_exchange_weak(currTail, newTail, 
                                          std::memory_order_release, 
                                          std::memory_order_relaxed)) {
                buffer_[currTail.index] = std::move(item);
                return true;
            }
        }
    }
    
    /**
     * 出队操作（ABA 安全）
     * @param item 存储出队元素的引用
     * @return true 成功，false 队列为空
     */
    bool dequeue(T& item) {
        while (true) {
            // 1. 原子地读取当前 head 的值和版本号
            VersionedIndex currHead = head_.load(std::memory_order_acquire);
            
            // 2. 检查队列是否为空
            VersionedIndex currTail = tail_.load(std::memory_order_acquire);
            if (currHead.index == currTail.index) {
                return false; // 队列空
            }
            
            size_t nextIndex = (currHead.index + 1) % capacity_;
            
            // 3. 创建新的 head 值，版本号递增
            VersionedIndex newHead{nextIndex, currHead.version + 1};
            
            // 4. 尝试原子地更新 head，同时检查值和版本号
            if (head_.compare_exchange_weak(currHead, newHead, 
                                          std::memory_order_release, 
                                          std::memory_order_relaxed)) {
                // 5. 成功获得了 currHead.index 位置，读取数据
                item = buffer_[currHead.index];
                return true;
            }
            // CAS 失败，重试
        }
    }
    
    /**
     * 获取队列当前大小（近似值）
     * 注意：版本号可能导致 ABA 检查更加严格，但 size 计算仍然是近似的
     */
    size_t size() const {
        VersionedIndex currTail = tail_.load(std::memory_order_acquire);
        VersionedIndex currHead = head_.load(std::memory_order_acquire);
        
        if (currTail.index >= currHead.index) {
            return currTail.index - currHead.index;
        } else {
            return capacity_ + currTail.index - currHead.index;
        }
    }
    
    /**
     * 检查队列是否为空（近似值）
     */
    bool empty() const {
        VersionedIndex currHead = head_.load(std::memory_order_acquire);
        VersionedIndex currTail = tail_.load(std::memory_order_acquire);
        return currHead.index == currTail.index;
    }
    
    /**
     * 获取队列容量
     */
    size_t capacity() const {
        return capacity_;
    }
    
    /**
     * 获取当前头指针版本号（用于调试和测试）
     */
    size_t head_version() const {
        return head_.load(std::memory_order_acquire).version;
    }
    
    /**
     * 获取当前尾指针版本号（用于调试和测试）
     */
    size_t tail_version() const {
        return tail_.load(std::memory_order_acquire).version;
    }
};

/**
 * 专门处理指针类型的 ABA 安全队列
 * 
 * 对于指针类型，我们可以使用标记指针技术，
 * 利用指针地址的低位（由于内存对齐通常未使用）来存储版本信息。
 */
template <typename T>
class TaggedPointerQueue {
private:
    static constexpr uintptr_t TAG_MASK = 0x7;  // 低3位用作标记
    static constexpr uintptr_t PTR_MASK = ~TAG_MASK;  // 其余位是实际指针
    
    struct Node {
        std::atomic<T> data;
        std::atomic<Node*> next;
        
        Node() : next(nullptr) {}
        explicit Node(const T& item) : data(item), next(nullptr) {}
    };
    
    std::atomic<uintptr_t> head_;  // 标记指针
    std::atomic<uintptr_t> tail_;  // 标记指针
    
    // 从标记指针中提取实际指针
    Node* extract_ptr(uintptr_t tagged_ptr) const {
        return reinterpret_cast<Node*>(tagged_ptr & PTR_MASK);
    }
    
    // 从标记指针中提取标记
    uintptr_t extract_tag(uintptr_t tagged_ptr) const {
        return tagged_ptr & TAG_MASK;
    }
    
    // 创建标记指针
    uintptr_t make_tagged_ptr(Node* ptr, uintptr_t tag) const {
        return reinterpret_cast<uintptr_t>(ptr) | (tag & TAG_MASK);
    }
    
public:
    TaggedPointerQueue() {
        Node* dummy = new Node();
        uintptr_t tagged_ptr = make_tagged_ptr(dummy, 0);
        head_.store(tagged_ptr, std::memory_order_relaxed);
        tail_.store(tagged_ptr, std::memory_order_relaxed);
    }
    
    ~TaggedPointerQueue() {
        // 清理所有节点
        while (true) {
            uintptr_t head_tagged = head_.load(std::memory_order_relaxed);
            Node* head_ptr = extract_ptr(head_tagged);
            
            uintptr_t tail_tagged = tail_.load(std::memory_order_relaxed);
            Node* tail_ptr = extract_ptr(tail_tagged);
            
            if (head_ptr == tail_ptr) {
                delete head_ptr;
                break;
            }
            
            Node* next = head_ptr->next.load(std::memory_order_relaxed);
            delete head_ptr;
            head_.store(make_tagged_ptr(next, 0), std::memory_order_relaxed);
        }
    }
    
    /**
     * 使用标记指针的入队操作
     */
    void enqueue(const T& item) {
        Node* new_node = new Node(item);
        
        while (true) {
            uintptr_t tail_tagged = tail_.load(std::memory_order_acquire);
            Node* tail_ptr = extract_ptr(tail_tagged);
            uintptr_t tail_tag = extract_tag(tail_tagged);
            
            Node* next = tail_ptr->next.load(std::memory_order_acquire);
            
            // 检查 tail 是否仍然是最后一个节点
            uintptr_t current_tail_tagged = tail_.load(std::memory_order_acquire);
            if (current_tail_tagged != tail_tagged) {
                continue;  // tail 被修改了，重试
            }
            
            if (next == nullptr) {
                // tail 确实指向最后一个节点，尝试添加新节点
                if (tail_ptr->next.compare_exchange_weak(next, new_node,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed)) {
                    // 成功添加节点，现在移动 tail，递增标记
                    uintptr_t new_tail_tagged = make_tagged_ptr(new_node, tail_tag + 1);
                    tail_.compare_exchange_weak(tail_tagged, new_tail_tagged,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                    break;
                }
            } else {
                // tail 没有指向最后一个节点，帮助推进 tail
                uintptr_t new_tail_tagged = make_tagged_ptr(next, tail_tag + 1);
                tail_.compare_exchange_weak(tail_tagged, new_tail_tagged,
                                          std::memory_order_release,
                                          std::memory_order_relaxed);
            }
        }
    }
    
    /**
     * 使用标记指针的出队操作
     */
    bool dequeue(T& item) {
        while (true) {
            uintptr_t head_tagged = head_.load(std::memory_order_acquire);
            Node* head_ptr = extract_ptr(head_tagged);
            uintptr_t head_tag = extract_tag(head_tagged);
            
            uintptr_t tail_tagged = tail_.load(std::memory_order_acquire);
            Node* tail_ptr = extract_ptr(tail_tagged);
            
            Node* next = head_ptr->next.load(std::memory_order_acquire);
            
            // 检查 head 是否仍然一致
            uintptr_t current_head_tagged = head_.load(std::memory_order_acquire);
            if (current_head_tagged != head_tagged) {
                continue;  // head 被修改了，重试
            }
            
            if (head_ptr == tail_ptr) {
                if (next == nullptr) {
                    return false;  // 队列空
                }
                // tail 落后了，帮助推进它
                uintptr_t tail_tag = extract_tag(tail_tagged);
                uintptr_t new_tail_tagged = make_tagged_ptr(next, tail_tag + 1);
                tail_.compare_exchange_weak(tail_tagged, new_tail_tagged,
                                          std::memory_order_release,
                                          std::memory_order_relaxed);
            } else {
                if (next == nullptr) {
                    continue;  // 不一致状态，重试
                }
                
                // 读取数据
                item = next->data.load(std::memory_order_relaxed);
                
                // 移动 head，递增标记
                uintptr_t new_head_tagged = make_tagged_ptr(next, head_tag + 1);
                if (head_.compare_exchange_weak(head_tagged, new_head_tagged,
                                              std::memory_order_release,
                                              std::memory_order_relaxed)) {
                    delete head_ptr;
                    return true;
                }
            }
        }
    }
};

} // namespace stage3
