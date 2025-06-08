cmake_minimum_required(VERSION 3.8)
project(tcb_span LANGUAGES CXX)

find_package(ament_cmake REQUIRED)

add_library(tcb_span INTERFACE)
target_sources(tcb_span INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include/tcb/span.hpp)
target_include_directories(tcb_span INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(tcb_span INTERFACE cxx_std_11)

ament_target_dependencies(tcb_span)

ament_export_targets(tcb_span)
ament_export_include_directories(include)

ament_package()