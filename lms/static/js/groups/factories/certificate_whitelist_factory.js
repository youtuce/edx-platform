// Backbone.js Page Object Factory: Certificates

;(function(define){
    define([
            'jquery',
            'js/groups/views/certificate_whitelist',
            'js/groups/views/certificate_whitelist_editor',
            'js/groups/collections/certificate_whitelist'
        ],
        function($, CertificateWhitelistView, CertificateWhitelistEditor ,CertificateWhitelistCollection){
            return function(certificate_white_list_json, certificate_exception_url){

                var certificateWhiteList = new CertificateWhitelistCollection(certificate_white_list_json, {
                    parse: true,
                    canBeEmpty: true,
                    url: certificate_exception_url
                });

                new CertificateWhitelistView({
                    certificateWhiteList:certificateWhiteList
                }).render();

                new CertificateWhitelistEditor({
                    certificateWhiteList:certificateWhiteList
                }).render();
            }
        }
    )
}).call(this, define || RequireJS.define);