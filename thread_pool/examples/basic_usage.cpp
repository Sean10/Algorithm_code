#include <chrono>
#include <iostream>
#include <random>
#include <string>
#include "thread_pool/thread_pool.hpp"

// 模拟耗时计算任务
int compute_task(int input) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(100, 500);
    
    // 模拟计算延迟
    std::this_thread::sleep_for(std::chrono::milliseconds(dis(gen)));
    return input * input;
}

int main() {
    // 创建线程池，使用系统默认线程数
    tp::ThreadPool pool;
    
    std::cout << "线程池创建完成，工作线程数: " << pool.thread_count() << std::endl;

    // 存储任务的future结果
    std::vector<std::future<int>> results;

    // 提交多个任务
    for (int i = 0; i < 10; ++i) {
        results.emplace_back(
            pool.submit([i] { 
                std::cout << "处理任务 " << i << " 在线程 " 
                         << std::this_thread::get_id() << std::endl;
                return compute_task(i);
            })
        );
    }

    // 获取并打印结果
    for (size_t i = 0; i < results.size(); ++i) {
        std::cout << "任务 " << i << " 结果: " << results[i].get() << std::endl;
    }

    std::cout << "所有任务完成！" << std::endl;
    return 0;
} 