// File: pybind.cc


#include <pybind11/pybind11.h>

#include <pybind11/stl_bind.h>
namespace py = pybind11;

#include "camera.hh"
#include "patchmatch.hh"
#include "viewer.hh"


PYBIND11_MAKE_OPAQUE(std::vector<int>);

PYBIND11_PLUGIN(libcpm) {
  py::module m("libcpm", "CPM3D library in C++");

  // this assumes 8UC3
  py::class_<cv::Mat>(m, "Mat")
    .def_buffer([](cv::Mat &m) -> py::buffer_info {
      return py::buffer_info(m.data, // uchar*
                             sizeof(uchar),
                             py::format_descriptor<uchar>::format(), 3,
                             {(unsigned long)m.rows, (unsigned long)m.cols,
                              (unsigned long)m.channels()},
                             {sizeof(uchar) * m.cols * m.channels(),
                              sizeof(uchar) * m.channels(), sizeof(uchar)});
      })
    .def("__init__", [](cv::Mat& m, py::buffer b) { // only supports 32F
          py::buffer_info info = b.request();
          m_assert(info.ndim == 3);
          m_assert(info.shape[2] == 14);

          new (&m) cv::Mat(640, 640, CV_32FC(14), info.ptr);

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

  py::bind_vector<std::vector<int>>(m, "VectorInt");

  py::class_<PatchMatch>(m, "PatchMatch")
    .def(py::init<>())
    .def("init",
        (void (PatchMatch::*)(const Camera&, int)) &PatchMatch::init,
        "init from cam")
    .def("segment", &PatchMatch::segment)
    .def("match_all", &PatchMatch::match_all)
    .def("match_with_hm", &PatchMatch::match_with_hm);


  return m.ptr();
}
