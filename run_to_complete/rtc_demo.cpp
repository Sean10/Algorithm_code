#include "rtc_demo.hpp"
#include <iostream>
#include <chrono>
#include <thread>
#include <functional>

// 模拟一个计算密集型任务
class ComputeTask {
public:
    void operator()() {
        // 模拟计算
        volatile int sum = 0;
        for(int i = 0; i < 1000000; i++) {
            sum += i;
        }
    }
};

int main() {
    // 创建RTC任务队列
    RTCQueue<std::function<void()>> queue;
    
    // 提交多个任务
    for(int i = 0; i < 10; i++) {
        queue.submit(ComputeTask());
    }
    
    // 记录开始时间
    auto start = std::chrono::high_resolution_clock::now();
    
    // 执行所有任务
    queue.process();
    
    // 记录结束时间
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "处理完成，耗时: " << duration.count() << " 微秒" << std::endl;
    
    return 0;
} 