cmake_minimum_required(VERSION 3.10)
project(PACT)

set(CMAKE_CXX_STANDARD 17)

# Set OpenCV_DIR to your OpenCV build folder
set(OpenCV_DIR "C:/OpenCV/build")

find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(PACT main.cpp)
target_link_libraries(PACT ${OpenCV_LIBS})