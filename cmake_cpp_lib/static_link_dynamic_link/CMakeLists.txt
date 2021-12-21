cmake_minimum_required (VERSION 3.10)

project (cmake_cpp_lib)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 11)
set (LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)
set (EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
add_subdirectory (demolib)
add_subdirectory (demolib2)
add_subdirectory (test)



