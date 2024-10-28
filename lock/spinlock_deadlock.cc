#include <pthread.h>
#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>

class SpinLock {
    std::atomic_flag flag = ATOMIC_FLAG_INIT;
public:
    void lock() {
        while (flag.test_and_set(std::memory_order_acquire)) {
            // 自旋等待，不让出CPU
            #if defined(__x86_64__)
            __asm__ volatile ("pause");
            #endif
        }
    }
    
    void unlock() {
        flag.clear(std::memory_order_release);
    }
};

SpinLock spin_a;
SpinLock spin_b;

void* thread_1(void*) {
    while (true) {
        std::cout << "Thread 1 trying to lock spin_a\n";
        spin_a.lock();
        std::cout << "Thread 1 locked spin_a, trying to lock spin_b\n";
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        spin_b.lock();  // 这里会死锁
        
        // 永远不会执行到这里
        spin_b.unlock();
        spin_a.unlock();
    }
    return nullptr;
}

void* thread_2(void*) {
    while (true) {
        std::cout << "Thread 2 trying to lock spin_b\n";
        spin_b.lock();
        std::cout << "Thread 2 locked spin_b, trying to lock spin_a\n";
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        spin_a.lock();  // 这里会死锁
        
        // 永远不会执行到这里
        spin_a.unlock();
        spin_b.unlock();
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
