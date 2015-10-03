""" Tests for API permissions classes. """
from django.test import TestCase, RequestFactory

from openedx.core.lib.api.permissions import IsStaffOrOwner
from student.tests.factories import UserFactory


class TestObject(object):
    """ Fake class for object permission tests. """
    user = None


class IsStaffOrOwnerTests(TestCase):
    """ Tests for IsStaffOrOwner permission class. """
    def setUp(self):
        super(IsStaffOrOwnerTests, self).setUp()
        self.permission = IsStaffOrOwner()
        self.request = RequestFactory().get('/')
        self.obj = TestObject()

    def assert_user_has_object_permission(self, user, permitted):
        """
        Asserts whether or not the user has permission to access an object.

        Arguments
            user (User)
            permitted (boolean)
        """
        self.request.user = user
        self.assertEqual(self.permission.has_object_permission(self.request, None, self.obj), permitted)

    def test_staff_user(self):
        """ Staff users should be permitted. """
        user = UserFactory.create(is_staff=True)
        self.assert_user_has_object_permission(user, True)

    def test_owner(self):
        """ Owners should be permitted. """
        user = UserFactory.create()
        self.obj.user = user
        self.assert_user_has_object_permission(user, True)

    def test_non_staff_test_non_owner_or_staff_user(self):
        """ Non-staff and non-owner users should not be permitted. """
        user = UserFactory.create()
        self.assert_user_has_object_permission(user, False)
