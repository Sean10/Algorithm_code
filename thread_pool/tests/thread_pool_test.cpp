#include <gtest/gtest.h>
#include "thread_pool/thread_pool.hpp"
#include <chrono>
#include <numeric>

class ThreadPoolTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(ThreadPoolTest, SubmitTasks) {
    tp::ThreadPool pool(4);  // 使用4个线程
    
    std::vector<std::future<int>> results;
    
    // 提交10个任务
    for (int i = 0; i < 10; ++i) {
        results.emplace_back(pool.submit([](int value) { return value * 2; }, i));
    }
    
    // 验证结果
    for (int i = 0; i < 10; ++i) {
        EXPECT_EQ(results[i].get(), i * 2);
    }
}

TEST_F(ThreadPoolTest, ExceptionHandling) {
    tp::ThreadPool pool(2);
    
    // 提交一个会抛出异常的任务
    auto future = pool.submit([]() -> int {
        throw std::runtime_error("Test exception");
        return 42;
    });
    
    EXPECT_THROW(future.get(), std::runtime_error);
}

TEST_F(ThreadPoolTest, StressTest) {
    tp::ThreadPool pool(8);
    const int NUM_TASKS = 1000;
    
    std::vector<std::future<int>> results;
    results.reserve(NUM_TASKS);
    
    // 提交大量任务
    for (int i = 0; i < NUM_TASKS; ++i) {
        results.emplace_back(pool.submit([](int value) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            return value;
        }, i));
    }
    
    // 验证所有任务都正确完成
    for (int i = 0; i < NUM_TASKS; ++i) {
        EXPECT_EQ(results[i].get(), i);
    }
} 