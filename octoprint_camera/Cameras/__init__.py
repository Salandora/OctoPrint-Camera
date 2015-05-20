from sys import platform
import logging

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

	def __del__(self):
		close()

	def close(self): 
		pass

	def grabImage(self):
		pass
