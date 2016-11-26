//File: camera.hh
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#pragma once
#include <thread>
#include <atomic>
#include <opencv2/core/core.hpp>

class Camera {
	public:
		Camera() { }

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

		cv::Mat m_cameras[kMaxCameras];
	protected:
		std::thread m_worker_th;
		std::atomic_bool m_stopped{false};

};

