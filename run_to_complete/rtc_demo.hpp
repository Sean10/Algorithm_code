#pragma once
#include <queue>
#include <functional>
#include <memory>
#include <atomic>

// RTC任务队列的实现
template<typename T>
class RTCQueue {
private:
    // 使用无锁队列存储任务
    std::queue<T> task_queue;
    std::atomic<bool> processing{false};

public:
    // 提交任务到队列
    void submit(T&& task) {
        task_queue.push(std::move(task));
    }

    // 执行队列中的所有任务
    void process() {
        if (processing.exchange(true)) {
            return; // 已有线程在处理
        }

        while (!task_queue.empty()) {
            auto& task = task_queue.front();
            // 确保任务执行到完成
            task();
            task_queue.pop();
        }

        processing.store(false);
    }
}; 