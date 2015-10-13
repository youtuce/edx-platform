/**
 * Track interaction with the student dashboard..
 */

var edx = edx || {};

(function ($) {
    'use strict';

    edx.dashboard = edx.dashboard || {};

    edx.dashboard.TrackEvents = function() {

         var course_title_link = $(".course-title > a"),
            course_image_link = $(".cover"),
            enter_course_link = $(".enter-course"),
            options_dropdown = $(".wrapper-action-more"),
            course_learn_verified = $(".message-copy > a"),
            find_courses_btn = $(".btn-find-courses");

        // Track a virtual pageview, for easy funnel reconstruction.
        window.analytics.page('student', 'dashboard' );

        // Emit an event when the "course title link" is clicked.
        window.analytics.trackLink(
            course_title_link,
            "edx.bi.dashboard.course_title.clicked",
            {
                category: "dashboard",
                label: course_title_link.data("course-key")
            }
        );

        // Emit an event  when the "course image" is clicked.
        window.analytics.trackLink(
            course_image_link,
            "edx.bi.dashboard.course_image.clicked",
            {
                category: "dashboard",
                label: course_image_link.data("course-key")
            }

        );

        // Emit an event  when the "View Course" button is clicked.
        window.analytics.trackLink(
            enter_course_link,
            "edx.bi.dashboard.enter_course.clicked",
            {
                category: "dashboard",
                label: enter_course_link.data("course-key")
            }
        );

        // Emit an event when the options dropdown is engaged.
        window.analytics.trackLink(
            options_dropdown,
            "edx.bi.dashboard.course_options_dropdown.clicked",
            {
                category: "dashboard",
                label: options_dropdown.data("course-key")
            }
        );

        // Emit an event  when the "Learn about verified" link is clicked.
        window.analytics.trackLink(
            course_learn_verified,
            "edx.bi.dashboard.verified_info_link.clicked",
            {
                category: "dashboard",
                label: course_learn_verified.data("course-key")
            }
        );

        // Emit an event  when the "Find Courses" button is clicked.
        window.analytics.trackLink(
            find_courses_btn,
            "edx.bi.dashboard.find_courses_button.clicked",
            {
                category: "dashboard",
                label: null
            }
        );
    };

    $(document).ready(function() {

        edx.dashboard.TrackEvents();

    });
})(jQuery);
