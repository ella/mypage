from copy import deepcopy
import anyjson as json
import logging
import time

from django.db import connection, transaction
from django.db.models.query import QuerySet

from mypage.pages.models import Page
from mypage.pages.layout import WidgetInLayout

log = logging.getLogger('mypage.pages.migrations')

get_page_wips_query = '''SELECT
    `pages_widgetinpage`.`widget_id`,
    `pages_widgetinpage`.`config_json`,
    `pages_widgetinpage`.`state`
    FROM `pages_widgetinpage` WHERE `pages_widgetinpage`.`page_id` = %s'''

class MockedWidgetInPage(object):
    """
    Emulates old WidgetInPage model
    """
    def __init__(self, page, widget_id, config_json, state):
        self.page = page
        self.widget_id = widget_id
        self.state = state
        self.config_json = config_json
        self.config = self.get_config(self.config_json)
    def get_config(self, config_json):
        if not config_json:
            return {}
        try:
            return json.deserialize(config_json)
        except Exception, e:
            log.warn('Broken config! %s, %s', config_json, e)
            return {}

def get_wips(page):
    """
    Return mocked wips for given page

    {14L: <MockedWidgetInPage: Widget: 14 in Page: 1>,
     18L: <MockedWidgetInPage: Widget: 18 in Page: 1>,
     ...
    """
    cursor = connection.cursor()
    cursor.execute(get_page_wips_query, (page.pk,))
    return dict((wip.widget_id, wip) for wip in [MockedWidgetInPage(page, *row) for row in cursor.fetchall()])

def create_wil(pair, wips):
    """
    Migrates widget ids pair (ints allready!) to WidgetInLayout dict like object with config and state

    If WIP does not exist, default config and states will be used

    It makes something like this:
    ["<str ct_id>", "<str id>"] + wip.config, wip.state
    =>
    {
        'widget_ct_id': <int ct_id>,
        'widget_id': <int id>,
        'config': <dict config>,
        'state': <state>,
    }
    """
    w_ct_id, w_pk = map(lambda x: int(x), pair)
    try:
        wip = wips[w_pk]
        config = wip.config
        state = wip.state
    except KeyError, e:
        config = {}
        state = WidgetInLayout.STATE_NORMAL
    return dict(
            widget_ct_id = w_ct_id,
            widget_id = w_pk,
            config = config,
            state = state)

def migrate_container(container, wips):
    """
    Migrates each pair in given container
    """
    return [create_wil(pair, wips) for pair in container]

def migrate_layout(layout, wips):
    """
    Migrates layout containers to a new structure with wils (widget in layout :)
    """
    migrated_layout = deepcopy(layout)
    migrated_layout['static_containers'] = [migrate_container(c, wips) for c in layout['static_containers']]
    migrated_layout['containers'] = [migrate_container(c, wips) for c in layout['containers']]
    return migrated_layout

def migrate_page(page):
    old_layout = json.deserialize(page.layout_json)
    layout = migrate_layout(old_layout, get_wips(page))
    qs = Page.objects.filter(pk=page.pk, layout_migrated=False) # do not save allready migrated page
    qs.update(layout_json=json.serialize(layout), layout_migrated=True)
    log.info('Page %d layout migrated.', page.pk)
    page.layout = layout
    page.layout_migrated = True
    return page

def migrate(limit=None, loop_sleep=0):
    #qs = Page.objects.filter(layout_migrated=False).only('id', 'layout_json')
    qs = QuerySet(Page).filter(layout_migrated=False).only('id', 'layout_json')
    if limit:
        qs = qs[:limit]
    for page in qs.iterator():
        migrate_page(page)
        time.sleep(loop_sleep)
