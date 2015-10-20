"""
Tests for xblock_utils.py
"""
import ddt
import uuid
from unittest import TestCase
from xblock.fragment import Fragment
from django.test.client import RequestFactory
from xblock.core import XBlock
from xmodule.x_module import XModule, XModuleDescriptor
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory, LibraryFactory
from lms.djangoapps.lms_xblock.runtime import quote_slashes
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.models import StudentModule


from openedx.core.lib.xblock_utils import (
    wrap_fragment,
    request_token,
    wrap_xblock,
    replace_jump_to_id_urls,
    replace_course_urls,
    grade_histogram
)

# TODO
# alphabetize the imports
# docstring all the classes and methods


class TestXblockUtils(ModuleStoreTestCase):

    def test_wrap_fragment(self):
        new_content = u'<p>New Content<p>'
        fragment = Fragment()
        fragment.add_css(u'body {background-color:red;}')
        fragment.add_javascript(u'alert("Hi!");')
        wrapped_fragment = wrap_fragment(fragment, new_content)
        self.assertEqual(u'<p>New Content<p>', wrapped_fragment.content)
        self.assertEqual(u'body {background-color:red;}', wrapped_fragment.resources[0].data)
        self.assertEqual(u'alert("Hi!");', wrapped_fragment.resources[1].data)

    def test_request_token(self):
        request_with_token = RequestFactory().get('/')
        request_with_token._xblock_token = '123'
        token = request_token(request_with_token)
        self.assertEqual(token, '123')

        request_without_token = RequestFactory().get('/')
        token = request_token(request_without_token)
        # Test to see if the token is an uuid1 hex value
        test_uuid = uuid.UUID(token, version=1)
        self.assertEqual(token, test_uuid.hex)

    def test_wrap_xblock(self):
        fragment = Fragment(u"<h1>Test!</h1>")
        fragment.add_css(u'body {background-color:red;}')
        fragment.add_javascript('alert("Test!");')

        test_course = CourseFactory.create(
            org='TestX',
            number='TS01',
            run='2015'
        )

        test_wrap_output = wrap_xblock(
            runtime_class='TestRuntime',
            block=test_course,
            view='studio_view',
            frag=fragment,
            context=None,
            usage_id_serializer=lambda usage_id: quote_slashes(unicode(usage_id)),
            request_token=uuid.uuid1().get_hex()
        )
        self.assertIsInstance(test_wrap_output, Fragment)
        self.assertIn('xblock-studio_view', test_wrap_output.content)
        self.assertIn('data-runtime-class="TestRuntime"', test_wrap_output.content)
        self.assertIn('data-usage-id="i4x:;_;_TestX;_TS01;_course;_2015"', test_wrap_output.content)
        self.assertIn('<h1>Test!</h1>', test_wrap_output.content)
        self.assertEqual(test_wrap_output.resources[0].data, u'body {background-color:red;}')
        self.assertEqual(test_wrap_output.resources[1].data, 'alert("Test!");')

    def test_replace_jump_to_id_urls(self):
        test_replace = replace_jump_to_id_urls(
            course_id=SlashSeparatedCourseKey('TestX', 'TS01', '2015'), 
            jump_to_id_base_url=u'/base_url/',
            block=CourseFactory.create(),
            view='studio_view',
            frag=Fragment(u'<a href="/jump_to_id/id">'),
            context=None
        )
        self.assertIsInstance(test_replace, Fragment)
        self.assertEqual(test_replace.content, u'<a href="/base_url/id">')

    def test_replace_course_urls(self):
        test_course = SlashSeparatedCourseKey('TestX', 'TS01', '2015')
        test_replace = replace_course_urls(
            course_id=test_course, 
            block=CourseFactory.create(),
            view='studio_view',
            frag=Fragment(u'<a href="/course/id">'),
            context=None
        )
        self.assertIsInstance(test_replace, Fragment)
        self.assertEqual(test_replace.content, u'<a href="/courses/TestX/TS01/2015/id">')

    def test_grade_histogram(self):
        new_grade = StudentModule.objects.create(
            student_id=1,
            grade=100,
            module_state_key='i4x://foo/bar/baz/some_module'
        )

        #grades = grade_histogram(u'i4x://foo/bar/baz/some_module')

