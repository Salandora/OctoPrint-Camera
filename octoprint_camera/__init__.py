# coding=utf-8
from __future__ import absolute_import


### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin.
#
# Take a look at the documentation on what other plugin mixins are available.

from flask import make_response, render_template, Response
import logging
import tornado
import tornado.web
import octoprint.plugin

from .Cameras import getCameraObject

class CameraPlugin(octoprint.plugin.StartupPlugin,
				   octoprint.plugin.ShutdownPlugin,
				   octoprint.plugin.SettingsPlugin):
	def __init__(self, *args, **kwargs):
		self._logger = logging.getLogger("octoprint.plugins.camera")

	def __del__(self):
		if self._camera is not None:
			self._camera.close()

	def on_startup(self, host, port):
		self._camera = getCameraObject()
		if self._camera is None:
			self._core_logger.error("Camera Object was not created correctly")

		self._camera.startCamera()

	def on_shutdown(self):
		self._camera.close()

	def routes_hook(self, current_routes):
		return [
			(r"/camera/grabImage", CameraResponseHandler, dict())
		]

class CameraResponseHandler(tornado.web.RequestHandler):
	def initialize(self, access_validation=None):
		self._camera = getCameraObject()
		self._access_validation = access_validation

	def get(self, *args, **kwargs):
		if self._access_validation is not None:
			self._access_validation(self.request)

		if self._camera is None:
			return make_response("Something went wrong while creating Video Capture Object", 500);

		frame = self._camera.grabImage()
		if frame is None:
			return make_response("Something went wrong while grabbing an Image", 500);

		self.set_header("Content-Type", "image/jpeg")
		self.write(frame)
		self.finish()

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Camera Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CameraPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {"octoprint.server.http.routes": __plugin_implementation__.routes_hook}
