cmake_minimum_required(VERSION 3.10)

# 基准测试可执行文件
add_executable(queue_benchmark queue_benchmark.cpp)

# 更新包含路径引用新的tools目录
target_include_directories(queue_benchmark PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

# 链接库
target_link_libraries(queue_benchmark 
    ${Boost_LIBRARIES}
    Threads::Threads
)

# 优化选项
target_compile_options(queue_benchmark PRIVATE -O3)

# 安装
install(TARGETS queue_benchmark DESTINATION bin)
