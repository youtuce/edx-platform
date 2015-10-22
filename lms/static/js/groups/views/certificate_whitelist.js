// Backbone Application View: CertificateWhitelist View

;(function(define){
    define([
            'jquery',
            'underscore',
            'gettext',
            'backbone'
        ],

        function($, _, gettext, Backbone){
            return Backbone.View.extend({
                el: "#white-listed-students",

                events: {
                    'click #generate-exception-certificates': 'generateExceptionCertificates'
                },

                initialize: function(options){
                    this.certificateWhiteList = options.certificateWhiteList;

                    // Re-render the view when an item is added to the collection
                    this.listenTo(this.certificateWhiteList, 'add', this.render);
                },

                render: function(){
                    var template = this.loadTemplate('certificate-white-list');

                    this.$el.html(template({certificates: this.certificateWhiteList.models}));

                },

                loadTemplate: function(name) {
                    var templateSelector = "#" + name + "-tpl",
                    templateText = $(templateSelector).text();
                    return _.template(templateText);
                },

                generateExceptionCertificates: function(){
                    console.log(this.certificateWhiteList.toJSON());
                    this.certificateWhiteList.sync('create', this.certificateWhiteList.newCertificateWhitelist(), {
                        success: function(){console.log("Collection updated on server.")},
                        error: function(){console.log("Error while saving on server.")}
                    });
                }

            });
        }
    )
}).call(this, define || RequireJS.define);