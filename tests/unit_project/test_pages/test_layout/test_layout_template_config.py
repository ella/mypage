# -*- coding: utf-8 -*-
from copy import deepcopy
#from mock import patch

from django.core.exceptions import ImproperlyConfigured

from djangosanetesting import UnitTestCase

from mypage.pages.models import Page
from mypage.pages.layout import Layout
#from mypage.widgets.models import Widget

from mypage.pages.layout import TemplateConfig
from mypage.pages.conf import settings

stored_layout = {
    'static_containers': [], 
    'containers': [],
}

stored_templpate_config = {
    'some_option': 1,
    'other_option': 2,
}

class TestLayoutTemplpateConfig(UnitTestCase):

    def setUp(self):
        super(TestLayoutTemplpateConfig, self).setUp()
        self.options_orig = TemplateConfig.options
        TemplateConfig.options = {'some_option': ((1, 2, 3), 1)}
        self.page = Page(pk=1)
        #self.layout = Layout(self.page, deepcopy(stored_layout))

    def tearDown(self):
        super(TestLayoutTemplpateConfig, self).tearDown()
        TemplateConfig.options = self.options_orig

    def test_template_config_empty_default_option_loading(self):
        layout = Layout(self.page, deepcopy(stored_layout))
        template_config = TemplateConfig(layout)
        self.assert_equals(1, template_config['some_option'])

    def test_template_config_unknown_option(self):
        layout = Layout(self.page, deepcopy(stored_layout))
        template_config = TemplateConfig(layout)
        self.assert_raises(
                ImproperlyConfigured, 
                template_config.__getitem__, 'unknown_option')

    def test_template_config_on_layout(self):
        l = deepcopy(stored_layout)
        l.update(dict(template_config=stored_templpate_config))
        layout = Layout(self.page, l)
        self.assert_equals(2, layout.template_config['other_option'])

    def test_template_config_as_hash(self):
        l = deepcopy(stored_layout)
        l.update(dict(template_config=stored_templpate_config))
        layout = Layout(self.page, l)
        self.assert_equals('1deb7217a43e5ad475a76b4158f1c472', layout.template_config.as_hash())
