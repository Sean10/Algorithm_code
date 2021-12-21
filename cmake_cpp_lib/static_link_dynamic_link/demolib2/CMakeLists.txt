cmake_minimum_required (VERSION 3.10)

aux_source_directory (. DEMOLIB_SRC_LIST2)

add_library(demolib2 SHARED ${DEMOLIB_SRC_LIST2})
# target_link_libraries(demolib2 demolib)

