import datetime

from django.db import models
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings
from django.core.cache import cache

SESSION_PAGE_EXPIRE_TIME = 4 * 7 * 24 * 60 * 60
PAGE_CACHE_TIMEOUT = 120

class PageManager(CurrentSiteManager):
    def get_for_id(self, id):
        key = 'page_for_id:%s' % id
        page = cache.get(key)
        if page:
            return page
        page = self.get(pk=id)
        page_cache_timeout = getattr(settings, 'PAGE_CACHE_TIMEOUT', PAGE_CACHE_TIMEOUT)
        cache.set(key, page, timeout=page_cache_timeout)
        return page

    def clone_from_page(self, page, defaults={}, **kwargs):
        """
        Returns cloned page
        """
        # clone and save page
        d = defaults.copy()
        d.update({
            'layout_json': page.layout_json,
            'site': page.site,
            'site_copy': page.site,
            'layout_migrated': page.layout_migrated,
        })
        new_page, created = self.get_or_create(defaults=d, **kwargs)
        if not created:
            return new_page
        new_page.layout = page.layout.clone()
        new_page.save()
        return new_page

class SessionPageManager(PageManager):

    def clean_old_pages(self):
        session_page_expire_time = datetime.timedelta(seconds=getattr(settings, 'SESSION_PAGE_EXPIRE_TIME', SESSION_PAGE_EXPIRE_TIME))
        self.filter(updated__lt=(datetime.datetime.now() - session_page_expire_time)).delete()

