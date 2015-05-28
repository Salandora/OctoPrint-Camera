$(function() {
    function CameraViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        self.selectedSize = ko.observable();

        self.resolutions = [
            { id: 3, value: { width: 1024, height: 768 } },
            { id: 2, value: { width: 800, height: 600 } },
            { id: 1, value: { width: 640, height: 480 } },
            { id: 0, value: { width: 320, height: 240 } },
        ];

        self.resolutionToText = function(data) {
            return data.value.width + 'x' + data.value.height;
        }

        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings.plugins.camera;
            
            var tmp = _.find(self.resolutions, function (item) {
                return (item.value.width == self.settings.size.width() && item.value.height == self.settings.size.height());
            });
            self.selectedSize(tmp !== undefined ? tmp.id : 0);
        }

        self.onSettingsBeforeSave = function () {
            var tmp = _.find(self.resolutions, function (item) { return item.id == self.selectedSize(); });
            if (tmp === undefined)
                tmp = _.last(self.resolutions);

            self.settings.size.width(tmp.value.width);
            self.settings.size.height(tmp.value.height);
        }
    }

    OCTOPRINT_VIEWMODELS.push([
        CameraViewModel,
        ["settingsViewModel"],
        ["#settings_plugin_camera"]
    ]);
});