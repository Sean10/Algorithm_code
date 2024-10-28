#include <pthread.h>
#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>
#include <vector>
#include <mutex>    // 添加 mutex 头文件
#include <sched.h>  // 添加 sched.h 用于CPU亲和性设置

// 自旋锁实现
class SpinLock {
    std::atomic_flag flag;
public:
    SpinLock() : flag(ATOMIC_FLAG_INIT) {}
    
    void lock() {
        while (flag.test_and_set(std::memory_order_acquire)) {
            #if defined(__x86_64__)
            __asm__ volatile ("pause");
            #endif
        }
    }
    
    void unlock() {
        flag.clear(std::memory_order_release);
    }
};

// 测试函数
template<typename Lock>
void benchmark_lock(Lock& lock, int num_threads, int iterations, 
                   const std::string& lock_name, int hold_time_us) {
    std::vector<std::thread> threads(num_threads);
    std::vector<double> latencies(num_threads);
    std::atomic<long> counter{0};
    std::atomic<bool> start{false};
    
    auto worker = [&](int thread_id) {
        while (!start.load(std::memory_order_acquire)) {
            std::this_thread::yield();
        }
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < iterations; i++) {
            lock.lock();
            counter.fetch_add(1, std::memory_order_relaxed);
            
            // 模拟临界区工作负载
            if (hold_time_us > 0) {
                auto work_start = std::chrono::high_resolution_clock::now();
                while (true) {
                    auto now = std::chrono::high_resolution_clock::now();
                    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
                        now - work_start).count();
                    if (elapsed >= hold_time_us) break;
                }
            }
            
            lock.unlock();
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        latencies[thread_id] = std::chrono::duration<double, std::micro>(
            end_time - start_time).count() / iterations;
    };

    for (int i = 0; i < num_threads; i++) {
        threads[i] = std::thread(worker, i);
    }
    
    start.store(true, std::memory_order_release);

    for (auto& t : threads) {
        t.join();
    }

    double avg_latency = 0;
    for (double lat : latencies) {
        avg_latency += lat;
    }
    avg_latency /= num_threads;

    std::cout << lock_name << "结果 (持锁时间: " << hold_time_us << "微秒):\n"
              << "- 最终计数器值: " << counter << "\n"
              << "- 平均每次加锁操作延迟: " << avg_latency << " 微秒\n"
              << "- 每秒操作次数: " << 1000000.0 / avg_latency << "\n\n";
}

void run_benchmark(int num_threads, int iterations, int hold_time_us) {
    std::cout << "\n=== 测试场景 ===\n"
              << "线程数: " << num_threads << "\n"
              << "每线程迭代次数: " << iterations << "\n"
              << "持锁时间: " << hold_time_us << " 微秒\n\n";

    std::mutex mutex;
    benchmark_lock(mutex, num_threads, iterations, "互斥锁", hold_time_us);

    SpinLock spinlock;
    benchmark_lock(spinlock, num_threads, iterations, "自旋锁", hold_time_us);
}

int main() {
    const int NUM_THREADS = 4;
    const int ITERATIONS = 10000;

    std::cout << "CPU核心数: " << std::thread::hardware_concurrency() << "\n";

    // 测试不同持锁时间的场景
    std::vector<int> hold_times = {0, 1, 10, 100};
    
    for (int hold_time : hold_times) {
        run_benchmark(NUM_THREADS, ITERATIONS, hold_time);
    }

    return 0;
}
