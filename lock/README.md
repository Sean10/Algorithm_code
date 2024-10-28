# 编译互斥锁示例
clang++ demo_mutex.cc -std=c++11 -stdlib=libc++

# 编译锁性能对比示例
clang++ lock_benchmark.cc -std=c++11 -stdlib=libc++ -o lock_benchmark

# 对比测试：
线程数：4
每个线程循环次数：100000
测量指标：
计数器最终值（验证正确性）
每次加锁操作的平均延迟（微秒）
运行程序后，你可以看到两种锁的性能对比。一般来说：
自旋锁在临界区很小且竞争不激烈时性能更好
互斥锁在临界区较大或竞争激烈时更适合，因为它会让出 CPU
你可以通过调整 NUM_THREADS 和 ITERATIONS 来测试不同场景下的性能表现。