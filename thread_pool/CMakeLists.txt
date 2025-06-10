cmake_minimum_required(VERSION 3.14)
project(thread_pool VERSION 1.0.0 LANGUAGES CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 编译选项
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Werror -pedantic)
endif()

#include_directories(SYSTEM /usr/include/c++/12)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libstdc++")

# 选项
option(THREAD_POOL_BUILD_TESTS "Build the thread pool tests" ON)
option(THREAD_POOL_BUILD_EXAMPLES "Build the thread pool examples" ON)
option(THREAD_POOL_BUILD_BENCHMARK "Build the thread pool benchmark" ON)
option(THREAD_POOL_USE_TCMALLOC "Use tcmalloc for benchmarks" OFF)
option(THREAD_POOL_USE_JEMALLOC "Use jemalloc for benchmarks" OFF)

# 查找依赖
find_package(Threads REQUIRED)

# benchmark依赖
if(THREAD_POOL_BUILD_BENCHMARK)
    # 查找Google Benchmark
    find_package(benchmark QUIET)
    if(NOT benchmark_FOUND)
        include(FetchContent)
        FetchContent_Declare(
            benchmark
            GIT_REPOSITORY https://github.com/google/benchmark.git
            GIT_TAG v1.9.0
        )
        FetchContent_MakeAvailable(benchmark)
    endif()
    
    # 内存分配器选项
    if(THREAD_POOL_USE_TCMALLOC)
        find_library(TCMALLOC_LIBRARY NAMES tcmalloc)
        if(NOT TCMALLOC_LIBRARY)
            message(FATAL_ERROR "tcmalloc library not found. Please install google-perftools.")
        else()
            message(STATUS "Found tcmalloc library: ${TCMALLOC_LIBRARY}")
            # 将tcmalloc库的路径传递给benchmark子目录
            set(TCMALLOC_LIBRARIES ${TCMALLOC_LIBRARY} CACHE INTERNAL "TCMalloc library for linking")
        endif()
    endif()
    
    if(THREAD_POOL_USE_JEMALLOC)
        find_package(PkgConfig REQUIRED)
        pkg_check_modules(JEMALLOC REQUIRED jemalloc)
    endif()
endif()

# 添加子目录
add_subdirectory(src)

if(THREAD_POOL_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

if(THREAD_POOL_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

if(THREAD_POOL_BUILD_BENCHMARK)
    add_subdirectory(benchmark)
endif()
