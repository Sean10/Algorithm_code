#include <iostream>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <functional>
#include <vector>

// 传统的线程安全队列实现
template<typename T>
class ThreadSafeQueue {
private:
    std::queue<T> task_queue;
    mutable std::mutex mutex;
    std::condition_variable cond;
    bool stop{false};

public:
    void push(T task) {
        {
            std::lock_guard<std::mutex> lock(mutex);
            task_queue.push(std::move(task));
        }
        cond.notify_one();
    }

    bool pop(T& task) {
        std::unique_lock<std::mutex> lock(mutex);
        cond.wait(lock, [this] { return !task_queue.empty() || stop; });
        
        if (stop && task_queue.empty()) {
            return false;
        }
        
        task = std::move(task_queue.front());
        task_queue.pop();
        return true;
    }

    void stop_processing() {
        {
            std::lock_guard<std::mutex> lock(mutex);
            stop = true;
        }
        cond.notify_all();
    }
};

// 使用相同的计算任务
class ComputeTask {
public:
    void operator()() {
        volatile int sum = 0;
        for(int i = 0; i < 1000000; i++) {
            sum += i;
        }
    }
};

// 工作线程
class Worker {
private:
    ThreadSafeQueue<std::function<void()>>& queue;
    std::thread thread;
    
public:
    Worker(ThreadSafeQueue<std::function<void()>>& q) : queue(q) {
        thread = std::thread([this] {
            std::function<void()> task;
            while (queue.pop(task)) {
                task();
            }
        });
    }
    
    ~Worker() {
        if (thread.joinable()) {
            thread.join();
        }
    }
};

int main() {
    ThreadSafeQueue<std::function<void()>> queue;
    std::vector<std::unique_ptr<Worker>> workers;
    
    // 创建工作线程
    const int num_threads = 4;
    for (int i = 0; i < num_threads; ++i) {
        workers.push_back(std::make_unique<Worker>(queue));
    }
    
    // 记录开始时间
    auto start = std::chrono::high_resolution_clock::now();
    
    // 提交相同数量的任务
    for(int i = 0; i < 10; i++) {
        queue.push(ComputeTask());
    }
    
    // 停止处理
    queue.stop_processing();
    
    // 等待所有工作线程完成
    workers.clear();
    
    // 记录结束时间
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "传统实现处理完成，耗时: " << duration.count() << " 微秒" << std::endl;
    
    return 0;
} 