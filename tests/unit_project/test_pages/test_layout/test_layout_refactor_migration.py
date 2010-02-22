# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from mypage.pages.models import Page
from mypage.pages.layout import Layout, WidgetInLayout
from mypage.widgets.models import Widget
from mypage.pages import migrations
import anyjson as json

#_migmodule = __import__('.'.join((migrations.__name__, '0012_layout_refactor')), {}, {}, ['create_wil', 'migrate_container', 'migrate_layout'])
#create_wil = _migmodule.create_wil
#migrate_container = _migmodule.migrate_container
#migrate_layout = _migmodule.migrate_layout
from mypage.pages.migrations.utils.layout_refactor_migration import create_wil, migrate_container, migrate_layout, MockedWidgetInPage


configs = {
    1: {},
    2: {'x': 1, 'y': 2}
}


def wil(widget_ct_id, widget_id, config=None, state=WidgetInLayout.STATE_NORMAL):
    try:
        config = config or configs[widget_id]
    except KeyError, e:
        config = {}
    return dict(widget_ct_id=widget_ct_id, widget_id=widget_id, config=config, state=state)


class TestLayoutRefactorMigration(UnitTestCase):

    def setUp(self):
        self.page = Page(pk=1)
        self.widgets = [Widget(content_type_id=1, pk=i) for i in range(1, 3)]
        wips = [MockedWidgetInPage(self.page, w.pk, json.serialize(configs[w.pk]), state=WidgetInLayout.STATE_NORMAL) for w in self.widgets]
        self.wips = dict((wip.widget_id, wip) for wip in wips)
        return super(TestLayoutRefactorMigration, self).setUp()

    def test_create_wil_success(self):
        pair = [u"1", u"2"]
        self.assert_equals(
                create_wil(pair, self.wips), 
                wil(1, 2))

    def test_create_wil_succes_wip_does_not_exist_defaults_will_be_used(self):
        pair = [u"1", u"100"]
        self.assert_equals(
                create_wil(pair, self.wips),
                wil(1, 100))

    def test_migrate_container_success(self):
        container = [[u"1", u"1"], [u"1", u"2"], [u"1", u"100"]]
        self.assert_equals(
                migrate_container(container, self.wips),
                [wil(1, 1), wil(1, 2), wil(1, 100)])

    def test_migrate_layout_success(self):
        layout = dict(timestamp = 1,
                containers = [[[u"1", u"1"], [u"1", u"100"]], [[u"1", u"200"]]],
                static_containers = [[[u"1", u"2"]]])
        migrated_layout = migrate_layout(layout, self.wips)
        self.assert_equals(
                migrated_layout['static_containers'],
                [[wil(1, 2)]])

