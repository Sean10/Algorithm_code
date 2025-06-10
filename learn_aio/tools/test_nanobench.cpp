#define ANKERL_NANOBENCH_IMPLEMENT
#include <nanobench.h>
#include <iostream>

int main() {
    double d = 1.0;
    
    std::cout << "测试nanobench性能计数器..." << std::endl;
    
    ankerl::nanobench::Bench()
        .title("简单测试")
        .performanceCounters(true)
        .run("double operations", [&] {
            d += 1.0 / d;
            if (d > 5.0) {
                d -= 5.0;
            }
            ankerl::nanobench::doNotOptimizeAway(d);
        });
    
    return 0;
} 