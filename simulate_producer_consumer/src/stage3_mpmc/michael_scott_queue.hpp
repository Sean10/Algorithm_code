#pragma once

#include <atomic>
#include <memory>

namespace stage3 {

/**
 * Michael-Scott 无锁队列算法实现
 * 
 * 这是无锁队列领域的经典算法，由 Maged M. Michael 和 Michael L. Scott 
 * 在 1996 年提出。几乎所有现代无锁队列实现都基于这个算法。
 * 
 * 论文：Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms
 * 
 * 关键特性：
 * 1. 基于单链表结构
 * 2. 使用 CAS 操作保证线程安全
 * 3. 支持多生产者和多消费者（MPMC）
 * 4. 无锁且无饥饿
 * 
 * 算法核心思想：
 * 1. 使用虚拟头节点简化边界条件处理
 * 2. head 指向第一个虚拟节点，tail 指向最后一个节点（或接近最后的节点）
 * 3. 入队：在链表末尾添加节点，然后推进 tail
 * 4. 出队：从头部移除节点，推进 head
 */
template <typename T>
class MichaelScottQueue {
private:
    struct Node {
        std::atomic<T*> data;      // 使用指针避免默认构造问题
        std::atomic<Node*> next;
        
        Node() : data(nullptr), next(nullptr) {}
        explicit Node(T* item) : data(item), next(nullptr) {}
    };
    
    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
    
public:
    /**
     * 构造函数
     * 创建一个虚拟头节点，head 和 tail 都指向它
     */
    MichaelScottQueue() {
        Node* dummy = new Node();
        head_.store(dummy, std::memory_order_relaxed);
        tail_.store(dummy, std::memory_order_relaxed);
    }
    
    /**
     * 析构函数
     * 清理所有剩余的节点
     */
    ~MichaelScottQueue() {
        Node* current = head_.load(std::memory_order_relaxed);
        while (current != nullptr) {
            Node* next = current->next.load(std::memory_order_relaxed);
            T* data = current->data.load(std::memory_order_relaxed);
            if (data != nullptr) {
                delete data;
            }
            delete current;
            current = next;
        }
    }
    
    /**
     * 入队操作
     * @param item 要入队的元素
     */
    void enqueue(const T& item) {
        // 1. 分配新节点和数据
        T* data = new T(item);
        Node* new_node = new Node(data);
        
        while (true) {
            // 2. 读取当前的 tail 和 tail->next
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = tail->next.load(std::memory_order_acquire);
            
            // 3. tail 和 tail->next 是一致的吗？
            if (tail == tail_.load(std::memory_order_acquire)) {
                if (next == nullptr) {
                    // 4a. tail 指向最后一个节点，尝试添加新节点
                    if (tail->next.compare_exchange_weak(next, new_node,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed)) {
                        // 5. 成功添加节点，现在尝试推进 tail
                        tail_.compare_exchange_weak(tail, new_node,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed);
                        break;
                    }
                } else {
                    // 4b. tail 没有指向最后一个节点，尝试推进它
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                }
            }
        }
    }
    
    /**
     * 入队操作（移动语义）
     */
    void enqueue(T&& item) {
        T* data = new T(std::move(item));
        Node* new_node = new Node(data);
        
        while (true) {
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = tail->next.load(std::memory_order_acquire);
            
            if (tail == tail_.load(std::memory_order_acquire)) {
                if (next == nullptr) {
                    if (tail->next.compare_exchange_weak(next, new_node,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed)) {
                        tail_.compare_exchange_weak(tail, new_node,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed);
                        break;
                    }
                } else {
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                }
            }
        }
    }
    
    /**
     * 出队操作
     * @param item 存储出队元素的引用
     * @return true 成功，false 队列为空
     */
    bool dequeue(T& item) {
        while (true) {
            // 1. 读取 head, tail 和 head->next
            Node* head = head_.load(std::memory_order_acquire);
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = head->next.load(std::memory_order_acquire);
            
            // 2. head, tail 和 head->next 是一致的吗？
            if (head == head_.load(std::memory_order_acquire)) {
                if (head == tail) {
                    if (next == nullptr) {
                        // 3a. 队列为空
                        return false;
                    }
                    // 3b. tail 落后了，尝试推进它
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                } else {
                    // 4. 队列不为空
                    if (next == nullptr) {
                        // 不一致的状态，重试
                        continue;
                    }
                    
                    // 5. 读取数据
                    T* data = next->data.load(std::memory_order_acquire);
                    if (data == nullptr) {
                        // 数据还没有完全初始化，重试
                        continue;
                    }
                    
                    // 6. 尝试推进 head
                    if (head_.compare_exchange_weak(head, next,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed)) {
                        // 7. 成功出队，复制数据并释放资源
                        item = *data;
                        delete data;
                        delete head;  // 删除旧的头节点
                        return true;
                    }
                }
            }
        }
    }
    
    /**
     * 检查队列是否为空
     * 注意：这是一个近似值，在高并发环境下可能不准确
     */
    bool empty() const {
        Node* head = head_.load(std::memory_order_acquire);
        Node* tail = tail_.load(std::memory_order_acquire);
        return (head == tail) && (head->next.load(std::memory_order_acquire) == nullptr);
    }
    
