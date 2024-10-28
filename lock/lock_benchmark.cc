#include <pthread.h>
#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>
#include <vector>

// 自旋锁实现
class SpinLock {
    std::atomic_flag flag = ATOMIC_FLAG_INIT;
public:
    void lock() {
        while (flag.test_and_set(std::memory_order_acquire)) {
            // 自旋等待
        }
    }
    void unlock() {
        flag.clear(std::memory_order_release);
    }
};

// 测试函数
template<typename Lock>
void benchmark_lock(Lock& lock, int num_threads, int iterations, const std::string& lock_name) {
    std::vector<std::thread> threads;
    std::vector<double> latencies(num_threads);
    volatile long counter = 0;

    auto worker = [&](int thread_id) {
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < iterations; i++) {
            lock.lock();
            counter++; // 临界区操作
            lock.unlock();
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        latencies[thread_id] = std::chrono::duration<double, std::micro>(end - start).count() / iterations;
    };

    // 启动所有线程
    for (int i = 0; i < num_threads; i++) {
        threads.emplace_back(worker, i);
    }

    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }

    // 计算平均延迟
    double avg_latency = 0;
    for (double lat : latencies) {
        avg_latency += lat;
    }
    avg_latency /= num_threads;

    std::cout << lock_name << "结果:\n"
              << "- 最终计数器值: " << counter << "\n"
              << "- 平均每次加锁操作延迟: " << avg_latency << " 微秒\n\n";
}

int main() {
    const int NUM_THREADS = 4;
    const int ITERATIONS = 100000;

    // 测试互斥锁
    std::mutex mutex;
    benchmark_lock(mutex, NUM_THREADS, ITERATIONS, "互斥锁");

    // 测试自旋锁
    SpinLock spinlock;
    benchmark_lock(spinlock, NUM_THREADS, ITERATIONS, "自旋锁");

    return 0;
}
