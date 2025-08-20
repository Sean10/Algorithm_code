cmake_minimum_required(VERSION 3.10)

# 集成测试源文件
set(INTEGRATION_TEST_SOURCES
    test_producer_consumer.cpp
)

# 创建集成测试可执行文件
add_executable(integration_tests ${INTEGRATION_TEST_SOURCES})

# 链接库
target_link_libraries(integration_tests 
    gtest
    gtest_main
    Threads::Threads
    ${Boost_LIBRARIES}
)

# 包含目录
target_include_directories(integration_tests PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/../../src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../benchmarks
)

# 添加测试到CTest
include(GoogleTest)
gtest_discover_tests(integration_tests)
