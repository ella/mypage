# -*- coding: utf-8 -*-

from copy import deepcopy
from itertools import chain
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


def keys_only(containers):
    """
    Transform WILs to keys (ct_id, pk pars)
    """
    return [map(lambda x: [x.widget_ct_id, x.widget_id], wils) for wils in containers]

def mocked_get_object(widget_ct_id, widget_id):
    return Widget(content_type_id=widget_ct_id, pk=widget_id)

class TestArrangeWidgets(UnitTestCase):

    def setUp(self):
        super(TestArrangeWidgets, self).setUp()
        self.page = Page(pk=1)
        self.layout = Layout(self.page, deepcopy(stored_layout))

    def test_check_containers(self):
        # TODO move me to my place :)
        from mypage.pages.views import check_containers
        containers_strs = [[[u"1", u"1"], [u"2", u"2"]], [[u"3", u"3"]]]
        containers_ints = [[[1, 1], [2, 2]], [[3, 3]]]
        self.assert_equals(
                check_containers(containers_strs),
                containers_ints)

    def test_arrange_widgets_success(self):
        sent_containers = [[[1, 2], [1, 1]], [[1, 11], [1, 12]]]
        self.layout.arrange_widgets(sent_containers)
        self.assert_equals(
                keys_only(self.layout.containers),
                sent_containers)

    @patch('mypage.pages.layout.get_object', mocked_get_object)
    def test_arrange_widgets_and_place_new_one_success(self):
        widget = Widget(content_type_id=1, pk=100)
        sent_containers = [[[1, 100], [1, 2], [1, 1]], [[1, 11], [1, 12]]]
        self.layout.arrange_widgets(sent_containers)
        self.assert_equals(
                keys_only(self.layout.containers),
                sent_containers)

    def test_arrange_widgets_and_remove_one_success(self):
        sent_containers = [[[1, 2], [1, 1]], [[1, 11]]]
        self.layout.arrange_widgets(sent_containers)
        self.assert_equals(
                keys_only(self.layout.containers),
                sent_containers)

