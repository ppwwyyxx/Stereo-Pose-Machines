//File: main.cpp
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include "camera.hh"
#include <opencv2/highgui/highgui.hpp>
#include <chrono>
using namespace cv;
using namespace std;
using namespace std::this_thread;

int main() {
	Camera c;
	c.setup();

	sleep_for(std::chrono::milliseconds(500));

	for (int i = 0; i < 20; ++i) {
		cv::imwrite("test" + to_string(i) + ".jpg", c.m_cameras[0]);
		sleep_for(std::chrono::milliseconds(200));
	}

	c.shutdown();
}
