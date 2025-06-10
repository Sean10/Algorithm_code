#ifndef THREAD_POOL_HPP
#define THREAD_POOL_HPP

#include <atomic>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <thread>
#include <type_traits>
#include <vector>

namespace tp {

// 为每个线程设计的、可被窃取的线程安全队列
template <typename T>
class StealableQueue {
private:
    std::deque<T> queue_;
    mutable std::mutex mutex_;

public:
    StealableQueue() = default;
    StealableQueue(const StealableQueue &) = delete;
    StealableQueue &operator=(const StealableQueue &) = delete;

    // 从队列前端推入任务 (供所属线程使用)
    void push(T item) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push_front(item);
    }

    // 从队列前端弹出任务 (供所属线程使用)
    bool pop(T &item) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return false;
        }
        item = std::move(queue_.front());
        queue_.pop_front();
        return true;
    }

    // 从队列后端窃取任务 (供其他线程使用)
    bool steal(T &item) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return false;
        }
        item = std::move(queue_.back());
        queue_.pop_back();
        return true;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }
};

class ThreadPool {
private:
    using Task = std::function<void()>;

    std::vector<std::thread> workers_;
    std::vector<std::unique_ptr<StealableQueue<Task>>> queues_;
    std::atomic<bool> stop_{false};
    std::atomic<size_t> next_queue_{0};

public:
    explicit ThreadPool(size_t thread_count = std::thread::hardware_concurrency()) {
        if (thread_count == 0) thread_count = 1;

        workers_.reserve(thread_count);
        queues_.reserve(thread_count);

        for (size_t i = 0; i < thread_count; ++i) {
            queues_.emplace_back(std::make_unique<StealableQueue<Task>>());
        }

        for (size_t i = 0; i < thread_count; ++i) {
            workers_.emplace_back([this, i] {
                while (!stop_) {
                    Task task;
                    if (queues_[i]->pop(task)) {
                        task();
                        continue;
                    }
                    
                    bool stolen = false;
                    for (size_t j = 1; j < queues_.size(); ++j) {
                        if (queues_[(i + j) % queues_.size()]->steal(task)) {
                            stolen = true;
                            break;
                        }
                    }
                    if (stolen) {
                        task();
                    } else {
                        std::this_thread::yield();
                    }
                }
            });
        }
    }

    ~ThreadPool() {
        stop_ = true;
        for (auto &worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    ThreadPool(const ThreadPool &) = delete;
    ThreadPool &operator=(const ThreadPool &) = delete;

    template <typename F, typename... Args>
    auto submit(F &&f, Args &&...args) -> std::future<typename std::invoke_result_t<F, Args...>> {
        using return_type = typename std::invoke_result_t<F, Args...>;

        auto task_ptr = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...));

        if (stop_) {
            throw std::runtime_error("submit on stopped ThreadPool");
        }

        auto queue_index = next_queue_.fetch_add(1) % queues_.size();
        queues_[queue_index]->push([task_ptr]() { (*task_ptr)(); });

        return task_ptr->get_future();
    }

    size_t thread_count() const { return workers_.size(); }

    size_t queue_size() const {
        size_t total_size = 0;
        for (const auto &q : queues_) {
            total_size += q->size();
        }
        return total_size;
    }
};

} // namespace tp

#endif // THREAD_POOL_HPP 