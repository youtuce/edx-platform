(function(requirejs) {
    requirejs.config({
        paths: {
            "moment": "xmodule/include/common_static/js/vendor/moment.min",
            "draggabilly": "xmodule/include/common_static/js/vendor/draggabilly.pkgd"
        },
        "moment": {
            exports: "moment"
        },
        "draggabilly": {
            exports: "Draggabilly"
        }
    });

}).call(this, RequireJS.requirejs);
