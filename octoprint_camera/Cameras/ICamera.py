class ICamera(object):
    """Camera Interface Class"""
	def __init__(self, *args, **kwargs):
		pass

	def __del__(self):
		close()

	def close(self): 
		pass

	def grabImage(self):
		pass

