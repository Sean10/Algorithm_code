cmake_minimum_required(VERSION 3.10)
project(aio_benchmark)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g")

# 构建类型和优化选项
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)
endif()

# 根据构建类型设置优化选项
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0")
endif()

# Sanitizer 选项
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(ENABLE_MSAN "Enable MemorySanitizer" OFF)

# AddressSanitizer (检测内存错误、缓冲区溢出、使用后释放等)
if(ENABLE_ASAN)
    message(STATUS "Enabling AddressSanitizer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")
endif()

# ThreadSanitizer (检测数据竞争)
if(ENABLE_TSAN)
    message(STATUS "Enabling ThreadSanitizer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=thread")
endif()

# UndefinedBehaviorSanitizer (检测未定义行为)
if(ENABLE_UBSAN)
    message(STATUS "Enabling UndefinedBehaviorSanitizer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=undefined")
endif()

# MemorySanitizer (检测未初始化内存读取)
if(ENABLE_MSAN)
    message(STATUS "Enabling MemorySanitizer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=memory -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=memory")
endif()

# 检查sanitizer冲突
if(ENABLE_ASAN AND ENABLE_TSAN)
    message(FATAL_ERROR "AddressSanitizer and ThreadSanitizer cannot be used together")
endif()

if(ENABLE_ASAN AND ENABLE_MSAN)
    message(FATAL_ERROR "AddressSanitizer and MemorySanitizer cannot be used together")
endif()

if(ENABLE_TSAN AND ENABLE_MSAN)
    message(FATAL_ERROR "ThreadSanitizer and MemorySanitizer cannot be used together")
endif()

# 查找所需库
find_library(AIO_LIB aio)
if(NOT AIO_LIB)
    message(FATAL_ERROR "libaio not found. Please install libaio-dev")
endif()

find_library(URING_LIB uring)
if(NOT URING_LIB)
    message(FATAL_ERROR "liburing not found. Please install liburing-dev")
endif()

find_package(Threads REQUIRED)

# 包含头文件目录
include_directories(src include)

# 源文件
set(SOURCES
    src/main.cpp
    src/aio_engine.cpp
    src/uring_engine.cpp
    src/benchmark.cpp
    src/config.cpp
    src/stats.cpp
    src/utils.cpp
    src/nanobench_impl.cpp
)

# 可执行文件
add_executable(aio_bench ${SOURCES})

# 链接库
target_link_libraries(aio_bench ${AIO_LIB} ${URING_LIB} Threads::Threads)

# 添加子目录
add_subdirectory(tools)

# 安装
install(TARGETS aio_bench DESTINATION bin) 