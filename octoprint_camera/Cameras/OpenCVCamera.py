from . import ICamera

from octoprint.server import debug
import cv2
import logging
import threading

def isOpenCV3():
	return cv2.__version__.startswith("3.")

if not isOpenCV3():
	import cv2.cv
	
	PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
	PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
	PROP_FPS = cv2.cv.CV_CAP_PROP_FPS
else:
	PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
	PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
	PROP_FPS = cv2.CAP_PROP_FPS

#debug = True

# highly inspired by https://github.com/miguelgrinberg/flask-video-streaming/blob/master/camera_pi.py
class OpenCVCamera(ICamera):
	def __init__(self):
		self._logger = logging.getLogger("octoprint.plugins.camera")
		self._camera = None

		self.running = False
		self.thread = None
		
		if debug:		
			self._timer = CvTimer()

		self._frame = None
		self.frame = None
		self.newImage = True

		self.frameLock = threading.Lock()

	def close(self):
		self.stopCamera()
		if not self._camera:
			return

		self._camera.release()
		del self._camera

	def startCamera(self):
		if self.thread is None:
			self.running = True
			self.thread = threading.Thread(target=self._thread)
			self.thread.start()

	def stopCamera(self):
		self.running = False
		if self.thread:
			self.thread.join()

		self.thread = None

	def openCamera(self, videoCaptureInput):
		if self._camera and self._camera.isOpened():
			self.close()

		self._camera = cv2.VideoCapture(videoCaptureInput)
		if not self._camera.isOpened():
			self._logger.error("Couldn't open camera")
			return False

		self._logger.info("Camera FPS: %d" % self._camera.get(PROP_FPS))
		return True

	def setCameraSize(self, width, height):
		if width is None or height is None:
			if width is None:
				self._logger.warning("Unable to set width and height, because parameter 'width' is None")
			if height is None:
				self._logger.warning("Unable to set width and height, because parameter 'height' is None")

			return

		try:
			ret = self._camera.set(PROP_FRAME_WIDTH, width)
			if ret:
				ret = self._camera.set(PROP_FRAME_HEIGHT, height)

				self._logger.info("Camera {Width: %d, Height %d}", self._camera.get(PROP_FRAME_WIDTH), self._camera.get(PROP_FRAME_HEIGHT))
			else:
				self._logger.error("Unable to set new Frame Width/Height")
		except Exception as e:
			self._logger.exception('Error setting camera Size to %dx%d: %s' % (width, height, e))

	def _thread(cls):
		while cls.running:
			if debug:		
				cls._timer.mark_new_frame()

			successRead, image = cls._camera.read()
			if successRead:
				with cls.frameLock:
					if debug:	
						cv2.putText(image, "fps=%s avg=%s" % (cls._timer.fps, cls._timer.avg_fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
						cv2.putText(image, "frame=%s" % (cls._timer.frame_num), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

					cls._frame = image
					cls.newImage = True

	def grabImage(self):
		with self.frameLock:
			if self._frame is not None or self.frame:
				if self.newImage:
					ret, jpeg = cv2.imencode('.jpg', self._frame)
					self.frame = jpeg.tostring()
					self.newImage = False

				return self.frame
		return None

def circular_counter(max):
    """helper function that creates an eternal counter till a max value"""
    x = 0
    while True:
        if x == max:
            x = 0
        x += 1
        yield x
 
class CvTimer(object):
    def __init__(self):
        self.tick_frequency = cv2.getTickFrequency()
        self.tick_at_init = cv2.getTickCount()
        self.last_tick = self.tick_at_init
        self.fps_len = 100
        self.l_fps_history = [ 10 for x in range(self.fps_len)]
        self.fps_counter = circular_counter(self.fps_len)
        self.frame_num = 0

    def mark_new_frame(self):
        self.last_tick = cv2.getTickCount()
        self.frame_num += 1

    def get_tick_now(self):
        return cv2.getTickCount()

    @property
    def fps(self):
        fps = self.tick_frequency / (self.get_tick_now() - self.last_tick)
        self.l_fps_history[self.fps_counter.next() - 1] = fps
        return int(fps)

    @property
    def avg_fps(self):
        return int(sum(self.l_fps_history) / float(self.fps_len))
