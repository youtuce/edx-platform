(function (define) {
    'use strict';
    define([
        'jquery',
        'js/dashboard/track_events'
    ],
    function($) {

        describe("edx.dashboard.TrackEvents", function() {

            var GA_PROPERTIES = {
                category: "dashboard",
                label: "edX/DemoX/Demo_Course"
            };

            beforeEach(function() {
                // Stub the analytics event tracker
                window.analytics = jasmine.createSpyObj('analytics', ['track', 'page', 'trackLink']);
                loadFixtures('js/fixtures/dashboard/dashboard.html');
                window.edx.dashboard.TrackEvents();
            });

            it("sends an analytics event when the user clicks course title link", function() {
                // Verify that analytics events fire when the "course title link" is clicked.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".course-title > a"),
                    "edx.bi.dashboard.course_title.clicked",
                     GA_PROPERTIES
                );
            });

            it("sends an analytics event when the user clicks course image link", function() {
                // Verify that analytics events fire when the "course image link" is clicked.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".cover"),
                    "edx.bi.dashboard.course_image.clicked",
                    GA_PROPERTIES
                );
            });


            it("sends an analytics event when the user clicks enter course link", function() {
                // Verify that analytics events fire when the "enter course link" is clicked.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".enter-course"),
                    "edx.bi.dashboard.enter_course.clicked",
                    GA_PROPERTIES
                );
            });

            it("sends an analytics event when the user clicks enter course link", function() {
                // Verify that analytics events fire when the options dropdown is engaged.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".wrapper-action-more"),
                    "edx.bi.dashboard.course_options_dropdown.clicked",
                    GA_PROPERTIES
                );
            });

            it("sends an analytics event when the user clicks the learned about verified track link", function() {
                //Verify that analytics events fire when the "Learned about verified track" link is clicked.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".message-copy > a"),
                    "edx.bi.dashboard.verified_info_link.clicked",
                    GA_PROPERTIES
                );
            });

            it("sends an analytics event when the user clicks find courses button", function() {
                // Verify that analytics events fire when the "user clicks find the course" button.
                expect(window.analytics.trackLink).toHaveBeenCalledWith(
                    $(".btn-find-courses"),
                    "edx.bi.dashboard.find_courses_button.clicked",
                    {
                        category: "dashboard",
                        label: null
                    }
                );
            });
        });
    });
}).call(this, window.define);
