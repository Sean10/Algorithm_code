cmake_minimum_required(VERSION 3.10)

# 单元测试源文件
set(UNIT_TEST_SOURCES
    test_mutex_queue.cpp
    test_spsc_queue.cpp
    test_benchmark_tools.cpp
)

# 创建单元测试可执行文件
add_executable(unit_tests ${UNIT_TEST_SOURCES})

# 链接库
target_link_libraries(unit_tests 
    gtest
    gtest_main
    Threads::Threads
    ${Boost_LIBRARIES}
)

# 包含目录
target_include_directories(unit_tests PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/../../src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../benchmarks
)

# 添加测试到CTest
include(GoogleTest)
gtest_discover_tests(unit_tests)
