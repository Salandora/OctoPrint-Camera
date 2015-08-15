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

IMAGE_FORMAT = "image/jpeg"

class CameraPlugin(octoprint.plugin.StartupPlugin,
				   octoprint.plugin.ShutdownPlugin,
				   octoprint.plugin.AssetPlugin,
				   octoprint.plugin.TemplatePlugin,
				   octoprint.plugin.SettingsPlugin):
	def __init__(self, *args, **kwargs):
		self._logger = logging.getLogger("octoprint.plugins.camera")
		self._camera = getCameraObject()

	def get_template_configs(self):
		return [dict(type="settings", custom_bindings=True)]

	def get_assets(self):
		return dict(js=["js/camera.js"])

	def get_settings_defaults(self):
		return dict(
			videoCaptureInput = 0,
			size = dict(width=640, height=480),
			format = "image/jpeg"
		)

	def on_settings_save(self, data):
		oldVideoCaptureInput = self._settings.get_int(["videoCaptureInput"])
		oldSize = self._settings.get(["size"])

		super(CameraPlugin, self).on_settings_save(data)

		IMAGE_FORMAT = self._settings.get(["format"])

		if oldVideoCaptureInput != self._settings.get_int(["videoCaptureInput"]):
			self._camera.openCamera(self._settings.get_int(["videoCaptureInput"]))

		if oldSize != self._settings.get(["size"]):
			self._camera.stopCamera()
			self._camera.setCameraSize(self._settings.get_int(["size", "width"]), self._settings.get_int(["size", "height"]))
		
		self._camera.startCamera()

	def on_after_startup(self):
		if self._camera is None:
			self._core_logger.error("Camera Object was not created correctly")
			return

		IMAGE_FORMAT = self._settings.get(["format"])

		self._camera.openCamera(self._settings.get_int(["videoCaptureInput"]))
		self._camera.setCameraSize(self._settings.get_int(["size", "width"]), self._settings.get_int(["size", "height"]))
		self._camera.startCamera()

	def on_shutdown(self):
		if self._camera:
			self._camera.close()

	def routes_hook(self, current_routes):
		return [
			(r"grabImage", ImageResponseHandler, dict(imageFunc=self._camera.grabImage))
		]

class ImageResponseHandler(tornado.web.RequestHandler):
	def initialize(self, imageFunc, access_validation=None):
		self._imageFunc = imageFunc
		self._access_validation = access_validation

	def get(self, *args, **kwargs):
		if self._access_validation is not None:
			self._access_validation(self.request)

		if self._imageFunc is None:
			raise tornado.web.HTTPError(500);

		frame = self._imageFunc()
		if frame is None:
			raise tornado.web.HTTPError(500);

		self.set_header("Content-Type", IMAGE_FORMAT)
		self.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
		self.set_header("Pragma", "no-cache")
		self.set_header("Expires", "0")
		
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
