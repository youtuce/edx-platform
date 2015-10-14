"""Tests for the Studio entity plugin API."""
from django.test import TestCase

from openedx.core.lib.api.plugins import PluginError
from openedx.core.lib.studio_entities import StudioEntityPluginManager


class TestStudioEntityPluginApi(TestCase):
    """Unit tests for the Studio entity plugin API."""

    def test_get_plugin(self):
        """Verify that get_plugin works as expected."""
        entity = StudioEntityPluginManager.get_plugin('programs')
        self.assertEqual(entity.tab_text, 'Programs')

        with self.assertRaises(PluginError):
            StudioEntityPluginManager.get_plugin('invalid_entity')
