from sys import platform

_instance = None

def getCameraObject():
	global _instance
	if _instance is None:
		if "linux" in platform or platform == "win32":
			from .OpenCVCamera import OpenCVCamera
			_instance = OpenCVCamera()			

	return _instance

class ICamera(object):
	"""Camera Interface Class"""
	def __init__(self):
		pass

	def close(self): 
		pass

	def startCamera(self, videoCaptureInput):
		pass

	def setCameraSize(self, width, height):
		pass

	def grabImage(self):
		pass
