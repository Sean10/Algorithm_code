cmake_minimum_required(VERSION 3.14)
project(slog C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(slog
    slog.c
    slog.h)
