# Benchmark CMakeLists.txt

# 设置头文件目录
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 定义benchmark框架的源文件
set(BENCHMARK_LIB_SOURCES
    src/benchmark_executor.cpp
    src/task_generators.cpp
    src/thread_pool_adapters.cpp
    src/factories_and_reporter.cpp
    # src/memory_profiler.cpp # 暂时禁用，直到实现
)

# 创建一个静态库来包含所有benchmark框架的核心逻辑
add_library(thread_pool_benchmark_lib STATIC ${BENCHMARK_LIB_SOURCES})

# 链接Google Benchmark和线程库
target_link_libraries(thread_pool_benchmark_lib PUBLIC
    Threads::Threads
    benchmark::benchmark
)

# 链接我们的线程池库
target_link_libraries(thread_pool_benchmark_lib PUBLIC thread_pool)

# --- 定义各个benchmark可执行文件 ---

# 1. CPU密集型测试
add_executable(benchmark_cpu_intensive
    src/benchmark_cpu_intensive.cpp
)
target_link_libraries(benchmark_cpu_intensive
    thread_pool_benchmark_lib
    benchmark::benchmark_main # 使用gbenchmark的主函数
)

# 2. IO密集型测试
add_executable(benchmark_io_intensive
    src/benchmark_io_intensive.cpp
)
target_link_libraries(benchmark_io_intensive
    thread_pool_benchmark_lib
    benchmark::benchmark_main
)

# 3. 线程池实现对比测试
add_executable(benchmark_threadpool_comparison
    src/benchmark_threadpool_comparison.cpp
)
target_link_libraries(benchmark_threadpool_comparison
    thread_pool_benchmark_lib
    benchmark::benchmark_main
)

# 5. 优化前后对比测试 (新添加)
add_executable(benchmark_optimization_comparison
    src/benchmark_optimization_comparison.cpp
)
target_link_libraries(benchmark_optimization_comparison
    thread_pool_benchmark_lib
    benchmark::benchmark_main
)

# 6. 内存分配性能对比测试
add_executable(benchmark_memory_allocation
    src/benchmark_memory_allocation.cpp
)
target_link_libraries(benchmark_memory_allocation
    thread_pool_benchmark_lib
    benchmark::benchmark_main
)

# --- 内存分配器特定的benchmark (可选) ---
option(THREAD_POOL_USE_TCMALLOC "Build with tcmalloc for benchmarks" OFF)

if(THREAD_POOL_USE_TCMALLOC AND TCMALLOC_LIBRARIES)
    message(STATUS "Benchmark: tcmalloc benchmark enabled.")
    add_executable(benchmark_memory_allocation_tcmalloc
        src/benchmark_memory_allocation.cpp
    )
    target_compile_definitions(benchmark_memory_allocation_tcmalloc PRIVATE USE_TCMALLOC)
    target_link_libraries(benchmark_memory_allocation_tcmalloc
        thread_pool_benchmark_lib
        ${TCMALLOC_LIBRARIES}
        benchmark::benchmark_main
    )
else()
    message(STATUS "Benchmark: tcmalloc benchmark not built because THREAD_POOL_USE_TCMALLOC is OFF or tcmalloc library not found.")
endif()

# 4. 主测试套件（如果需要一个单独的、非gbenchmark的入口）
# add_executable(thread_pool_benchmark
#     src/main_benchmark.cpp
# )
# target_link_libraries(thread_pool_benchmark
#     thread_pool_benchmark_lib
# )

# --- 安装脚本 ---
install(DIRECTORY scripts/ DESTINATION bin) 