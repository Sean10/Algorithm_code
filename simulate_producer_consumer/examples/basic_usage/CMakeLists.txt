cmake_minimum_required(VERSION 3.10)

# 基础示例程序
add_executable(simple_producer_consumer simple_producer_consumer.cpp)

target_include_directories(simple_producer_consumer PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/../../src
)

target_link_libraries(simple_producer_consumer 
    Threads::Threads
)

# 安装
install(TARGETS simple_producer_consumer DESTINATION bin)
