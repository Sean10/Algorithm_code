add_executable(basic_usage basic_usage.cpp)
target_include_directories(basic_usage PRIVATE ${CMAKE_SOURCE_DIR}/include)
 
if(UNIX)
    target_link_libraries(basic_usage PRIVATE pthread)
endif() 