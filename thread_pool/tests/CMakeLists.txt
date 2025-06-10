find_package(GTest REQUIRED)

add_executable(thread_pool_test thread_pool_test.cpp)
target_include_directories(thread_pool_test PRIVATE 
    ${CMAKE_SOURCE_DIR}/include
    ${GTEST_INCLUDE_DIRS}
)

target_link_libraries(thread_pool_test PRIVATE
    GTest::GTest
    GTest::Main
)

if(UNIX)
    target_link_libraries(thread_pool_test PRIVATE pthread)
endif()

add_test(NAME thread_pool_test COMMAND thread_pool_test) 