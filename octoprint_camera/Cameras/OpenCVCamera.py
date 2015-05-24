from . import ICamera

from time import sleep, time
import cv2
import logging
import threading

current_milli_time = lambda: int(round(time() * 1000))

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

	def openCamera(self):
		self._camera = cv2.VideoCapture(0)
		if not self._camera.isOpened():
			self._logger.error("Couldn't open camera")
			return False

		try:
			self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
			self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

			self._camera.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
			self._camera.set(cv2.CAP_PROP_FORMAT, cv2.CAP_MODE_YUYV)

			self._camera.set(cv2.CAP_PROP_FPS, 30)
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

		frames = 0
		start = current_milli_time()
		while cls.running:
			successRead, image = cls._camera.read()
			if successRead:
				frames += 1
				with cls.frameLock:
					cls.frame = image

			if current_milli_time() - start >= 1000:
				cls._logger.info("%d fps" % frames)
				frames = 0
				start = current_milli_time()

		cls.thread = None
		cls.close()

	def grabImage(self):
		with self.frameLock:
			ret, jpeg = cv2.imencode('.jpg', self.frame)
			return jpeg.tostring() if ret else None

