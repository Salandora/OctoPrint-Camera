$(function () {
    function CameraViewModel(parameters) {
        self.imageNr = 0; // Serial number of current image
        self.imgSrc = ko.observable();
        self.fps = ko.observable(20);
        self.imgBaseUrl = $("#cameraObj").attr("data-url");
        
        self.imageLoaded = function () {
            if (!self.paused) {
                setTimeout(function () { self.createImageLayer() }, 1000 / self.fps());
            }
        };

        self.createImageLayer = function () {
            self.imgSrc(self.imgBaseUrl + "?n=" + (++self.imageNr))
        }

        self.imageOnClick = function () {
            self.paused = !self.paused;
            if (!self.paused) {
                self.createImageLayer();
            }
        }

        self.imageLoaded();
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        CameraViewModel,
        [],
        "#tab_plugin_camera"
    ]);
});