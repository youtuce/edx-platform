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
                    this.certificateWhiteList.sync('create', this.certificateWhiteList.newCertificateWhitelist(), {
                        success: this.showSuccess,
                        error: this.showError
                    });
                },

                showSuccess: function(xhr, status, options){
                    var response = JSON.parse(xhr. responseText);
                    console.log(response.message);
                },

                showError: function(xhr, status, options){
                    var response = JSON.parse(xhr. responseText);
                    $(".error-message").text(response.message);
                    console.log(response.message)
                }

            });
        }
    )
}).call(this, define || RequireJS.define);