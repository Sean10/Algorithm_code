cmake_minimum_required (VERSION 3.10)

aux_source_directory (. DEMOLIB_SRC_LIST)

add_library(demolib SHARED ${DEMOLIB_SRC_LIST})


target_link_libraries(demolib demolib2)