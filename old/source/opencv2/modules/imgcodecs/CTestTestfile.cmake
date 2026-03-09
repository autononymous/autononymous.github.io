# CMake generated Testfile for 
# Source directory: C:/OpenCV/modules/imgcodecs
# Build directory: C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/imgcodecs
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_imgcodecs "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_test_imgcodecs.exe" "--gtest_output=xml:opencv_test_imgcodecs.xml")
set_tests_properties(opencv_test_imgcodecs PROPERTIES  LABELS "Main;opencv_imgcodecs;Accuracy" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;196;ocv_add_accuracy_tests;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;0;")
add_test(opencv_perf_imgcodecs "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_imgcodecs.exe" "--gtest_output=xml:opencv_perf_imgcodecs.xml")
set_tests_properties(opencv_perf_imgcodecs PROPERTIES  LABELS "Main;opencv_imgcodecs;Performance" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/performance" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;207;ocv_add_perf_tests;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;0;")
add_test(opencv_sanity_imgcodecs "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_imgcodecs.exe" "--gtest_output=xml:opencv_perf_imgcodecs.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
set_tests_properties(opencv_sanity_imgcodecs PROPERTIES  LABELS "Main;opencv_imgcodecs;Sanity" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/sanity" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;207;ocv_add_perf_tests;C:/OpenCV/modules/imgcodecs/CMakeLists.txt;0;")
