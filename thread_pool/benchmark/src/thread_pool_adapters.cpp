#include "../include/benchmark_framework.hpp"
#include "thread_pool/thread_pool.hpp"
#include "thread_pool/thread_pool_original.hpp"

using namespace tp_bench;

// --- CustomThreadPoolAdapter (Optimized) ---
void CustomThreadPoolAdapter::initialize(size_t thread_count) {
    pool_ = std::make_unique<tp::ThreadPool>(thread_count);
}

void CustomThreadPoolAdapter::shutdown() {
    pool_.reset();
}

std::future<void> CustomThreadPoolAdapter::submit_task(std::function<void()> task) {
    return pool_->submit(std::move(task));
}

std::future<int> CustomThreadPoolAdapter::submit_task_with_result(std::function<int()> task) {
    return pool_->submit(std::move(task));
}

// --- OriginalThreadPoolAdapter ---
void OriginalThreadPoolAdapter::initialize(size_t thread_count) {
    pool_ = std::make_unique<tp_original::ThreadPool>(thread_count);
}

void OriginalThreadPoolAdapter::shutdown() {
    pool_.reset();
}

std::future<void> OriginalThreadPoolAdapter::submit_task(std::function<void()> task) {
    return pool_->submit(std::move(task));
}

std::future<int> OriginalThreadPoolAdapter::submit_task_with_result(std::function<int()> task) {
    return pool_->submit(std::move(task));
}


// --- StdAsyncAdapter ---
void StdAsyncAdapter::initialize(size_t) {
    // std::async不需要初始化
}

void StdAsyncAdapter::shutdown() {
    // std::async不需要关闭
}

std::future<void> StdAsyncAdapter::submit_task(std::function<void()> task) {
    return std::async(std::launch::async, std::move(task));
}

std::future<int> StdAsyncAdapter::submit_task_with_result(std::function<int()> task) {
    return std::async(std::launch::async, std::move(task));
} 