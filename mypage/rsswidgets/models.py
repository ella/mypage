from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

import anyjson as json
import feedparser

from mypage.widgets.models import Widget, WidgetFetchDataFailedException
from mypage.widgets.models import get_object
from mypage.rsswidgets.forms import RSSDisplayForm
from mypage.rsswidgets.conf import settings

class RSSWidget(Widget):
    feed_url = models.URLField()
    frequency_seconds = models.PositiveIntegerField(default=1800)


    CACHE_ENTRIES = 20

    @property
    def frequency(self):
        return timedelta(seconds=self.frequency_seconds)

    def _content_cache_timeout(self):
        return self.frequency_seconds
    content_cache_timeout = property(_content_cache_timeout)


    class Meta:
        verbose_name = _('RSS Widget')
        verbose_name_plural = _('RSS Widgets')

    def display_form(self, *args, **kwargs):
        return RSSDisplayForm(*args, **kwargs)

    def _fetch_data(self):
        try:
            d = feedparser.parse(self.feed_url)
        except Exception, e:
            raise WidgetFetchDataFailedException(e)
        if d.bozo is 1:
            raise WidgetFetchDataFailedException(d.bozo_exception)
        try:
            data = {
                'title': d.feed.title,
                'link': d.feed.link,
                'entries': d.entries[:self.CACHE_ENTRIES],
            }
        except AttributeError, e:
            raise WidgetFetchDataFailedException(e)
        return data

    def modify_data(self, data=None, config={}):
        item_count = config.get('item_count', settings.DEFAULT_ITEM_COUNT)
        data['entries'] = data['entries'][:int(item_count)]
        return data

class MultiRSSWidget(Widget):
    """
    widget that wraps multiple rss widgets

    relationship is given via self.config_json.rss-widgets structure

    rss-widget is a json object with 3-tuples
    (content-type, primary-key, feed-count,)
    TODO: add position value
    """

    content_cache_timeout = 60

    config_json = models.TextField()

    def config_get(self):
        return json.deserialize(self.config_json)
    def config_set(self, value):
        self.config_json = json.serialize(value)
    config = property(config_get, config_set)

    class Meta:
        verbose_name = _('Multi RSS Widget')
        verbose_name_plural = _('Multi RSS Widgets')

    def _fetch_data(self):
        return 'multi-rss-widget'

    def modify_data(self, data=None, config={}):
        rss_widgets = self.config.get('rss-widgets', [])
        items = []
        for ct, pk, count in rss_widgets:
            widget = get_object(ct, pk)
            items.extend(widget.get_data({'item_count': count,})['entries'])
        return self.add_categories(items)

    def add_categories(self, items):
        l = []
        for i in items:
            l.append({
                'item': i,
                'category': self.find_category(i),
            })
        return l

    def find_category(self, item):
        for urlstart, category in settings.CATEGORIES:
            if item.link.startswith(urlstart):
                return category
        return default

