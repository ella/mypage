from django.db import models
from django import forms
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote

import feedparser

from mypage.widgets.models import Widget, WidgetFetchDataFailedException, actionmethod

class YouTubeDispayForm(forms.Form):
    keyword = models.CharField(_('keyword'), max_length=100)

RSS_URL = 'http://gdata.youtube.com/feeds/api/videos?format=5&q='
CACHE_ENTRIES = 9

class YouTubeWidget(Widget):

    class Meta:
        verbose_name = _('YouTube Widget')
        verbose_name_plural = _('YouTube Widgets')

    def display_form(self, *args, **kwargs):
        return YouTubeDispayForm(*args, **kwargs)   

    def get_data(self, config, allow_fetch=True):
        keyword = config.get("keyword", None)
        if not keyword:
            # empty data != no data 
            return {'entries':[],}

        url = RSS_URL + urlquote(keyword)
        d = feedparser.parse( url )
        
        if d.bozo is 1:
            raise WidgetFetchDataFailedException(d.bozo_exception)
        data = {
            'title': d.feed.title,
            'link': d.feed.link,
            'entries': d.entries[:CACHE_ENTRIES],
            'keyword': keyword,
        }
        return data

    @actionmethod
    def search(self, request, wil):        
        keyword = request.GET.get('keyword', None) 
        wil.config.update({"keyword":keyword})
        return self.get_content(wil.config, RequestContext(request))

