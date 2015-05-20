from . import ICamera
import cv2

class OpenCVCamera(ICamera):
	"""description of class"""
	def __init__(self):
		self.openCamera()

	def openCamera(self):
		self._camera = cv2.VideoCapture(0)

		if not self._camera.isOpened():
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

	def genVideo(self):
		while True:
			frame = self.grabImage()
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

