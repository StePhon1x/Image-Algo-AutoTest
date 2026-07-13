cmake_minimum_required(VERSION 3.10)
project(ImageAlgoTest)
set(CMAKE_CXX_STANDARD 11)

# OpenCV依赖预留，需要时取消注释
# find_package(OpenCV REQUIRED)
# include_directories(${OpenCV_INCLUDE_DIRS})

# 可执行文件统一输出到 build/bin
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 由processor.cpp生成 processor.exe
add_executable(processor processor.cpp)

# 启用OpenCV时取消注释，目标名与上方一致
# target_link_libraries(processor ${OpenCV_LIBS})