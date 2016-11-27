//File: main.cpp
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include "camera.hh"
#include <opencv2/highgui/highgui.hpp>
#include <chrono>
using namespace cv;
using namespace std;
using namespace std::this_thread;
#include "lib/timer.hh"

int main() {
	Camera c;
	c.setup();

	for (int i = 0; i < 100; ++i) {
		// imwrite takes 20ms
		auto im = c.get(0);
		// cv::imshow("test", im);
		cv::imwrite("test" + to_string(i) + ".jpg", im);
		sleep_for(std::chrono::milliseconds(1000));
	}

	c.shutdown();
}
