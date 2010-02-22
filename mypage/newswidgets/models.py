import urllib
from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from mypage.widgets.models import Widget, WidgetFetchDataFailedException
from mypage.rsswidgets.models import RSSWidget

class NewsWidget(Widget):
    frequency = timedelta(hours=24)
    rsswidget = models.ForeignKey(RSSWidget, verbose_name=_('RSSWidget with feed source for perex'))

    class Meta:
        verbose_name = _('News Widget')
        verbose_name_plural = _('News Widgets')

    def _fetch_data(self):
        data = {
            'perex': self.rsswidget.get_data({
                    'item_count': 1,
            }),
            'categories': [],
        };
        for item in self.newssource_set.order_by('order'):
            item_count = item.item_count
            if item.rsswidget.pk == self.rsswidget.pk:
                item_count = item_count + 1
            feed = item.rsswidget.get_data({
                'item_count': item_count,
            });
            if item.rsswidget.pk == self.rsswidget.pk:
                feed['entries'] = feed['entries'][1:]
            data['categories'].append({
                'source': item,
                'feed': feed,
            })
        return data

    def modify_data(self, data=None, config={}):
        return data

class NewsSource(models.Model):
    widget = models.ForeignKey(NewsWidget)
    rsswidget = models.ForeignKey(RSSWidget, verbose_name=_('RSSWidget with feed source'))
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    url = models.URLField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(unique=True)
    item_count = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('News Source')
        verbose_name_plural = _('News Sources')

    def __unicode__(self):
        return self.name
