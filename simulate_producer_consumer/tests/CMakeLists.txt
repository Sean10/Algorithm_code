cmake_minimum_required(VERSION 3.10)

# 查找Google Test
find_package(GTest QUIET)
if(NOT GTest_FOUND)
    # 如果没有安装GTest，使用FetchContent下载
    include(FetchContent)
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/release-1.12.1.zip
    )
    FetchContent_MakeAvailable(googletest)
endif()

# 包含目录
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../src)

# 单元测试
add_subdirectory(unit)

# 集成测试
add_subdirectory(integration)

# 创建测试运行脚本
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/scripts/run_all_tests.sh.in
    ${CMAKE_CURRENT_BINARY_DIR}/scripts/run_all_tests.sh
    @ONLY
)

# 添加自定义目标来运行所有测试
add_custom_target(run_tests
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/scripts/run_all_tests.sh
    DEPENDS unit_tests integration_tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running all tests"
)
