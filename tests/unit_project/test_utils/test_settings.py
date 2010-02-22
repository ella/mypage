import sys
from unittest import TestCase

from django import conf

from mypage.utils.settings import Settings


class DummyModule(object):
    SAMPLE_CONFIG_OPTION = 'sample-config-value'


class TestSettings(TestCase):
    def setUp(self):
        dummy_module = DummyModule()
        sys.modules['tmp_tests_someapp_conf'] = dummy_module

        self.settings = Settings('tmp_tests_someapp_conf')

    def test_value_only_in_app_settings(self):
        self.failUnlessEqual(self.settings.SAMPLE_CONFIG_OPTION, 'sample-config-value')

    def test_value_overriden_via_django_conf_settings(self):
        self.failUnlessEqual(self.settings.SITE_ID, 1)

    def test_value_defined_nowhere(self):
        self.failUnlessRaises(AttributeError, lambda:self.settings.UNDEFINED_VALUE)

    def test_value_prefixed_constants(self):
        settings = Settings('tmp_tests_someapp_conf', prefix='SITE_')
        self.failUnlessEqual(settings.SAMPLE_CONFIG_OPTION, 'sample-config-value')
        self.failUnlessEqual(settings.ID, conf.settings.SITE_ID)
