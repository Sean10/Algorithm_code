#include "config.h"
#include "benchmark.h"
#include "utils.h"
#include <nanobench.h>
#include <iostream>
#include <memory>
#include <csignal>

using namespace aio_bench;

// 全局基准测试对象
std::unique_ptr<Benchmark> g_benchmark;

// 信号处理函数
void signal_handler(int signal) {
    std::cout << "\n收到信号 " << signal << ", 正在停止测试..." << std::endl;
    if (g_benchmark) {
        g_benchmark->stop();
    }
}

int main(int argc, char* argv[]) {
    std::cout << "AIO 基准测试工具 v1.0\n" << std::endl;
    
    // 解析配置
    Config config;
    if (!config.parse_args(argc, argv)) {
        return 1;
    }
    
    // 设置信号处理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    try {
        // 创建基准测试对象
        g_benchmark = std::make_unique<Benchmark>(config);
        
        // 初始化
        if (!g_benchmark->initialize()) {
            std::cerr << "错误: 初始化失败" << std::endl;
            return 1;
        }
        
        // 运行测试
        std::cout << "开始基准测试..." << std::endl;
        
        if (config.enable_perf_benchmark) {
            std::cout << "启用性能分析模式..." << std::endl;
            // 使用nanobench包装整个AIO测试，启用性能计数器
            ankerl::nanobench::Bench()
                .title("AIO基准测试性能分析")
                .unit("op")  // 改为op单位以获得更详细的指标
                .epochs(1)   // 只运行一次
                .performanceCounters(true)  // 启用性能计数器
                .run("AIO测试完整执行", [&] {
                    g_benchmark->run();
                    ankerl::nanobench::doNotOptimizeAway(g_benchmark.get());
                });
        } else {
            g_benchmark->run();
        }
        
        std::cout << "测试完成" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "异常: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "未知异常" << std::endl;
        return 1;
    }
    
    return 0;
} 