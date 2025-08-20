#include <iostream>
#include <thread>
#include <chrono>
#include <vector>
#include "stage1_basics/mutex_queue.hpp"
#include "stage2_spsc/spsc_ring_buffer.hpp"

using namespace std::chrono_literals;

void demo_mutex_queue() {
    std::cout << "\n=== 互斥锁队列示例 ===" << std::endl;
    
    stage1::MutexQueue<int> queue(10);
    constexpr int num_items = 20;
    
    // 生产者线程
    std::thread producer([&queue]() {
        for (int i = 1; i <= num_items; ++i) {
            queue.push(i);
            std::cout << "生产: " << i << std::endl;
            std::this_thread::sleep_for(100ms);
        }
    });
    
    // 消费者线程
    std::thread consumer([&queue]() {
        for (int i = 1; i <= num_items; ++i) {
            int value;
            if (queue.pop_for(value, 1s)) {
                std::cout << "消费: " << value << std::endl;
            }
            std::this_thread::sleep_for(150ms);
        }
    });
    
    producer.join();
    consumer.join();
    
    std::cout << "互斥锁队列示例完成" << std::endl;
}

void demo_spsc_queue() {
    std::cout << "\n=== SPSC无锁队列示例 ===" << std::endl;
    
    stage2::SPSCRingBuffer<int> queue(16); // 必须是2的幂
    constexpr int num_items = 20;
    
    // 生产者线程
    std::thread producer([&queue]() {
        for (int i = 1; i <= num_items; ++i) {
            while (!queue.push(i)) {
                std::this_thread::yield();
            }
            std::cout << "生产: " << i << std::endl;
            std::this_thread::sleep_for(80ms);
        }
    });
    
    // 消费者线程
    std::thread consumer([&queue]() {
        int consumed = 0;
        while (consumed < num_items) {
            int value;
            if (queue.pop(value)) {
                std::cout << "消费: " << value << std::endl;
                consumed++;
            } else {
                std::this_thread::sleep_for(10ms);
            }
        }
    });
    
    producer.join();
    consumer.join();
    
    std::cout << "SPSC无锁队列示例完成" << std::endl;
}

void compare_performance() {
    std::cout << "\n=== 性能对比示例 ===" << std::endl;
    
    constexpr int num_operations = 10000;
    
    // 测试互斥锁队列
    {
        stage1::MutexQueue<int> queue(1000);
        auto start = std::chrono::high_resolution_clock::now();
        
        std::thread producer([&queue]() {
            for (int i = 0; i < num_operations; ++i) {
                queue.push(i);
            }
        });
        
        std::thread consumer([&queue]() {
            for (int i = 0; i < num_operations; ++i) {
                int value;
                queue.pop(value);
            }
        });
        
        producer.join();
        consumer.join();
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "互斥锁队列: " << duration.count() << " 微秒 (" 
                  << num_operations << " 操作)" << std::endl;
    }
    
    // 测试SPSC队列
    {
        stage2::SPSCRingBuffer<int> queue(1024);
        auto start = std::chrono::high_resolution_clock::now();
        
        std::thread producer([&queue]() {
            for (int i = 0; i < num_operations; ++i) {
                while (!queue.push(i)) {
                    std::this_thread::yield();
                }
            }
        });
        
        std::thread consumer([&queue]() {
            for (int i = 0; i < num_operations; ++i) {
                int value;
                while (!queue.pop(value)) {
                    std::this_thread::yield();
                }
            }
        });
        
        producer.join();
        consumer.join();
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "SPSC无锁队列: " << duration.count() << " 微秒 (" 
                  << num_operations << " 操作)" << std::endl;
    }
}

int main() {
    std::cout << "生产者-消费者队列示例程序" << std::endl;
    std::cout << "本程序演示了不同类型队列的使用方法和性能特征" << std::endl;
    
    try {
        demo_mutex_queue();
        demo_spsc_queue();
        compare_performance();
        
        std::cout << "\n=== 示例程序完成 ===" << std::endl;
        std::cout << "更多高级功能请参考 guide.md 和测试代码" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
