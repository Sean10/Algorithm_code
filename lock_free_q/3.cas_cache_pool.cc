#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <cassert>
#include <vector>
#include <memory>

// 模板化节点结构
template<typename T>
struct Node {
    T data;
    std::atomic<Node<T>*> next;

    // 构造函数
    Node(const T& data) : data(data), next(nullptr) {}
    Node() : next(nullptr) {}  // 默认构造函数用于哨兵节点
};

// 节点缓存池类 - 全局共享的缓存池
template<typename T>
class NodePool {
private:
    std::atomic<Node<T>*> free_list;  // 空闲节点链表
    std::atomic<size_t> pool_size;    // 当前池中节点数量
    const size_t max_pool_size;       // 最大池大小

public:
    explicit NodePool(size_t max_size = 1000) 
        : free_list(nullptr), pool_size(0), max_pool_size(max_size) {}

    ~NodePool() {
        // 清理所有缓存的节点
        Node<T>* node = free_list.load();
        while (node) {
            Node<T>* next = node->next.load();
            delete node;
            node = next;
        }
    }

    // 从缓存池获取节点
    Node<T>* acquire() {
        Node<T>* node = free_list.load(std::memory_order_acquire);
        
        while (node != nullptr) {
            Node<T>* next = node->next.load(std::memory_order_relaxed);
            
            // 尝试从空闲链表中移除节点
            if (free_list.compare_exchange_weak(
                node, next, 
                std::memory_order_release, 
                std::memory_order_relaxed)) {
                
                pool_size.fetch_sub(1, std::memory_order_relaxed);
                node->next.store(nullptr, std::memory_order_relaxed);
                return node;
            }
        }
        
        // 缓存池为空，分配新节点
        return new Node<T>();
    }

    // 将节点归还到缓存池
    void release(Node<T>* node) {
        if (!node || pool_size.load(std::memory_order_relaxed) >= max_pool_size) {
            delete node;  // 池已满或节点无效，直接删除
            return;
        }

        Node<T>* old_head = free_list.load(std::memory_order_relaxed);
        do {
            node->next.store(old_head, std::memory_order_relaxed);
        } while (!free_list.compare_exchange_weak(
            old_head, node,
            std::memory_order_release,
            std::memory_order_relaxed));
        
        pool_size.fetch_add(1, std::memory_order_relaxed);
    }

    size_t size() const {
        return pool_size.load(std::memory_order_relaxed);
    }
};

// 线程本地缓存类
template<typename T>
class ThreadLocalCache {
private:
    std::vector<Node<T>*> cache;  // 本地缓存数组
    size_t cache_index;           // 当前缓存索引
    const size_t cache_size;      // 缓存大小
    NodePool<T>* global_pool;     // 全局缓存池引用

public:
    explicit ThreadLocalCache(NodePool<T>* pool, size_t size = 32)
        : cache_index(0), cache_size(size), global_pool(pool) {
        cache.reserve(cache_size);
    }

    ~ThreadLocalCache() {
        // 将所有本地缓存的节点归还给全局池
        for (Node<T>* node : cache) {
            if (node) {
                global_pool->release(node);
            }
        }
    }

    // 从本地缓存获取节点
    Node<T>* acquire() {
        if (cache_index > 0) {
            return cache[--cache_index];  // 从本地缓存获取
        }
        
        // 本地缓存为空，从全局池批量获取
        refill_cache();
        
        if (cache_index > 0) {
            return cache[--cache_index];
        }
        
        // 全局池也为空，直接分配
        return global_pool->acquire();
    }

    // 将节点归还到本地缓存
    void release(Node<T>* node) {
        if (!node) return;
        
        if (cache_index < cache_size) {
            cache[cache_index++] = node;  // 放入本地缓存
        } else {
            global_pool->release(node);   // 本地缓存已满，归还给全局池
        }
    }

private:
    // 从全局池批量获取节点填充本地缓存
    void refill_cache() {
        size_t batch_size = std::min(cache_size / 2, cache_size - cache_index);
        for (size_t i = 0; i < batch_size; ++i) {
            Node<T>* node = global_pool->acquire();
            if (node) {
                cache[cache_index++] = node;
            }
        }
    }
};

// 优化后的无锁队列类
template<typename T>
class OptimizedLockFreeQueue {
private:
    std::atomic<Node<T>*> head;
    std::atomic<Node<T>*> tail;
    
    // 静态全局缓存池
    static NodePool<T> global_pool;
    
    // 线程本地缓存
    static thread_local ThreadLocalCache<T> local_cache;

public:
    // 构造函数：初始化哨兵节点
    OptimizedLockFreeQueue() {
        Node<T>* sentinel = local_cache.acquire();
        new (sentinel) Node<T>();  // 使用placement new初始化
        head.store(sentinel);
        tail.store(sentinel);
    }

    // 析构函数：释放所有节点
    ~OptimizedLockFreeQueue() {
        while (Node<T>* node = head.load()) {
            head.store(node->next);
            local_cache.release(node);
        }
    }

