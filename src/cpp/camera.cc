//File: camera.cc

#include "camera.hh"
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include "lib/timer.hh"
#include "config.hh"

using namespace std;
using namespace cv;

const size_t Camera::kMaxCameras;
const int FrameBuffer::kFrameBufferSize = 50;

void Camera::shutdown() {
	m_stopped = true;
	if (m_worker_th.joinable())
		m_worker_th.join();
}

cv::Mat Camera::get_for_py(int i) const {
  m_assert(i < num_cameras);
  auto m = m_camera_buffer[i].read_new();
  // original size: 1600x1200
  static auto r = cv::Rect(ORIG_W*CROP_X0,ORIG_H*CROP_Y0,ORIG_W*CROP_W,ORIG_H*CROP_H);
  m = m(r);
  m = und[i].undistort(m);
  //cv::resize(m, m, cv::Size(368,368));
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
