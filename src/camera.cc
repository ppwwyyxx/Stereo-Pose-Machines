//File: camera.cc

#include "camera.hh"

#include <chrono>
#include <thread>

#include <opencv2/imgproc/imgproc.hpp>
#include "lib/timer.hh"

using namespace std;


void Camera::shutdown() {
	m_stopped = true;
	if (m_worker_th.joinable())
		m_worker_th.join();
}

cv::Mat Camera::get_for_py(int i) const {
  m_assert(i < num_cameras);
  auto m = m_camera_buffer[i].read_new();
  // original size: 1600x1200
  auto r = cv::Rect(1600*0.25,1200*0.25,800,600);
  m = m(r);
  cv::resize(m, m, cv::Size(368,368));
  cv::flip(m, m, 1);
  return m;
}

FrameBuffer::FrameBuffer() : frames(kFrameBufferSize) { }

void FrameBuffer::write(cv::Mat mat) {
	int new_pos = (write_pos + 1) % kFrameBufferSize;
	frames[new_pos] = mat.clone();
	write_pos = new_pos;
}

cv::Mat FrameBuffer::read() const {
  last_read_pos = write_pos;
	return frames[write_pos];
}

cv::Mat FrameBuffer::read_new() const {
  while (last_read_pos == write_pos) {};
  return read();
}
