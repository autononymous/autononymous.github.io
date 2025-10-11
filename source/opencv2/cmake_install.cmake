# Install script for directory: C:/OpenCV

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files/OpenCV")
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

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippicv-readme.htm" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/icv/readme.htm")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippicv-EULA.rtf" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/EULA.rtf")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippicv-third-party-programs.txt" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/third-party-programs.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippiw-support.txt" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/icv/../iw/../support.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippiw-third-party-programs.txt" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/icv/../iw/../third-party-programs.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ippiw-EULA.rtf" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippicv/ippicv_win/icv/../iw/../EULA.rtf")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "flatbuffers-LICENSE.txt" FILES "C:/OpenCV/3rdparty/flatbuffers/LICENSE.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "opencl-headers-LICENSE.txt" FILES "C:/OpenCV/3rdparty/include/opencl/LICENSE.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ade-LICENSE" FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ade/ade-0.1.2e/LICENSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ffmpeg-license.txt" FILES "C:/OpenCV/3rdparty/ffmpeg/license.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "licenses" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/etc/licenses" TYPE FILE RENAME "ffmpeg-readme.txt" FILES "C:/OpenCV/3rdparty/ffmpeg/readme.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2" TYPE FILE FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/cvconfig.h")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv2" TYPE FILE FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/opencv2/opencv_modules.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/x64/vc17/lib/OpenCVModules.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/x64/vc17/lib/OpenCVModules.cmake"
         "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/CMakeFiles/Export/d30778e0ac7619fb773456bd811156bf/OpenCVModules.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/x64/vc17/lib/OpenCVModules-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/x64/vc17/lib/OpenCVModules.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/lib" TYPE FILE FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/CMakeFiles/Export/d30778e0ac7619fb773456bd811156bf/OpenCVModules.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/lib" TYPE FILE FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/CMakeFiles/Export/d30778e0ac7619fb773456bd811156bf/OpenCVModules-noconfig.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/x64/vc17/lib" TYPE FILE FILES
    "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/win-install/OpenCVConfig-version.cmake"
    "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/win-install/x64/vc17/lib/OpenCVConfig.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE FILES
    "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/win-install/OpenCVConfig-version.cmake"
    "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/win-install/OpenCVConfig.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "libs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "C:/OpenCV/LICENSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "scripts" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE FILES "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/CMakeFiles/install/setup_vars_opencv4.cmd")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/zlib/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/libjpeg-turbo/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/libtiff/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/libwebp/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/openjpeg/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/libpng/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/openexr/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ippiw/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/protobuf/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/hal/ipp/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/3rdparty/ittnotify/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/include/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/calib3d/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/core/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/dnn/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/features2d/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/flann/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/gapi/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/highgui/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/imgcodecs/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/imgproc/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/java/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/js/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/ml/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/objc/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/objdetect/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/photo/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/python/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/stitching/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/ts/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/video/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/videoio/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/.firstpass/world/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/core/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/flann/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/imgproc/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/ml/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/photo/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/python_tests/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/dnn/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/features2d/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/imgcodecs/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/videoio/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/calib3d/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/highgui/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/objdetect/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/stitching/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/ts/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/video/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/gapi/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/java_bindings_generator/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/js_bindings_generator/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/objc_bindings_generator/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/python_bindings_generator/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/python3/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/doc/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/data/cmake_install.cmake")
  include("C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/apps/cmake_install.cmake")

endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
