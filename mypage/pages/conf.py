# -*- coding: utf-8 -*-

from django.conf import settings

from mypage.utils.settings import Settings

PAGE_THEMES = {'default': settings.DEFAULT_PAGE_ID}

PAGE_TEMPLATE_OPTIONS = {}

settings = Settings('mypage.pages.conf')
