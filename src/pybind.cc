// File: pybind.cc
// Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include <pybind11/pybind11.h>
namespace py = pybind11;

#include "camera.hh"
#include "viewer.hh"

PYBIND11_PLUGIN(libcpm) {
  py::module m("libcpm", "CPM3D library in C++");

  // this assumes 8UC3
  py::class_<cv::Mat>(m, "Mat").def_buffer([](cv::Mat &m) -> py::buffer_info {
    return py::buffer_info(m.data, // uchar*
                           sizeof(uchar),
                           py::format_descriptor<uchar>::format(), 3,
                           {(unsigned long)m.rows, (unsigned long)m.cols,
                            (unsigned long)m.channels()},
                           {sizeof(uchar) * m.cols * m.channels(),
                            sizeof(uchar) * m.channels(), sizeof(uchar)});
  });

  py::class_<Camera>(m, "Camera")
      .def(py::init<>())
      .def("setup", &Camera::setup)
      .def("shutdown", &Camera::shutdown)
      .def("get", &Camera::get)
      .def("get_new", &Camera::get_new)
      .def("get_for_py", &Camera::get_for_py)
      .def_readwrite("num_cameras", &Camera::num_cameras);

  py::class_<StereoCameraViewer>(m, "StereoCameraViewer")
    .def(py::init<const Camera&>())
    .def("start", &StereoCameraViewer::start)
    .def("stop", &StereoCameraViewer::stop);
  return m.ptr();
}
