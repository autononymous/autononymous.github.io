#include <iostream>
#include <opencv.hpp> // Add this line

int main() {
    std::cout << "Hello, World!" << std::endl;

    // Example: Create and show an empty image
    cv::Mat img = cv::Mat::zeros(300, 300, CV_8UC3);
    cv::imshow("Empty Image", img);
    cv::waitKey(0);

    return 0;
}



