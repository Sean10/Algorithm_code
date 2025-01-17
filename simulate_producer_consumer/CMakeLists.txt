cmake_minimum_required(VERSION 3.10)
project(queue_benchmark)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 Boost 库
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

# 添加可执行文件
add_executable(queue_benchmark queue_benchmark.cpp)

# 链接 Boost 库和 pthread
target_link_libraries(queue_benchmark 
    ${Boost_LIBRARIES}
    pthread
) 