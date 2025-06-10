cmake_minimum_required(VERSION 3.10)
project(aio_benchmark_tools)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O3 -g")

# 包含头文件目录
include_directories(../include)

# nanobench环境检测工具
add_executable(test_nanobench test_nanobench.cpp)

# 安装
install(TARGETS test_nanobench DESTINATION bin)

# 帮助
add_custom_target(help_tools
    COMMAND ${CMAKE_COMMAND} -E echo "可用工具:"
    COMMAND ${CMAKE_COMMAND} -E echo "  test_nanobench - 检测nanobench性能计数器支持"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "编译:"
    COMMAND ${CMAKE_COMMAND} -E echo "  mkdir -p build && cd build"
    COMMAND ${CMAKE_COMMAND} -E echo "  cmake .. && make"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "运行:"
    COMMAND ${CMAKE_COMMAND} -E echo "  ./test_nanobench"
) 