# coding=utf-8
from __future__ import absolute_import


### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin.
#
# Take a look at the documentation on what other plugin mixins are available.

import cv2
import flask
import logging
import octoprint.plugin

class CameraPlugin(octoprint.plugin.TemplatePlugin, octoprint.plugin.BlueprintPlugin):
	def __init__(self, *args, **kwargs):
		self._camera = None

	def _openCamera(self):
		self._camera = cv2.VideoCapture(0)

		try:
			self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
			self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
		except Exception as e:
			self._logger.error('Error setting camera frame to 800x448 size: %s' % e)
			return False

		try:
			self._getFrame()
		except:
			return False

		return True

	def _getFrame(self):
		if self._camera is None:
			if not self._openCamera():
				return None

		for i in range(5):
			self._camera.retrieve() # some garbage

		try:
			success, image = self._camera.retrieve()
		except:
			success = False

		if success:
			ret, jpeg = cv2.imencode('.jpg', image)
			return jpeg.tobytes()

		return None

	def is_blueprint_protected(self):
		return False

	@octoprint.plugin.BlueprintPlugin.route("/grabPic", methods=["GET"])
	def grabPic(self):
		frame = self._getFrame()
		if frame is None:
			return flask.make_response("Something went wrong while creating Capture Object", 500);
		
		return flask.Response(frame, mimetype='image/jpeg')


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Camera Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CameraPlugin()

	# global __plugin_hooks__
	# __plugin_hooks__ = {"some.octoprint.hook": __plugin_implementation__.some_hook_handler}
