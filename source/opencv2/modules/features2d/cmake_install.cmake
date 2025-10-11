# Install script for directory: C:/OpenCV/modules/features2d

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files/opencv_features2d")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/lib" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/lib/opencv_features2d4120.lib")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/bin" TYPE SHARED_LIBRARY OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_features2d4120.dll")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "pdb")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/bin" TYPE FILE OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_features2d4120.pdb")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/features2d/include/opencv2/features2d.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2/features2d" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/features2d/include/opencv2/features2d/features2d.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2/features2d/hal" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/features2d/include/opencv2/features2d/hal/interface.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "mscr-chi_table_LICENSE.txt" FILES "C:/OpenCV/modules/features2d/3rdparty/mscr/chi_table_LICENSE.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/features2d/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
