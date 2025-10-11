# Install script for directory: C:/OpenCV/modules/ml

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files/opencv_ml")
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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/lib" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/lib/opencv_ml4120.lib")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/bin" TYPE SHARED_LIBRARY OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_ml4120.dll")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "pdb")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/bin" TYPE FILE OPTIONAL FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_ml4120.pdb")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/ml/include/opencv2/ml.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2/ml" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/ml/include/opencv2/ml/ml.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2/ml" TYPE FILE OPTIONAL FILES "C:/OpenCV/modules/ml/include/opencv2/ml/ml.inl.hpp")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/ml/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
