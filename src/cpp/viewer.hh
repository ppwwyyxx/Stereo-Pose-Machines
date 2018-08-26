//File: viewer.hh


#pragma once
#include <atomic>
#include <thread>
#include "lib/timer.hh"
#include "camera.hh"

class StereoCameraViewer {
  public:
    StereoCameraViewer(const Camera& cam);
    ~StereoCameraViewer() {
      stopped = true;
      if (m_worker_th.joinable())
        m_worker_th.join();
    }

    void start();

    void stop() { stopped = true; }

  protected:
    const Camera& m_cam;
    std::thread m_worker_th;
    std::atomic_bool stopped{false};
    Timer m_timer;

    void worker();
};
