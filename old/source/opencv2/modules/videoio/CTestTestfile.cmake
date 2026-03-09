# CMake generated Testfile for 
# Source directory: C:/OpenCV/modules/videoio
# Build directory: C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/videoio
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_videoio "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_test_videoio.exe" "--gtest_output=xml:opencv_test_videoio.xml")
set_tests_properties(opencv_test_videoio PROPERTIES  LABELS "Main;opencv_videoio;Accuracy" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/OpenCV/modules/videoio/CMakeLists.txt;281;ocv_add_accuracy_tests;C:/OpenCV/modules/videoio/CMakeLists.txt;0;")
add_test(opencv_perf_videoio "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_videoio.exe" "--gtest_output=xml:opencv_perf_videoio.xml")
set_tests_properties(opencv_perf_videoio PROPERTIES  LABELS "Main;opencv_videoio;Performance" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/performance" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/OpenCV/modules/videoio/CMakeLists.txt;282;ocv_add_perf_tests;C:/OpenCV/modules/videoio/CMakeLists.txt;0;")
add_test(opencv_sanity_videoio "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_videoio.exe" "--gtest_output=xml:opencv_perf_videoio.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
set_tests_properties(opencv_sanity_videoio PROPERTIES  LABELS "Main;opencv_videoio;Sanity" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/sanity" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/OpenCV/modules/videoio/CMakeLists.txt;282;ocv_add_perf_tests;C:/OpenCV/modules/videoio/CMakeLists.txt;0;")
