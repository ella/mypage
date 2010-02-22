# -*- coding: utf-8 -*-
from copy import deepcopy
from mock import patch

from djangosanetesting import UnitTestCase

from mypage.pages.models import Page
from mypage.pages.layout import Layout, WidgetInLayout

stored_layout = {
    'static_containers': [[
        {
            'widget_ct_id': 1,
            'widget_id': 1,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        }
    ]],
    'containers': [[
        {
            'widget_ct_id': 1,
            'widget_id': 2,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        },
        {
            'widget_ct_id': 1,
            'widget_id': 3,
            'config': {},
            'state': WidgetInLayout.STATE_NEW,
        },
    ]]
}

def dummy_render(instance, context={}, allow_fetch=False, tab=None):
    return '%d:%d:%s' % (instance.widget_ct_id, instance.widget_id, tab)

class TestLayoutRendering(UnitTestCase):

    def setUp(self):
        super(TestLayoutRendering, self).setUp()
        self.page = Page(pk=1)
        self.layout = deepcopy(stored_layout)

    @patch('mypage.pages.layout.WidgetInLayout.render', dummy_render)
    def test_render(self):
        layout = Layout(self.page, self.layout)
        self.assert_equals(
                layout.render(context={}), 
                {'static_containers': [['1:1:None']], 'containers': [['1:2:None', '1:3:None']]})

    @patch('mypage.pages.layout.WidgetInLayout.render', dummy_render)
    def test_render_with_settab(self):
        layout = Layout(self.page, self.layout)
        self.assert_equals(
                layout.render(context={}, settab=dict(widget_ct_id=1, widget_id=2, tab='sometab')),
                {'static_containers': [['1:1:None']], 'containers': [['1:2:sometab', '1:3:None']]})
