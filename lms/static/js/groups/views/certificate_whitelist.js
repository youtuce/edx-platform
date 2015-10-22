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
                    var response = xhr;
                    var $message_div = $(".error-message");
                    $message_div.html('<div class="msg-success">*' + response.message + '</div>');

                    $('html, body').animate({
                        scrollTop: $message_div.offset().top
                    }, 1000);
                },

                showError: function(xhr, status, options){
                    var response = JSON.parse(xhr.responseText);
                    var $message_div = $(".error-message");
                    $message_div.html('<div class="msg-error">*' + response.message + '</div>');

                    $('html, body').animate({
                        scrollTop: $message_div.offset().top
                    }, 1000);
                }

            });
        }
    )
}).call(this, define || RequireJS.define);