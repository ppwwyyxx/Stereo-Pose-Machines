//File: pylon_camera.cc


#include <iostream>
#include <chrono>
#include <sstream>
#include <pylon/PylonIncludes.h>
#include <pylon/usb/BaslerUsbInstantCameraArray.h>
#include "camera.hh"

using namespace Pylon;
using namespace Basler_UsbCameraParams;
using namespace std;

void worker(Camera& camera) {
	CTlFactory& tlFactory = CTlFactory::GetInstance();

	// Get all attached devices and exit application if no device is found.
	DeviceInfoList_t devices;
	if ( tlFactory.EnumerateDevices(devices) == 0 ) {
		throw RUNTIME_EXCEPTION( "No camera present.");
	}

  camera.num_cameras = min(devices.size(), Camera::kMaxCameras);
	CBaslerUsbInstantCameraArray cameras(camera.num_cameras);

  bool rev = false;

	// Create and attach all Pylon Devices.
  try {
    for ( size_t i = 0; i < cameras.GetSize(); ++i) {
      cameras[i].Attach(tlFactory.CreateDevice(devices[i]));
      cameras[i].Open();
      cameras[i].GainSelector.SetValue(GainSelector_All);
      if (IsWritable(cameras[i].GainAuto)){
        cameras[i].GainAuto.SetValue(GainAuto_Off);
      }
      cameras[i].ReverseY.SetValue(true);
      cameras[i].ReverseX.SetValue(true);
      cameras[i].Gain.SetValue(6.0);
      cameras[i].BslColorSpaceMode.SetValue(BslColorSpaceMode_RGB);
      cameras[i].LightSourcePreset.SetValue(LightSourcePreset_Off);
      cameras[i].ExposureAuto.SetValue(ExposureAuto_Off);
      cameras[i].ExposureTime.SetValue(25000.0);
      cameras[i].OverlapMode.SetValue(OverlapMode_Off);

      // Print the model name of the camera.
      cout << "Using device " << i << ": " << cameras[i].GetDeviceInfo().GetModelName()
        << ", " << cameras[i].DeviceSerialNumber.GetValue()
        << endl;
    }
  } catch (const GenericException& e) {
		// Error handling
		cerr << "Cannot setup cameras! " << endl << e.GetDescription() << endl;
		exit(1);
  }
  ostringstream ss;
  ss << cameras[0].DeviceSerialNumber.GetValue();
  string serial1 = ss.str();
  if (serial1.find("711") == string::npos)  // 711 should be the first camera
    rev = true;
  cout << "Reverse camera order: " << rev << endl;


	// Starts grabbing for all cameras starting with index 0. The grabbing
	// is started for one camera after the other. That's why the images of all
	// cameras are not taken at the same time.
	// However, a hardware trigger setup can be used to cause all cameras to
	// grab images synchronously.
	// According to their default configuration, the cameras are
	// set up for free-running continuous acquisition.
	cameras.StartGrabbing();

	cout << "Start grabbing ..." << endl;

	// This smart pointer will receive the grab result data.
	CGrabResultPtr ptrGrabResult;
	Pylon::CImageFormatConverter formatConverter;
	formatConverter.OutputPixelFormat = Pylon::PixelType_BGR8packed;
	Pylon::CPylonImage pylonImage;
	cv::Mat openCVImage;

	try {
		while (cameras.IsGrabbing() && not camera.is_stopped()) {
			cameras.RetrieveResult(5000, ptrGrabResult, TimeoutHandling_ThrowException);
			if (ptrGrabResult->GrabSucceeded()) {
				formatConverter.Convert(pylonImage, ptrGrabResult);
				openCVImage = cv::Mat(
						ptrGrabResult->GetHeight(),
						ptrGrabResult->GetWidth(),
						CV_8UC3,
						(uint8_t *)pylonImage.GetBuffer());
				// When the cameras in the array are created the camera context value
        // is set to the index of the camera in the array.
        // The camera context is a user settable value.
        // This value is attached to each grab result and can be used
        // to determine the camera that produced the grab result.
        intptr_t cameraContextValue = ptrGrabResult->GetCameraContext();
        int index = rev ? 1 - cameraContextValue : cameraContextValue;

        camera.m_camera_buffer[index].write(openCVImage);
			}
		}
	} catch (const GenericException &e) {
		// Error handling
		cerr << "An exception occurred! " << endl << e.GetDescription() << endl;
		exit(1);
	}
}

void Camera::setup() {
  m_assert(!m_worker_th.joinable());
	m_worker_th = thread([&] {
			PylonInitialize();
			worker(*this);
			PylonTerminate();
	});
	// wait for all cameras to be ready
  while (num_cameras == 0)
		this_thread::sleep_for(chrono::milliseconds(300));
  for (int i = 0; i < num_cameras; ++i)
    while (m_camera_buffer[i].empty())
      this_thread::sleep_for(chrono::milliseconds(300));
  cout << "Initialized " << num_cameras << " cameras !" << endl;
}

