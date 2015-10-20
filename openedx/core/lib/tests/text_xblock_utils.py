"""
Tests for xblock_utils.py
"""
import ddt
from uuid import UUID
from unittest import TestCase
from xblock.fragment import Fragment
from django.test.client import RequestFactory

from openedx.core.lib.xblock_utils import (
    wrap_fragment,
    request_token
)

# alphabetize the imports
# docstring all the classes and methods


class TestXblockUtils(TestCase):

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
        test_uuid = UUID(token, version=1)
        self.assertEqual(token, test_uuid.hex)



