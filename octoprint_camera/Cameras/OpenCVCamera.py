from . import ICamera
import cv2
import logging

class OpenCVCamera(ICamera):
	"""description of class"""
	def __init__(self):
		self._core_logger = logging.getLogger("octoprint.plugins.camera.core")
		openCamera(self)

	def openCamera(self):
		self._camera = cv2.VideoCapture(0)
		if not self._camera.isOpened():
			self._logger.error("Couldn't open camera")
			return False

		try:
			self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
			self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
		except Exception as e:
			self._logger.error('Error setting camera frame to 640x480 size: %s' % e)
			return False

		for i in range(5):
			self.grabImage()

		return True

	def close(self): 
		if not self._camera:
			return

		self._camera.release()

	def grabImage(self):
		if self._camera is None:
			if not self.openCamera():
				return None

		try:
			success, image = self._camera.read()
		except:
			success = False

		if success:
			ret, jpeg = cv2.imencode('.jpg', image)
			return jpeg.tobytes()

		return None

