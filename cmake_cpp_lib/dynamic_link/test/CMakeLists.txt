cmake_minimum_required (VERSION 3.10)

aux_source_directory (. TEST_SRC_LIST)

add_executable(test ${TEST_SRC_LIST})
target_link_libraries(test demolib)

