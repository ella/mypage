import datetime
import itertools
import logging
from copy import deepcopy

import anyjson as json

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django import template
import django.template.loader
from django.utils.safestring import mark_safe
from django.conf import settings

from mypage.pages.managers import PageManager, SessionPageManager
from mypage.pages.layout import Layout
from mypage.widgets.models import Widget
from mypage.widgets.models import get_object
from mypage.widgets.templatetags.splitobjectlist import split_list

DEFAULT_PAGE_TEMPLATES = (
    ('page.html', 'Default', 2),
    ('page3.html', 'Default 3', 3),
)

DEFAULT_SKIN_CHOICES = (('default', 'Default'),)

log = logging.getLogger('mypage.pages.models')

def page_template_choices():
    # TODO: do this function lazy to support multi-site process
    page_templates = getattr(settings, 'PAGE_TEMPLATES', DEFAULT_PAGE_TEMPLATES)
    page_template_choices = [ (val, name) for val, name, containers in page_templates ]
    return page_template_choices

def skin_choices():
    # TODO: migrate and remove
    return getattr(settings, 'SKIN_CHOICES', DEFAULT_SKIN_CHOICES)

class Page(models.Model):
    "Page containing multiple widgets."
    template = models.CharField(max_length=100, default='page.html', choices=page_template_choices())
    site = models.ForeignKey(Site, default=lambda: settings.SITE_ID)
    # TODO migrate to layout.template_config and remove
    skin = models.CharField(max_length=100, blank=True, default='', choices=skin_choices())
    layout_migrated = models.BooleanField(default=False)

    layout_json = models.TextField()

    objects = PageManager()

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __unicode__(self):
        return u'Page: %d' % self.pk

    @property
    def widgets(self):
        if not hasattr(self, '_widgets'):
            self._widgets = Widget.objects.filter(pk__in=map(lambda wil: wil.widget_id, self.layout.widgets))
        return self._widgets

    def update_template(self,  new_template):
        if new_template == self.template:
            return

        cs = None
        for val, name, containers in getattr(settings, 'PAGE_TEMPLATES', DEFAULT_PAGE_TEMPLATES):
            if val == new_template:
                cs = containers
                break
        else:
            raise KeyError('%r is not a valid choice for template' % new_template)

        self.layout.arrange_containers(cs)
        self.template = new_template

    def get_widgets(self):
        return [ i.get_child() for i in self.widgets.all() ]

    def layout_get(self):
        if not hasattr(self, '_layout'):
            self._layout = Layout(self, json.deserialize(self.layout_json))
        return self._layout
    def layout_set(self, value):
        self.layout_json = json.serialize(value)
    layout = property(layout_get, layout_set)

    def add_widget(self, widget, container=0, position=None):
        self.layout.insert_widget(widget, container=container, position=position)
        self.save()
        log.info('Add widget %d into page %d)', widget.pk, self.pk)

    def add_widgets(self, widgets):
        for w in widgets:
            self.add_widget(w)
        self.save()

    def remove_widget(self, widget):
        self.layout.remove_widget(widget)
        log.info('Remove widget %d from page %d)', widget.pk, self.pk)
        self.save()

    def remove_widgets(self, widgets):
        for w in widgets:
            self.remove_widget(w)
        self.save()


class UserPage(Page):
    "Page customized by/for one User"
    user = models.ForeignKey(User, db_index=True)
    objects = PageManager()
    site_copy = models.ForeignKey(Site, default=lambda: settings.SITE_ID)

    class Meta:
        unique_together = (('site_copy', 'user',),)
        verbose_name = _('User page')
        verbose_name_plural = _('User pages')


class SessionPage(Page):
    "Page customized by/for one AnonymousUser via a session"
    session_key = models.CharField(_('session key'), max_length=40, db_index=True)
    updated = models.DateTimeField(null=False, default=datetime.datetime.now)
    site_copy = models.ForeignKey(Site, default=lambda: settings.SITE_ID)

    objects = SessionPageManager()

    class Meta:
        unique_together = (('site_copy', 'session_key',),)
        verbose_name = _('Session page')
        verbose_name_plural = _('Session pages')