    /**
     * 获取队列大小的近似值
     * 注意：这个操作的时间复杂度是 O(n)，且在高并发下不准确
     */
    size_t size() const {
        size_t count = 0;
        Node* current = head_.load(std::memory_order_acquire);
        Node* next = current->next.load(std::memory_order_acquire);
        
        while (next != nullptr) {
            ++count;
            current = next;
            next = current->next.load(std::memory_order_acquire);
        }
        
        return count;
    }
};

/**
 * Michael-Scott 队列的改进版本，使用内存池减少动态分配开销
 * 
 * 这个版本展示了如何在保持算法核心不变的情况下进行性能优化：
 * 1. 预分配节点池减少 new/delete 开销
 * 2. 节点回收重用
 * 3. 缓存行对齐避免伪共享
 */
template <typename T>
class OptimizedMichaelScottQueue {
private:
    struct alignas(64) Node {  // 缓存行对齐
        std::atomic<T*> data;
        std::atomic<Node*> next;
        
        Node() : data(nullptr), next(nullptr) {}
        explicit Node(T* item) : data(item), next(nullptr) {}
    };
    
    // 简单的内存池实现
    struct NodePool {
        static constexpr size_t POOL_SIZE = 1024;
        Node pool[POOL_SIZE];
        std::atomic<Node*> free_list;
        std::atomic<size_t> allocated_count;
        
        NodePool() : allocated_count(0) {
            // 初始化空闲链表
            for (size_t i = 0; i < POOL_SIZE - 1; ++i) {
                pool[i].next.store(&pool[i + 1], std::memory_order_relaxed);
            }
            pool[POOL_SIZE - 1].next.store(nullptr, std::memory_order_relaxed);
            free_list.store(&pool[0], std::memory_order_relaxed);
        }
        
        Node* allocate() {
            Node* node = free_list.load(std::memory_order_acquire);
            while (node != nullptr) {
                Node* next = node->next.load(std::memory_order_relaxed);
                if (free_list.compare_exchange_weak(node, next,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed)) {
                    node->data.store(nullptr, std::memory_order_relaxed);
                    node->next.store(nullptr, std::memory_order_relaxed);
                    allocated_count.fetch_add(1, std::memory_order_relaxed);
                    return node;
                }
            }
            
            // 池用完了，回退到动态分配
            allocated_count.fetch_add(1, std::memory_order_relaxed);
            return new Node();
        }
        
        void deallocate(Node* node) {
            if (node >= pool && node < pool + POOL_SIZE) {
                // 这是池中的节点，回收到空闲链表
                Node* old_head = free_list.load(std::memory_order_acquire);
                do {
                    node->next.store(old_head, std::memory_order_relaxed);
                } while (!free_list.compare_exchange_weak(old_head, node,
                                                        std::memory_order_release,
                                                        std::memory_order_relaxed));
            } else {
                // 这是动态分配的节点，直接删除
                delete node;
            }
            allocated_count.fetch_sub(1, std::memory_order_relaxed);
        }
    };
    
    alignas(64) std::atomic<Node*> head_;  // 避免伪共享
    alignas(64) std::atomic<Node*> tail_;  // 避免伪共享
    NodePool node_pool_;
    
public:
    OptimizedMichaelScottQueue() {
        Node* dummy = node_pool_.allocate();
        head_.store(dummy, std::memory_order_relaxed);
        tail_.store(dummy, std::memory_order_relaxed);
    }
    
    ~OptimizedMichaelScottQueue() {
        Node* current = head_.load(std::memory_order_relaxed);
        while (current != nullptr) {
            Node* next = current->next.load(std::memory_order_relaxed);
            T* data = current->data.load(std::memory_order_relaxed);
            if (data != nullptr) {
                delete data;
            }
            node_pool_.deallocate(current);
            current = next;
        }
    }
    
    void enqueue(const T& item) {
        T* data = new T(item);
        Node* new_node = node_pool_.allocate();
        new_node->data.store(data, std::memory_order_relaxed);
        
        while (true) {
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = tail->next.load(std::memory_order_acquire);
            
            if (tail == tail_.load(std::memory_order_acquire)) {
                if (next == nullptr) {
                    if (tail->next.compare_exchange_weak(next, new_node,
                                                       std::memory_order_release,
                                                       std::memory_order_relaxed)) {
                        tail_.compare_exchange_weak(tail, new_node,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed);
                        break;
                    }
                } else {
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                }
            }
        }
    }
    
    bool dequeue(T& item) {
        while (true) {
            Node* head = head_.load(std::memory_order_acquire);
            Node* tail = tail_.load(std::memory_order_acquire);
            Node* next = head->next.load(std::memory_order_acquire);
            
            if (head == head_.load(std::memory_order_acquire)) {
                if (head == tail) {
                    if (next == nullptr) {
                        return false;  // 空队列
                    }
                    tail_.compare_exchange_weak(tail, next,
                                              std::memory_order_release,
                                              std::memory_order_relaxed);
                } else {
                    if (next == nullptr) {
                        continue;
                    }
                    
                    T* data = next->data.load(std::memory_order_acquire);
                    if (data == nullptr) {
                        continue;
                    }
                    
                    if (head_.compare_exchange_weak(head, next,
                                                  std::memory_order_release,
                                                  std::memory_order_relaxed)) {
                        item = *data;
                        delete data;
                        node_pool_.deallocate(head);
                        return true;
                    }
                }
            }
        }
    }
    
    bool empty() const {
        Node* head = head_.load(std::memory_order_acquire);
        Node* tail = tail_.load(std::memory_order_acquire);
        return (head == tail) && (head->next.load(std::memory_order_acquire) == nullptr);
    }
};

} // namespace stage3
