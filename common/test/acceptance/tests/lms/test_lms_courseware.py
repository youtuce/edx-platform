# -*- coding: utf-8 -*-
"""
End-to-end tests for the LMS.
"""
import time

from ..helpers import UniqueCourseTest
from ...pages.studio.auto_auth import AutoAuthPage
from ...pages.lms.create_mode import ModeCreationPage
from ...pages.studio.overview import CourseOutlinePage
from ...pages.lms.courseware import CoursewarePage, CoursewareSequentialTabPage
from ...pages.lms.course_nav import CourseNavPage
from ...pages.lms.problem import ProblemPage
from ...pages.common.logout import LogoutPage
from ...pages.lms.track_selection import TrackSelectionPage
from ...pages.lms.pay_and_verify import PaymentAndVerificationFlow, FakePaymentPage
from ...pages.lms.dashboard import DashboardPage
from ...fixtures.course import CourseFixture, XBlockFixtureDesc


class CoursewareTest(UniqueCourseTest):
    """
    Test courseware.
    """
    USERNAME = "STUDENT_TESTER"
    EMAIL = "student101@example.com"

    def setUp(self):
        super(CoursewareTest, self).setUp()

        self.courseware_page = CoursewarePage(self.browser, self.course_id)

        self.course_outline = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        # Install a course with sections/problems, tabs, updates, and handouts
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section 1').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection 1').add_children(
                    XBlockFixtureDesc('problem', 'Test Problem 1')
                )
            ),
            XBlockFixtureDesc('chapter', 'Test Section 2').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection 2').add_children(
                    XBlockFixtureDesc('problem', 'Test Problem 2')
                )
            )
        ).install()

        # Auto-auth register for the course.
        self._auto_auth(self.USERNAME, self.EMAIL, False)

    def _goto_problem_page(self):
        """
        Open problem page with assertion.
        """
        self.courseware_page.visit()
        self.problem_page = ProblemPage(self.browser)
        self.assertEqual(self.problem_page.problem_name, 'TEST PROBLEM 1')

    def _auto_auth(self, username, email, staff):
        """
        Logout and login with given credentials.
        """
        AutoAuthPage(self.browser, username=username, email=email,
                     course_id=self.course_id, staff=staff).visit()

    def test_courseware(self):
        """
        Test courseware if recent visited subsection become unpublished.
        """

        # Visit problem page as a student.
        self._goto_problem_page()

        # Logout and login as a staff user.
        LogoutPage(self.browser).visit()
        self._auto_auth("STAFF_TESTER", "staff101@example.com", True)

        # Visit course outline page in studio.
        self.course_outline.visit()

        # Set release date for subsection in future.
        self.course_outline.change_problem_release_date_in_studio()

        # Logout and login as a student.
        LogoutPage(self.browser).visit()
        self._auto_auth(self.USERNAME, self.EMAIL, False)

        # Visit courseware as a student.
        self.courseware_page.visit()
        # Problem name should be "TEST PROBLEM 2".
        self.assertEqual(self.problem_page.problem_name, 'TEST PROBLEM 2')

    def test_skip_navigation(self):
        """
        Skip navigation functions as intended.
        """

        # Navigate to a course
        self.courseware_page.visit()

        # Verify the skip container is present
        self.courseware_page.verify_skip_to_container_exists()

        # Activate the link and expect focus to be on the #href
        # self.courseware_page.skip_to_main_content()


