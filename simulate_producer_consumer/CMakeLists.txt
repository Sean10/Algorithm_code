cmake_minimum_required(VERSION 3.10)
project(ProducerConsumerQueues VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 项目选项
option(BUILD_BENCHMARKS "Build benchmark programs" ON)
option(BUILD_TESTS "Build unit and integration tests" ON)
option(BUILD_EXAMPLES "Build example programs" ON)
option(ENABLE_COVERAGE "Enable code coverage" OFF)

# 查找依赖
find_package(Boost REQUIRED)
find_package(Threads REQUIRED)

# 包含目录
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${Boost_INCLUDE_DIRS})

# 编译选项
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DDEBUG")

if(ENABLE_COVERAGE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --coverage")
endif()

# 子模块
if(BUILD_BENCHMARKS)
    add_subdirectory(benchmarks)
endif()

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# 安装配置
install(DIRECTORY src/ 
        DESTINATION include/producer_consumer_queues
        FILES_MATCHING PATTERN "*.hpp")
