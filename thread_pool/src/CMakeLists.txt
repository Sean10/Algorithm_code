add_library(thread_pool INTERFACE)
target_include_directories(thread_pool INTERFACE 
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
 
if(UNIX)
    target_link_libraries(thread_pool INTERFACE pthread)
endif() 