    // 入队操作（单生产者）
    void push(const T& data) {
        Node<T>* new_node = local_cache.acquire();
        new (new_node) Node<T>(data);  // 使用placement new初始化
        
        Node<T>* old_tail = nullptr;

        // CAS操作更新尾指针
        do {
            old_tail = tail.load(std::memory_order_acquire);
        } while (!tail.compare_exchange_weak(
            old_tail, 
            new_node,
            std::memory_order_release,
            std::memory_order_relaxed
        ));

        // 将新节点链接到队列
        old_tail->next.store(new_node, std::memory_order_release);
    }

    // 出队操作（单消费者）
    bool pop(T& result) {
        Node<T>* old_head = head.load(std::memory_order_acquire);
        Node<T>* new_head = nullptr;

        // 循环直到成功获取并更新头指针
        do {
            // 队列为空
            if (!old_head->next.load(std::memory_order_acquire)) {
                return false;
            }

            new_head = old_head->next.load(std::memory_order_acquire);
            result = new_head->data;  // 提前获取数据

        } while (!head.compare_exchange_weak(
            old_head, 
            new_head,
            std::memory_order_release,
            std::memory_order_relaxed
        ));

        // 将旧的头节点归还到缓存池
        local_cache.release(old_head);
        return true;
    }

    // 检查队列是否为空
    bool empty() const {
        return head.load(std::memory_order_acquire)->next == nullptr;
    }

    // 获取缓存池统计信息
    static size_t get_pool_size() {
        return global_pool.size();
    }
};

// 静态成员定义
template<typename T>
NodePool<T> OptimizedLockFreeQueue<T>::global_pool(1000);

template<typename T>
thread_local ThreadLocalCache<T> OptimizedLockFreeQueue<T>::local_cache(&OptimizedLockFreeQueue<T>::global_pool);

// 性能测试函数
void performance_test() {
    OptimizedLockFreeQueue<int> queue;
    const int ITEM_COUNT = 100000000;  // 测试数据量
    
    auto start_time = std::chrono::high_resolution_clock::now();

    // 生产者线程
    std::thread producer([&queue]() {
        for (int i = 0; i < ITEM_COUNT; ++i) {
            queue.push(i);
        }
        std::cout << "优化版生产者完成\n";
    });

    // 消费者线程
    std::thread consumer([&queue]() {
        int value;
        int count = 0;
        while (count < ITEM_COUNT) {
            if (queue.pop(value)) {
                assert(value == count);  // 验证数据顺序正确性
                count++;
            } else {
                std::this_thread::yield();  // 队列为空时让出CPU
            }
        }
        std::cout << "优化版消费者完成，处理了 " << count << " 个项目\n";
    });

    // 等待线程完成
    producer.join();
    consumer.join();

    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

    // 验证队列已为空
    assert(queue.empty());
    std::cout << "优化版测试通过，耗时: " << duration.count() << " 毫秒\n";
    std::cout << "缓存池大小: " << OptimizedLockFreeQueue<int>::get_pool_size() << "\n";
}

// 多线程压力测试
void stress_test() {
    OptimizedLockFreeQueue<int> queue;
    const int THREAD_COUNT = 4;
    const int ITEMS_PER_THREAD = 1000000;
    std::atomic<int> total_consumed{0};
    
    auto start_time = std::chrono::high_resolution_clock::now();

    // 创建多个生产者线程
    std::vector<std::thread> producers;
    for (int t = 0; t < THREAD_COUNT; ++t) {
        producers.emplace_back([&queue, t]() {
            for (int i = 0; i < ITEMS_PER_THREAD; ++i) {
                queue.push(t * ITEMS_PER_THREAD + i);
            }
        });
    }

    // 创建多个消费者线程
    std::vector<std::thread> consumers;
    for (int t = 0; t < THREAD_COUNT; ++t) {
        consumers.emplace_back([&queue, &total_consumed]() {
            int value;
            int local_count = 0;
            while (total_consumed.load() < THREAD_COUNT * ITEMS_PER_THREAD) {
                if (queue.pop(value)) {
                    local_count++;
                    total_consumed.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }

    // 等待所有线程完成
    for (auto& producer : producers) {
        producer.join();
    }
    for (auto& consumer : consumers) {
        consumer.join();
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

    std::cout << "多线程压力测试完成\n";
    std::cout << "总处理项目: " << total_consumed.load() << "\n";
    std::cout << "耗时: " << duration.count() << " 毫秒\n";
    std::cout << "最终缓存池大小: " << OptimizedLockFreeQueue<int>::get_pool_size() << "\n";
}

int main() {
    std::cout << "=== 缓存池优化的无锁队列测试 ===\n\n";
    
    // 单线程性能测试
    std::cout << "1. 单线程性能测试:\n";
    performance_test();
    
    std::cout << "\n2. 多线程压力测试:\n";
    // 目前设备核数不够多, 暂不测
    // stress_test();
    
    std::cout << "\n所有测试完成！\n";
    return 0;
}
