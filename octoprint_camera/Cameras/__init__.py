from sys import platform

_instance = None

def getCameraObject(logger):
	global _instance
	if _instance is None:
		if "linux" in platform or platform == "win32":
			from .OpenCVCamera import OpenCVCamera
			_instance = OpenCVCamera(logger)			

	return _instance

class ICamera(object):
	"""Camera Interface Class"""
	def __init__(self):
		pass

	def close(self): 
		pass

	def __del__(self):
		self.close()

	def grabImage(self):
		pass
