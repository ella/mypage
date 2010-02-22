# -*- coding: utf-8 -*-
from copy import deepcopy
from mock import patch

from djangosanetesting import UnitTestCase

from mypage.pages.models import Page
from mypage.pages.layout import Layout, WidgetInLayout
from mypage.widgets.models import Widget

stored_layout = {
    'static_containers': [[
        {
            'widget_ct_id': 1,
            'widget_id': 20,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        }
    ]],
    'containers': [[
        {
            'widget_ct_id': 1,
            'widget_id': 1,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        },
        {
            'widget_ct_id': 1,
            'widget_id': 2,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        },
    ],[
        {
            'widget_ct_id': 1,
            'widget_id': 11,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        },
    ]],
}


class TestLayout(UnitTestCase):

    def setUp(self):
        super(TestLayout, self).setUp()
        self.page = Page(pk=1)
        self.layout = Layout(self.page, deepcopy(stored_layout))

    def test_get_static_widgets(self):
        self.assert_equals(
            [{'state': 2, 'config': {}, 'widget_id': 20, 'widget_ct_id': 1}],
            self.layout.static_widgets)

    def test_get_dynamic_widgets(self):
        self.assert_equals(
            [1, 2, 11],
            map(lambda x: x['widget_id'], self.layout.dynamic_widgets))

    def test_get_widgets(self):
        self.assert_equals(
            [1, 2, 11, 20],
            map(lambda x: x['widget_id'], self.layout.widgets))

    def test_get_widget(self):
        self.assert_equals(
            {'state': 2, 'config': {}, 'widget_id': 2, 'widget_ct_id': 1},
            self.layout.get_widget(1, 2))

    def test_get_widget_not_found(self):
        self.assert_raises(
            Layout.WidgetInLayoutDoesNotExist,
            self.layout.get_widget, 1000, 1000)

    def test_get_widget_reference(self):
        config = {'a':1}
        wil = self.layout.get_widget(1, 2)
        wil.config = config
        self.assert_equals(
            config,
            self.layout.get_widget(1, 2).config)
        self.assert_equals(
            config,
            self.layout['containers'][0][1].config)
        self.assert_true(self.layout.changed)
