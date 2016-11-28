//File: camera.hh
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#pragma once
#include <thread>
#include <atomic>
#include <vector>
#include <opencv2/core/core.hpp>
#include "lib/debugutils.hh"

struct FrameBuffer {
	FrameBuffer();

	std::vector<cv::Mat> frames;
  std::atomic_int write_pos{-1};	// the position last written (always contains valid data)
  mutable int last_read_pos{-1};

	void write(cv::Mat mat);	// copy mat in to my buffer
	cv::Mat read() const;	// read latest frame
	cv::Mat read_new() const;	// read latest frame not read yet

	bool empty() const { return write_pos < 0; }
	static const int kFrameBufferSize;
};

class Camera {
	public:
		Camera() { }
		~Camera() { shutdown(); }

		void setup();
		void shutdown();

		bool is_stopped() const { return m_stopped; }

		// Limits the amount of cameras used for grabbing.
		// It is important to manage the available bandwidth when grabbing with multiple cameras.
		// This applies, for instance, if two GigE cameras are connected to the same network adapter via a switch.
		// To manage the bandwidth, the GevSCPD interpacket delay parameter and the GevSCFTD transmission delay
		// parameter can be set for each GigE camera device.
		// The "Controlling Packet Transmission Timing with the Interpacket and Frame Transmission Delays on Basler GigE Vision Cameras"
		// Application Notes (AW000649xx000)
		// provide more information about this topic.
		// The bandwidth used by a FireWire camera device can be limited by adjusting the packet size.
		static const size_t kMaxCameras = 2;

		cv::Mat get(int i) const {
      m_assert(i < num_cameras);
      return m_camera_buffer[i].read();
    }
		cv::Mat get_new(int i) const {
      m_assert(i < num_cameras);
      return m_camera_buffer[i].read_new();
    }

    int num_cameras = 0;
		FrameBuffer m_camera_buffer[kMaxCameras];
	protected:
		std::thread m_worker_th;
		std::atomic_bool m_stopped{false};
};

