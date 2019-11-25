cmake_minimum_required(VERSION 2.8)
project(waveOverUDP)

message("Build type: ${CMAKE_BUILD_TYPE}")

get_filename_component(BUILD_DIR_NAME ${CMAKE_BINARY_DIR} NAME)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../${BUILD_DIR_NAME}-bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../${BUILD_DIR_NAME}-bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../${BUILD_DIR_NAME}-bin")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fvisibility=hidden")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions -fno-rtti")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-exceptions -Wall -fvisibility=hidden")

set(TARGET_OS "unix")
set(TARGET_LIBS asound wiringPi)

add_executable(wavePlayUDP
  "${CMAKE_CURRENT_LIST_DIR}/wavePlayUDP.cpp")
target_link_libraries(wavePlayUDP ${TARGET_LIBS})

add_executable(waveSendUDP
  "${CMAKE_CURRENT_LIST_DIR}/waveSendUDP.cpp")
target_link_libraries(waveSendUDP ${TARGET_LIBS})