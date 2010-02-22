from django.contrib import admin

from mypage.newswidgets.models import NewsWidget, NewsSource

admin.site.register(NewsWidget)
admin.site.register(NewsSource)
