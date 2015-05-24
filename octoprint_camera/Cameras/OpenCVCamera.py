from . import ICamera

from time import sleep, time
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

	def close(self):
		self.running = False
		if not self._camera:
			return

		self._camera.release()

	def startCamera(self):
		if self.thread is None:
			self.running = True
			self.thread = threading.Thread(target=self._thread)
			self.thread.start()

	def openCamera(self):
		self._camera = cv2.VideoCapture(0)
		if not self._camera.isOpened():
			self._logger.error("Couldn't open camera")
			return False

		self._logger.info("Camera FPS: %d" % self._camera.get(cv2.CAP_PROP_FPS))
		return True

	def setCameraSize(self, width=640, height=480):
		try:
			self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
			self._logger.info("Camera Width: %d" % self._camera.get(cv2.CAP_PROP_FRAME_WIDTH))

			self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
			self._logger.info("Camera Height: %d" % self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
		except Exception as e:
			self._logger.exception('Error setting camera Size to %dx%d: %s' % (width, height, e))

	def _thread(cls):
		if not cls.openCamera():
			cls.running = False
			cls.thread = None
			return

		frames = 0
		start = current_milli_time()
		while cls.running:
			successRead, image = cls._camera.read()
			if successRead:
				frames += 1
				with cls.frameLock:
					cls.frame = image

		cls.thread = None
		cls.close()

	def grabImage(self):
		with self.frameLock:
			ret, jpeg = cv2.imencode('.jpg', self.frame)
			return jpeg.tostring() if ret else None

