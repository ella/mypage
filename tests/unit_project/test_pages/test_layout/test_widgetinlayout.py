# -*- coding: utf-8 -*-
from mock import patch
from copy import deepcopy

from djangosanetesting import UnitTestCase

from django.utils.safestring import SafeString

from mypage.widgets.models import Widget
from mypage.pages.models import Page
from mypage.pages.layout import Layout, WidgetInLayout

from unit_project import template_loader

stored_layout = {
    'static_containers': [[]],
    'containers': [[
    {
        'widget_ct_id': 1,
        'widget_id': 1,
        'config': {},
        'state': WidgetInLayout.STATE_NEW,
    }]]
}

def get_dummy_widget(instance=None):
    return Widget(content_type_id=1, pk=1)

def rendered_widget_dummy_render(instance, *args, **kwargs):
    return 'spam'

class TestWidgetInLayout(UnitTestCase):

    def setUp(self):
        super(TestWidgetInLayout, self).setUp()
        self.layout = Layout(Page(pk=1), deepcopy(stored_layout))

    def test_update(self):
        wil = self.layout['containers'][0][0]
        wil.config = {'a':2}
        self.assert_equals(wil.config, {'a':2})
        self.assert_equals(self.layout['containers'][0][0]['config'], {'a':2})
        self.assert_true(self.layout.changed) # layout must be flagged as changed

    @patch('mypage.widgets.models.RenderedWidget.render', rendered_widget_dummy_render)
    @patch('mypage.pages.layout.WidgetInLayout.widget', property(get_dummy_widget))
    def test_render(self):
        wil = self.layout['containers'][0][0]
        rendered_widget = wil.render(context={})
        self.assert_equals(rendered_widget, 'spam')
        self.assert_true(isinstance(rendered_widget, SafeString))

    @patch('mypage.widgets.models.RenderedWidget.render', rendered_widget_dummy_render)
    @patch('mypage.pages.layout.WidgetInLayout.widget', property(get_dummy_widget))
    def test_render_reset_state(self):
        wil = self.layout['containers'][0][0]
        self.assert_false(self.layout.changed)
        rendered_widget = wil.render(context={})
        self.assert_equals(self.layout['containers'][0][0]['state'], WidgetInLayout.STATE_NORMAL)
        self.assert_true(self.layout.changed)

    def test_factory(self):
        self.assert_equals(
                WidgetInLayout.factory(self.layout['containers'][0], get_dummy_widget()),
                {'state': 2, 'config': {}, 'widget_id': 1, 'widget_ct_id': 1})
