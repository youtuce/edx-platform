// Backbone.js Application Model: CertificateWhitelist

;(function(define){
    define([
            'underscore',
            'underscore.string',
            'backbone',
            'gettext'
        ],

        function(_, str, Backbone, gettext){
            'use strict';

            return Backbone.Model.extend({
                idAttribute: 'id',

                defaults: {
                    user_id: '',
                    user_name: '',
                    user_email: '',
                    modified: '',
                    free_text: ''
                },

                validate: function(attrs){
                    if (!_.string.trim(attrs.user_name) && !_.string.trim(attrs.user_email)) {
                        return gettext('Student username/email is required.');
                    }

                }
            });
        }
    )
}).call(this, define || RequireJS.define);