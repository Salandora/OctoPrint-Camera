# coding=utf-8
from __future__ import absolute_import


### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin.
#
# Take a look at the documentation on what other plugin mixins are available.

from flask import make_response, Response
import logging
import octoprint.plugin

from .Cameras import getCameraObject

class CameraPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.SettingsPlugin,
				   octoprint.plugin.TemplatePlugin, 
			  	   octoprint.plugin.AssetPlugin,
				   octoprint.plugin.BlueprintPlugin):
	def __init__(self, *args, **kwargs):
		self._logger = logging.getLogger("octoprint.plugins.camera")
		self._core_logger = logging.getLogger("octoprint.plugins.camera.core")

		self._camera = getCameraObject(self._core_logger)
		if self._camera is None:
			self._core_logger.error("Camera Object was not created correctly")

	def on_startup(self, host, port):
		# setup our custom logger
		core_logging_handler = logging.handlers.RotatingFileHandler(self._settings.get_plugin_logfile_path(postfix="core"), maxBytes=2*1024*1024)
		core_logging_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
		core_logging_handler.setLevel(logging.DEBUG)

		self._core_logger.addHandler(core_logging_handler)
		self._core_logger.setLevel(logging.DEBUG if self._settings.get_boolean(["debug_logging"]) else logging.CRITICAL)
		self._core_logger.propagate = False

	def is_blueprint_protected(self):
		return False

	def get_assets(self):
		return dict(
			js=["js/camera.js"],
		)

	@octoprint.plugin.BlueprintPlugin.route("/grabPic", methods=["GET"])
	def grabPic(self):
		if self._camera is None:
			return make_response("Something went wrong while creating Video Capture Object", 500);

		frame = self._camera.grabImage()
		if frame is None:
			return make_response("Something went wrong while grabbing an Image", 500);
		
		return Response(frame, mimetype='image/jpeg')


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Camera Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CameraPlugin()

	# global __plugin_hooks__
	# __plugin_hooks__ = {"some.octoprint.hook": __plugin_implementation__.some_hook_handler}
