// Backbone.js Application Collection: CertificateWhitelist

;(function(define){
    define([
            'backbone',
            'gettext',
            'js/groups/models/certificate_exception'
        ],

        function(Backbone, gettext, CertificateException){
            'use strict';

            var CertificateWhitelist =  Backbone.Collection.extend({
                model: CertificateException,

                /**
                 * It represents the maximum number of CertificateExceptions that a user can create. default set to 10.
                 */
                maxAllowed: 10,

                url: '',

                initialize: function(attrs, options){
                    this.url = options.url;
                    this.bind('add', this.addModel, this);
                    this.bind('remove', this.removeModel, this);
                },

                addModel: function(){
                    this.toggleAddNewItemButtonState();
                },

                removeModel: function(){
                    this.toggleAddNewItemButtonState();
                },

                toggleAddNewItemButtonState: function() {
                    // user can create a new item e.g CertificateException; if not exceeded the maxAllowed limit.
                    if(this.length >= this.maxAllowed) {
                        $("#add-to-white-list").addClass('action-add-hidden');
                    } else {
                        $("#add-to-white-list").removeClass('action-add-hidden');
                    }
                },

                newCertificateWhitelist: function(){
                    var filtered = this.filter(function(certificate_exception){
                        return !certificate_exception.get('id');
                    });

                    return new CertificateWhitelist(filtered, {url: this.url});
                },

                parse: function (certificate_whitelist_json) {
                    // Transforms the provided JSON into a CertificateWhitelist collection
                    var modelArray = this.certificate_whitelist(certificate_whitelist_json);

                    for (var i in modelArray) {
                        if (modelArray.hasOwnProperty(i)) {
                            this.push(modelArray[i]);
                        }
                    }
                    return this.models;
                },

                certificate_whitelist: function(certificate_whitelist_json) {
                    var return_array;

                    try {
                        return_array = JSON.parse(certificate_whitelist_json);
                    } catch (ex) {
                        // If it didn't parse, and `certificate_whitelist_json` is an object then return as it is
                        // otherwise return empty array
                        if (typeof certificate_whitelist_json === 'object'){
                            return_array = certificate_whitelist_json;
                        }
                        else {
                            console.error(
                                interpolate(
                                    gettext('Could not parse certificate JSON. %(message)s'), {message: ex.message}, true
                                )
                            );
                            return_array = [];
                        }
                    }
                    return return_array;
                }

            });

            return CertificateWhitelist;
        }
    )
}).call(this, define || RequireJS.define);