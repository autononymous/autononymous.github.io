# CMake generated Testfile for 
# Source directory: C:/OpenCV/modules/dnn
# Build directory: C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/dnn
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_dnn "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_test_dnn.exe" "--gtest_output=xml:opencv_test_dnn.xml")
set_tests_properties(opencv_test_dnn PROPERTIES  LABELS "Main;opencv_dnn;Accuracy" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/OpenCV/modules/dnn/CMakeLists.txt;261;ocv_add_accuracy_tests;C:/OpenCV/modules/dnn/CMakeLists.txt;0;")
add_test(opencv_perf_dnn "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_dnn.exe" "--gtest_output=xml:opencv_perf_dnn.xml")
set_tests_properties(opencv_perf_dnn PROPERTIES  LABELS "Main;opencv_dnn;Performance" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/performance" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/OpenCV/modules/dnn/CMakeLists.txt;272;ocv_add_perf_tests;C:/OpenCV/modules/dnn/CMakeLists.txt;0;")
add_test(opencv_sanity_dnn "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_perf_dnn.exe" "--gtest_output=xml:opencv_perf_dnn.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
set_tests_properties(opencv_sanity_dnn PROPERTIES  LABELS "Main;opencv_dnn;Sanity" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/sanity" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/OpenCV/modules/dnn/CMakeLists.txt;272;ocv_add_perf_tests;C:/OpenCV/modules/dnn/CMakeLists.txt;0;")
