cmake_minimum_required(VERSION 3.10)
project(rtc_demo)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(rtc_demo rtc_demo.cpp)

add_executable(traditional_demo traditional_demo.cpp)

find_package(Threads REQUIRED)
target_link_libraries(rtc_demo Threads::Threads)
target_link_libraries(traditional_demo Threads::Threads) 
