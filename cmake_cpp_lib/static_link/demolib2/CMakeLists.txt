cmake_minimum_required (VERSION 3.10)

aux_source_directory (. DEMOLIB_SRC_LIST)

add_library(demolib2 SHARED ${DEMOLIB_SRC_LIST})


