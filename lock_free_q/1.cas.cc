#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <cassert>

// 模板化节点结构
template<typename T>
struct Node {
    T data;
    std::atomic<Node<T>*> next;  // 明确指定模板参数

    // 构造函数
    Node(const T& data) : data(data), next(nullptr) {}
};

// 无锁队列类
template<typename T>
class LockFreeQueue {
private:
    std::atomic<Node<T>*> head;  // 明确指定模板参数
    std::atomic<Node<T>*> tail;  // 明确指定模板参数

public:
    // 构造函数：初始化哨兵节点
    LockFreeQueue() {
        Node<T>* sentinel = new Node<T>(T());  // 明确指定模板参数
        head.store(sentinel);
        tail.store(sentinel);
    }

    // 析构函数：释放所有节点
    ~LockFreeQueue() {
        while (Node<T>* node = head.load()) {  // 明确指定模板参数
            head.store(node->next);
            delete node;
        }
    }

    // 入队操作（单生产者）
    void push(const T& data) {
        Node<T>* new_node = new Node<T>(data);  // 明确指定模板参数
        Node<T>* old_tail = nullptr;  // 明确指定模板参数

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
        Node<T>* old_head = head.load(std::memory_order_acquire);  // 明确指定模板参数
        Node<T>* new_head = nullptr;  // 明确指定模板参数

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

        // 释放旧的头节点（原哨兵节点）
        delete old_head;
        return true;
    }

    // 检查队列是否为空
    bool empty() const {
        return head.load(std::memory_order_acquire)->next == nullptr;
    }
};

// 测试函数
int main() {
    LockFreeQueue<int> queue;
    const int ITEM_COUNT = 100000000;  // 测试数据量

    // 生产者线程
    std::thread producer([&queue]() {
        for (int i = 0; i < ITEM_COUNT; ++i) {
            queue.push(i);
        }
        std::cout << "Producer finished\n";
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
        std::cout << "Consumer finished, processed " << count << " items\n";
    });

    // 等待线程完成
    producer.join();
    consumer.join();

    // 验证队列已为空
    assert(queue.empty());
    std::cout << "All tests passed\n";

    return 0;
}

