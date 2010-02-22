from urlparse import urlparse
from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from mypage.rsswidgets.models import RSSWidget
from mypage.magazineswidgets.forms import MagazinesDisplayForm, DEFAULT_ITEM_COUNT
from mypage.tvprogramwidgets.models import remove_diacritics

class MagazinesWidget(RSSWidget):
    frequency = timedelta(seconds=4*60)

    class Meta:
        verbose_name = _('Magazines Widget')
        verbose_name_plural = _('Magazines Widgets')

    def display_form(self, *args, **kwargs):
        return MagazinesDisplayForm(*args, **kwargs)

    def modify_data(self, data=None, config={}):
        data = super(MagazinesWidget, self).modify_data(data, config)
        for item in data['entries']:
            item['domain'] = urlparse(item['link'])[1]
            item['tag'] = item['domain'].replace('.', '_')
            try:
                domains = MagazinesDomain.objects.get(domain=item['domain'])
                item['alt'] = domains.name
            except MagazinesDomain.DoesNotExist, e:
                pass
        return super(MagazinesWidget, self).modify_data(data, config)

class MagazinesDomain(models.Model):
    domain = models.CharField(_('Domain'), max_length=100)
    name = models.CharField(_('Name'), max_length=100)
