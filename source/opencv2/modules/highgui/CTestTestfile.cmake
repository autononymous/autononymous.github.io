# CMake generated Testfile for 
# Source directory: C:/OpenCV/modules/highgui
# Build directory: C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/modules/highgui
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_highgui "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/bin/opencv_test_highgui.exe" "--gtest_output=xml:opencv_test_highgui.xml")
set_tests_properties(opencv_test_highgui PROPERTIES  LABELS "Main;opencv_highgui;Accuracy" WORKING_DIRECTORY "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/source/opencv2/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/OpenCV/cmake/OpenCVUtils.cmake;1799;add_test;C:/OpenCV/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/OpenCV/modules/highgui/CMakeLists.txt;311;ocv_add_accuracy_tests;C:/OpenCV/modules/highgui/CMakeLists.txt;0;")
