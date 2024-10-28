#include <pthread.h>
#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>
#include <mutex>

std::mutex mutex_a;
std::mutex mutex_b;

void* thread_1(void*) {
    while (true) {
        std::cout << "Thread 1 trying to lock mutex_a\n";
        mutex_a.lock();
        std::cout << "Thread 1 locked mutex_a, trying to lock mutex_b\n";
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        mutex_b.lock();  // 这里会死锁
        
        // 永远不会执行到这里
        mutex_b.unlock();
        mutex_a.unlock();
    }
    return nullptr;
}

void* thread_2(void*) {
    while (true) {
        std::cout << "Thread 2 trying to lock mutex_b\n";
        mutex_b.lock();
        std::cout << "Thread 2 locked mutex_b, trying to lock mutex_a\n";
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        mutex_a.lock();  // 这里会死锁
        
        // 永远不会执行到这里
        mutex_a.unlock();
        mutex_b.unlock();
    }
    return nullptr;
}

int main() {
    pthread_t t1, t2;
    
    // 创建线程
    pthread_create(&t1, nullptr, thread_1, nullptr);
    pthread_create(&t2, nullptr, thread_2, nullptr);
    
    // 等待线程结束（实际上不会结束）
    pthread_join(t1, nullptr);
    pthread_join(t2, nullptr);
    
    return 0;
}
