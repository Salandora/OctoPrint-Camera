from . import ICamera

from time import sleep
import cv2
import logging
import threading

# highly inspired by https://github.com/miguelgrinberg/flask-video-streaming/blob/master/camera_pi.py
class OpenCVCamera(ICamera):

	def __init__(self):
		self._logger = logging.getLogger("octoprint.plugins.camera")
		self.running = False
		self.thread = None
		self.frame = None

		self.frameLock = threading.Lock()

	def startCamera(self):
		if self.thread is None:
			self.running = True
			self.thread = threading.Thread(target=self._thread)
			self.thread.start()

			while self.running and self.frame is None:
				sleep(1)

	def _cameraOpen(self):
		return self._camera is not None and self._camera.isOpened()

	def openCamera(self):
		self._camera = cv2.VideoCapture(0)
		if not self._cameraOpen():
			self._logger.error("Couldn't open camera")
			return False

		try:
			self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
			self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
		except Exception as e:
			self._logger.error('Error setting camera frame to 640x480 size: %s' % e)
			return False

		return True

	def close(self):
		self.running = False
		if not self._camera:
			return

		self._camera.release()

	def _thread(cls):
		if not cls.openCamera():
			cls.running = False
			cls.thread = None
			return

		while cls.running:
			success = cls._camera.grab()
			if success:
				success, image = cls._camera.retrieve()
				if success:
					with cls.frameLock:
						cls.frame = image

		cls.thread = None
		cls.close()

	def grabImage(self):
		self.startCamera()
		with self.frameLock:
			ret, jpeg = cv2.imencode('.jpg', self.frame)
			return jpeg.tostring()

