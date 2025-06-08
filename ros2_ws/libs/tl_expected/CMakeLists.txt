cmake_minimum_required(VERSION 3.8)
project(tl_expected LANGUAGES CXX)

find_package(ament_cmake REQUIRED)

add_library(${PROJECT_NAME} INTERFACE)
target_include_directories(${PROJECT_NAME} INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)
target_compile_features(${PROJECT_NAME} INTERFACE cxx_std_14)

ament_export_include_directories(include)

ament_package()