class ProctoredExamTest(UniqueCourseTest):
    """
    Test courseware.
    """
    USERNAME = "STUDENT_TESTER"
    EMAIL = "student101@example.com"

    def setUp(self):
        super(ProctoredExamTest, self).setUp()

        self.courseware_page = CoursewarePage(self.browser, self.course_id)

        self.course_outline = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        # Install a course with sections/problems, tabs, updates, and handouts
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )
        course_fix.add_advanced_settings({
            "enable_proctored_exams": {"value": "true"}
        })

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section 1').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection 1').add_children(
                    XBlockFixtureDesc('problem', 'Test Problem 1')
                )
            )
        ).install()

        self.track_selection_page = TrackSelectionPage(self.browser, self.course_id)
        self.payment_and_verification_flow = PaymentAndVerificationFlow(self.browser, self.course_id)
        self.immediate_verification_page = PaymentAndVerificationFlow(
            self.browser, self.course_id, entry_point='verify-now'
        )
        self.upgrade_page = PaymentAndVerificationFlow(self.browser, self.course_id, entry_point='upgrade')
        self.fake_payment_page = FakePaymentPage(self.browser, self.course_id)
        self.dashboard_page = DashboardPage(self.browser)
        self.problem_page = ProblemPage(self.browser)

        # Add a verified mode to the course
        ModeCreationPage(
            self.browser, self.course_id, mode_slug=u'verified', mode_display_name=u'Verified Certificate',
            min_price=10, suggested_prices='10,20'
        ).visit()

        # Auto-auth register for the course.
        self._auto_auth(self.USERNAME, self.EMAIL, False)

    def _auto_auth(self, username, email, staff):
        """
        Logout and login with given credentials.
        """
        AutoAuthPage(self.browser, username=username, email=email,
                     course_id=self.course_id, staff=staff).visit()

    def _login_as_a_verified_user(self):
        """
        login as a verififed user
        """

        self._auto_auth(self.USERNAME, self.EMAIL, False)

        # the track selection page cannot be visited. see the other tests to see if any prereq is there.
        # Navigate to the track selection page
        self.track_selection_page.visit()

        # Enter the payment and verification flow by choosing to enroll as verified
        self.track_selection_page.enroll('verified')

        # Proceed to the fake payment page
        self.payment_and_verification_flow.proceed_to_payment()

        # Submit payment
        self.fake_payment_page.submit_payment()

    def test_can_create_proctored_exam_in_studio(self):
        """
        Test that Proctored exam settings are visible in Studio.
        """

        # Given that I am a staff member
        LogoutPage(self.browser).visit()
        self._auto_auth("STAFF_TESTER", "staff101@example.com", True)

        # When I visit the course outline page in studio.
        self.course_outline.visit()

        # And open the subsection edit dialog
        self.course_outline.open_exam_settings_dialog()

        # Then I can view all settings related to Proctored and timed exams
        self.assertTrue(self.course_outline.proctoring_items_are_displayed())

    def test_proctored_exam_flow(self):
        """
        Test that staff can create a proctored exam.
        """

        # Given that I am a staff member on the exam settings section
        LogoutPage(self.browser).visit()
        self._auto_auth("STAFF_TESTER", "staff101@example.com", True)
        self.course_outline.visit()
        self.course_outline.open_exam_settings_dialog()

        # When I Make the exam proctored.
        self.course_outline.make_exam_proctored()

        # And I login as a verified student.
        LogoutPage(self.browser).visit()
        self._login_as_a_verified_user()

        # And visit the courseware as a verified student.
        self.courseware_page.visit()

        # Then I can see an option to take the exam as a proctored exam.
        self.assertTrue(self.courseware_page.can_start_proctored_exam)

    def test_timed_exam_flow(self):
        """
        Test that staff can create a timed exam.
        """

        # Given that I am a staff member on the exam settings section
        LogoutPage(self.browser).visit()
        self._auto_auth("STAFF_TESTER", "staff101@example.com", True)
        self.course_outline.visit()
        self.course_outline.open_exam_settings_dialog()

        # When I Make the exam timed.
        self.course_outline.make_exam_timed()

        # And I login as a verified student.
        LogoutPage(self.browser).visit()
        self._login_as_a_verified_user()

        # And visit the courseware as a verified student.
        self.courseware_page.visit()

        # And I start the timed exam
        self.courseware_page.start_timed_exam()

        # Then I am taken to the exam with a timer bar showing
        self.assertTrue(self.courseware_page.is_timer_bar_present)


class CoursewareMultipleVerticalsTest(UniqueCourseTest):
    """
    Test courseware with multiple verticals
    """
    USERNAME = "STUDENT_TESTER"
    EMAIL = "student101@example.com"

    def setUp(self):
        super(CoursewareMultipleVerticalsTest, self).setUp()

        self.courseware_page = CoursewarePage(self.browser, self.course_id)

        self.course_outline = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        # Install a course with sections/problems, tabs, updates, and handouts
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section 1').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection 1').add_children(
                    XBlockFixtureDesc('problem', 'Test Problem 1', data='<problem>problem 1 dummy body</problem>'),
                    XBlockFixtureDesc('html', 'html 1', data="<html>html 1 dummy body</html>"),
                    XBlockFixtureDesc('problem', 'Test Problem 2', data="<problem>problem 2 dummy body</problem>"),
                    XBlockFixtureDesc('html', 'html 2', data="<html>html 2 dummy body</html>"),
                ),
                XBlockFixtureDesc('sequential', 'Test Subsection 2'),
            ),
        ).install()

        # Auto-auth register for the course.
        AutoAuthPage(self.browser, username=self.USERNAME, email=self.EMAIL,
                     course_id=self.course_id, staff=False).visit()
        self.courseware_page.visit()
        self.course_nav = CourseNavPage(self.browser)

    def test_tab_position(self):
        # test that using the position in the url direct to correct tab in courseware
        self.course_nav.go_to_section('Test Section 1', 'Test Subsection 1')
        subsection_url = self.courseware_page.get_active_subsection_url()
        url_part_list = subsection_url.split('/')
        self.assertEqual(len(url_part_list), 9)

        course_id = url_part_list[4]
        chapter_id = url_part_list[-3]
        subsection_id = url_part_list[-2]
        problem1_page = CoursewareSequentialTabPage(
            self.browser,
            course_id=course_id,
            chapter=chapter_id,
            subsection=subsection_id,
            position=1
        ).visit()
        self.assertIn('problem 1 dummy body', problem1_page.get_selected_tab_content())

        html1_page = CoursewareSequentialTabPage(
            self.browser,
            course_id=course_id,
            chapter=chapter_id,
            subsection=subsection_id,
            position=2
        ).visit()
        self.assertIn('html 1 dummy body', html1_page.get_selected_tab_content())

        problem2_page = CoursewareSequentialTabPage(
            self.browser,
            course_id=course_id,
            chapter=chapter_id,
            subsection=subsection_id,
            position=3
        ).visit()
        self.assertIn('problem 2 dummy body', problem2_page.get_selected_tab_content())

        html2_page = CoursewareSequentialTabPage(
            self.browser,
            course_id=course_id,
            chapter=chapter_id,
            subsection=subsection_id,
            position=4
        ).visit()
        self.assertIn('html 2 dummy body', html2_page.get_selected_tab_content())
