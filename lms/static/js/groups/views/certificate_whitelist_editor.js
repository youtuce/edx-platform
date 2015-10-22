// Backbone Application View: CertificateWhitelist View

;(function(define){
    define([
            'jquery',
            'underscore',
            'gettext',
            'backbone',
            'js/groups/models/certificate_exception'
        ],

        function($, _, gettext, Backbone, CertificateException){
            return Backbone.View.extend({
                el: "#certificate-white-list-editor",
                error_div: '.error-message',

                events: {
                    'click #add-to-white-list': 'addToWhiteList'
                },

                initialize: function(options){
                    this.certificateWhiteList = options.certificateWhiteList;
                },

                render: function(){
                    var template = this.loadTemplate('certificate-white-list-editor');

                    this.$el.html(template());

                },

                loadTemplate: function(name) {
                    var templateSelector = "#" + name + "-tpl",
                    templateText = $(templateSelector).text();
                    return _.template(templateText);
                },

                addToWhiteList: function(){
                    var value = $("#certificate-exception").val();
                    var free_text = $("#free-text-notes").val();

                    var user_email = '', user_name='';

                    if(this.isEmailAddress(value))
                        user_email = value;
                    else
                        user_name = value;

                    var certificate_exception = new CertificateException({
                        user_name: user_name,
                        user_email: user_email,
                        free_text: free_text,
                        'modified': new Date()
                    });

                    if(certificate_exception.isValid())
                        this.certificateWhiteList.add(certificate_exception, {validate: true});
                    else
                        this.showErrorMessage(certificate_exception.validationError);
                },

                isEmailAddress: function validateEmail(email) {
                    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
                    return re.test(email);
                },

                showErrorMessage: function(message){
                    $(this.error_div).append("<div class='error'>" + message + "</div>");
                }

            });
        }
    )
}).call(this, define || RequireJS.define);