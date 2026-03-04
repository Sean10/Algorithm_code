#pragma once

#include <ranges>
#include <coroutine>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <algorithm>
#include <chrono>
#include <optional>

namespace stage6 {

/**
 * C++23 Ranges 库在生产者消费者模型中的应用
 */
template<typename T>
class RangesOptimizedQueue {
private:
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    const size_t capacity_;

public:
    explicit RangesOptimizedQueue(size_t capacity) : capacity_(capacity) {}

    bool push(const T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return queue_.size() < capacity_; });
        
        queue_.push(item);
        cv_.notify_one();
        return true;
    }

    bool pop(T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return !queue_.empty(); });
        
        item = queue_.front();
        queue_.pop();
        cv_.notify_one();
        return true;
    }

    /**
     * 使用 Ranges 库批量处理数据
     */
    template<std::ranges::input_range R>
    void push_batch(R&& range) {
        // 使用 ranges 进行数据预处理
        auto processed_data = range 
            | std::views::transform([](const auto& item) { 
                return item * 2;  // 示例：数据变换
              })
            | std::views::filter([](const auto& item) { 
                return item > 0;  // 示例：数据过滤
              });

        for (const auto& item : processed_data) {
            push(item);
        }
    }

    /**
     * 使用 Ranges 库批量获取数据
     */
    std::vector<T> pop_batch(size_t max_count) {
        std::vector<T> result;
        result.reserve(max_count);
        
        for (size_t i = 0; i < max_count; ++i) {
            T item;
            if (pop(item)) {
                result.push_back(item);
            } else {
                break;
            }
        }
        
        return result;
    }

    /**
     * 使用 Ranges 库进行数据分析
     */
    auto analyze_queue_data() {
        std::vector<T> temp_data;
        
        // 临时获取队列数据进行分析
        {
            std::lock_guard<std::mutex> lock(mutex_);
            std::queue<T> temp_queue = queue_;
            while (!temp_queue.empty()) {
                temp_data.push_back(temp_queue.front());
                temp_queue.pop();
            }
        }
        
        // 使用 ranges 进行数据分析
        auto analysis = temp_data 
            | std::views::transform([](const T& item) { return static_cast<double>(item); })
            | std::views::filter([](double val) { return val > 0; });
        
        // 计算统计信息
        double sum = 0;
        size_t count = 0;
        for (double val : analysis) {
            sum += val;
            count++;
        }
        
        return std::make_pair(count > 0 ? sum / count : 0.0, count);
    }
};

/**
 * C++20 协程在异步生产者消费者模型中的应用
 */
template<typename T>
class CoroutineQueue {
private:
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    const size_t capacity_;

public:
    explicit CoroutineQueue(size_t capacity) : capacity_(capacity) {}

    /**
     * 协程任务类型
     */
    struct Task {
        struct promise_type {
            Task get_return_object() {
                return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
            }
            
            std::suspend_never initial_suspend() { return {}; }
            std::suspend_never final_suspend() noexcept { return {}; }
            void return_void() {}
            void unhandled_exception() {}
        };

        std::coroutine_handle<promise_type> handle;
        
        Task(std::coroutine_handle<promise_type> h) : handle(h) {}
        
        ~Task() {
            if (handle) {
                handle.destroy();
            }
        }
        
        // 禁止拷贝，允许移动
        Task(const Task&) = delete;
        Task& operator=(const Task&) = delete;
        Task(Task&& other) noexcept : handle(std::exchange(other.handle, {})) {}
        Task& operator=(Task&& other) noexcept {
            if (this != &other) {
                if (handle) {
                    handle.destroy();
                }
                handle = std::exchange(other.handle, {});
            }
            return *this;
        }
    };

    /**
     * 异步生产者协程
     */
    Task async_producer(std::vector<T> data) {
        for (const auto& item : data) {
            // 异步推入数据
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] { return queue_.size() < capacity_; });
                queue_.push(item);
            }
            cv_.notify_one();
            
            // 协程挂起点，允许其他协程运行
            co_await std::suspend_always{};
        }
    }

    /**
     * 异步消费者协程
     */
    Task async_consumer(size_t count, std::vector<T>& result) {
        result.reserve(count);
        
        for (size_t i = 0; i < count; ++i) {
            T item;
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] { return !queue_.empty(); });
                item = queue_.front();
                queue_.pop();
            }
            cv_.notify_one();
            
            result.push_back(item);
            
            // 协程挂起点
            co_await std::suspend_always{};
        }
    }

    /**
     * 同步方法（用于非协程环境）
     */
    bool push(const T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return queue_.size() < capacity_; });
        
        queue_.push(item);
        cv_.notify_one();
        return true;
    }

    bool pop(T& item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return !queue_.empty(); });
        
        item = queue_.front();
        queue_.pop();
        cv_.notify_one();
        return true;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }
};

/**
 * 生成器协程 - 用于异步数据生成
 */
template<typename T>
struct Generator {
    struct promise_type {
        T current_value;
        
        Generator get_return_object() {
            return Generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        
        std::suspend_always yield_value(T value) {
            current_value = value;
            return {};
        }
        
        void return_void() {}
        void unhandled_exception() {}
    };

    std::coroutine_handle<promise_type> handle;
    
    Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    
    ~Generator() {
        if (handle) {
            handle.destroy();
        }
    }
    
    // 禁止拷贝，允许移动
    Generator(const Generator&) = delete;
    Generator& operator=(const Generator&) = delete;
    Generator(Generator&& other) noexcept : handle(std::exchange(other.handle, {})) {}
    Generator& operator=(Generator&& other) noexcept {
        if (this != &other) {
            if (handle) {
                handle.destroy();
            }
            handle = std::exchange(other.handle, {});
        }
        return *this;
    }

    bool move_next() {
        if (handle && !handle.done()) {
            handle.resume();
            return !handle.done();
        }
        return false;
    }

    T current_value() {
        return handle.promise().current_value;
    }
};

/**
 * 数据生成器协程示例
 */
inline Generator<int> fibonacci_generator(int count) {
    int a = 0, b = 1;
    for (int i = 0; i < count; ++i) {
        co_yield a;
        int temp = a + b;
        a = b;
        b = temp;
    }
}

/**
 * 使用协程的异步数据处理管道
 */
template<typename T>
class AsyncProcessingPipeline {
private:
    CoroutineQueue<T> input_queue_;
    CoroutineQueue<T> output_queue_;

public:
    AsyncProcessingPipeline(size_t capacity) 
        : input_queue_(capacity), output_queue_(capacity) {}

    /**
     * 异步处理管道协程
     */
    typename CoroutineQueue<T>::Task process_pipeline() {
        while (true) {
            T item;
            if (input_queue_.pop(item)) {
                // 处理数据（示例：简单变换）
                T processed_item = item * 2;
                output_queue_.push(processed_item);
                
                // 协程挂起点
                co_await std::suspend_always{};
            }
        }
    }

    bool push_input(const T& item) {
        return input_queue_.push(item);
    }

    bool pop_output(T& item) {
        return output_queue_.pop(item);
    }

    size_t input_size() const { return input_queue_.size(); }
    size_t output_size() const { return output_queue_.size(); }
};

} // namespace stage6
