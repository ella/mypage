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
            {
                'widget_ct_id': 1,
                'widget_id': 12,
                'config': {},
                'state': WidgetInLayout.STATE_NEW,
            },
        ]]
}


class TestInsertRemoveWidget(UnitTestCase):

    def setUp(self):
        super(TestInsertRemoveWidget, self).setUp()
        self.page = Page(pk=1)
        self.layout = Layout(self.page, deepcopy(stored_layout))
        self.widget = Widget(content_type_id=1, pk=100)

    def test_insert_widget_defaults(self):
        self.layout.insert_widget(self.widget)
        self.assert_equals(
                self.layout['containers'][0][2],
                {'state': WidgetInLayout.STATE_NEW, 'config': {}, 'widget_id': 100, 'widget_ct_id': 1})

    def test_insert_widget_with_config(self):
        self.layout.insert_widget(self.widget, config={'x':'y'}, state=WidgetInLayout.STATE_NORMAL)
        self.assert_equals(
                self.layout['containers'][0][2],
                {'state': WidgetInLayout.STATE_NORMAL, 'config': {'x':'y'}, 'widget_id': 100, 'widget_ct_id': 1})

    def test_insert_widget_to_specified_container(self):
        self.layout.insert_widget(self.widget, container=1)
        self.assert_equals(
                self.layout['containers'][1][2],
                {'state': 2, 'config': {}, 'widget_id': 100, 'widget_ct_id': 1})

    def test_insert_widget_to_specified_container_out_of_range(self):
        self.assert_raises(
            IndexError,
            self.layout.insert_widget, self.widget, container=2)

    def test_insert_widget_to_specified_position(self):
        self.layout.insert_widget(self.widget, position=0)
        self.assert_equals(
                self.layout['containers'][0][0],
                {'state': 2, 'config': {}, 'widget_id': 100, 'widget_ct_id': 1})
        self.assert_equals(
                self.layout['containers'][0][1],
                {'state': 2, 'config': {}, 'widget_id': 1, 'widget_ct_id': 1})

    def test_insert_widget_to_specified_position_out_of_range(self):
        self.layout.insert_widget(self.widget, position=100)
        self.assert_equals(
                self.layout['containers'][0][2],
                {'state': 2, 'config': {}, 'widget_id': 100, 'widget_ct_id': 1})

    def test_insert_allready_assigned_widget(self):
        self.layout.insert_widget(Widget(content_type_id=1, pk=1))
        self.assert_equals(
                len(self.layout.widgets), 5)
