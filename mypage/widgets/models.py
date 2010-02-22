from string import Template
from datetime import datetime, timedelta

from django.utils.hashcompat import md5_constructor
from django.db import models, connection, transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.conf import settings
from django.template import loader, RequestContext
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.handlers.wsgi import WSGIRequest

from mypage.widgets.forms import BaseDisplayForm
from mypage.widgets.fields import ContentTypeField
from mypage.widgets.storage import storage


# default reneal frequency - one hour
DEFAULT_WIDGET_FREQUENCY = 60 * 60
# cache widget timeout
WIDGET_TIMEOUT = 60 * 60
# cache content timeout
WIDGET_CONTENT_TIMEOUT = 60 * 60

DATA_CACHE_PREFIX = 'd'
WIDGET_CACHE_PREFIX = 'w'
CONTENT_CACHE_PREFIX = 'c'

EMPTY_CONTENT = ''


def get_cache_key(prefix, widget=None, content_type_id=None, object_id=None):
    assert widget or (content_type_id and object_id), ''

    if widget:
        return '%s:%s:%s' % (prefix, widget.content_type_id, widget.pk)
    else:
        return '%s:%s:%s' % (prefix, content_type_id, object_id)

def get_data_cache_key(widget=None, content_type_id=None, object_id=None):
    return get_cache_key(DATA_CACHE_PREFIX, widget, content_type_id, object_id)
def get_widget_cache_key(widget=None, content_type_id=None, object_id=None):
    return get_cache_key(WIDGET_CACHE_PREFIX, widget, content_type_id, object_id)

def get_content_cache_key(widget=None, content_type_id=None, object_id=None, config={}, tab=None):
    begin = get_cache_key(CONTENT_CACHE_PREFIX, widget, content_type_id, object_id)
    sorted_config = [ (k, config[k]) for k in sorted(config.keys()) ]

    key = '%s:%s:%s:%s' % (begin, sorted_config, tab, settings.SITE_ID)

    return md5_constructor(key).hexdigest()


def get_object(content_type_id, object_id):
    cache_key = get_widget_cache_key(content_type_id=content_type_id, object_id=object_id)
    obj = cache.get(cache_key)
    if obj is None:
        ct = ContentType.objects.get_for_id(int(content_type_id))
        obj = ct.get_object_for_this_type(pk=object_id)
        cache.set(cache_key, obj, timeout=getattr(settings, 'WIDGET_TIMEOUT', WIDGET_TIMEOUT))
    return obj

def actionmethod(method):
    """
    Simple decorator for flagging widget method as an action method callable by acton_dispatcher
    """
    method.action_method = True
    return method


def clone_model(model):
    """
    Create a copy of a model instance

    Works in model inheritance case. M2M relationships are currently not handled,
    i.e. they are not copied.

    Inspired by Copy a Model Instance snippet from djangosnippets.org by miracle2k
    http://www.djangosnippets.org/snippets/1040/
    """
    initial = dict([(f.name, getattr(model, f.name))
        for f in model._meta.fields
        if not isinstance(f, models.AutoField) and\
            not f in model._meta.parents.values()])
    obj = model.__class__(**initial)
    obj.save()
    return obj

class RenderedWidget(object):

    CACHE_TIMEOUT = 60 * 60
    
    def __init__(self, widget, state):
        self.widget = widget
        self.state = state

    @property
    def cache_key(self):
        return 'renderedwidget:%d:%d:%d:%d' % (
                settings.SITE_ID,
                self.widget.content_type_id, 
                self.widget.pk, 
                self.state)

    def _render_html(self, context):
        context.push()
        context['widget'] = self.widget
        context['state'] = self.state
        out = loader.render_to_string(self.widget.get_template(self.widget.TEMPLATE), context)
        context.pop()
        return out

    def rendered_html(self, context):
        out = cache.get(self.cache_key)
        if not out:
            out = self._render_html(context)
            cache.set(self.cache_key, out, self.CACHE_TIMEOUT)
        return out


    def render(self, config, context, allow_fetch=False, tab=None):
        try:
            subst = {'content': self.widget.get_content(config, context, allow_fetch, tab=tab)}
        except WidgetFetchDataFailedException, e:
            subst = {'content': loader.render_to_string('widgets.widget/content500.html')}
        return Template(self.rendered_html(context)).safe_substitute(subst)

class Widget(models.Model):
    rendered_widget_class = RenderedWidget

    frequency = timedelta(seconds=getattr(settings, 'DEFAULT_WIDGET_FREQUENCY', DEFAULT_WIDGET_FREQUENCY))

    DISPLAY_FORM_TEMPLATE = 'display_form.html'
    CONTENT_TEMPLATE = 'content.html'
    TEMPLATE = 'widget.html'

    content_type = ContentTypeField(editable=False, help_text="Type of the widget, the most-specific subclass")

    title = models.CharField(_('Title'), max_length=100)
    slug = models.SlugField(max_length=100)

    last_downloaded = models.DateTimeField(null=True, blank=True)
    next_download = models.DateTimeField(default=datetime.now)

    url = models.URLField(_('Header link URL'), blank=True)

    class Meta:
        verbose_name = _('Widget')
        verbose_name_plural = _('Widgets')

    def __unicode__(self):
        return self.title

    def display_form(self, *args, **kwargs):
        """
        Form used for configuration teh widget's appearance, it's cleaned_data is then
        stored in WidgetInPage.config and passed to rendering phase as config json.
        """
        return BaseDisplayForm(*args, **kwargs)

    def _content_cache_timeout(self):
        return getattr(settings, 'WIDGET_CONTENT_TIMEOUT', WIDGET_CONTENT_TIMEOUT)
    content_cache_timeout = property(_content_cache_timeout)

    def get_content(self, config, context, allow_fetch=False, tab=None):
        key = get_content_cache_key(widget=self, config=config, tab=tab)
        content = cache.get(key)
        if content:
            return content

        data = self.get_data(config, allow_fetch)
        if not data:
            return EMPTY_CONTENT

        context.update({
            'widget': self,
            'config': config,
            'tab': tab,
            'data': data,
        })

        template = self.get_template(self.CONTENT_TEMPLATE)
        content = loader.render_to_string(template, context)
        if content:
            cache.set(key, content, timeout=self.content_cache_timeout)
        return content

    def config_form(self, *args, **kwargs):
        return BaseConfigForm(*args, **kwargs)

    def save(self, force_update=False, force_insert=False):
        "update the info on who I am"
        self.content_type = ContentType.objects.get_for_model(self)
        super(Widget, self).save(force_update=force_update, force_insert=force_insert)
        # drop the data from cache when widget is updated
        storage.delete(get_data_cache_key(self))
        cache.delete(get_widget_cache_key(self))

    def get_child(self):
        ret = self
        ct = ContentType.objects.get_for_model(self)
        if ct.pk != self.content_type_id:
            ret = get_object(self.content_type_id, self.pk)
        return ret

    class ActionMethodDoesNotExists(Exception):
        pass

    def action_dispatcher(self, request, wil, to_call):
        """
        Calls action method found by to_call param

        Action methods are accsesible by dispatcher when decorated/flagged as action methods

        Example:

        @actionmethod
        def my_action(self, request, wil):
            '''
            It can also update wil.config (POST only). Action method is usaly called
            by widget_action view and page there wil be automaticly saved if wil is saved here
            '''
            wil.config.update(dict(spam=request.POST.get('spam', 1)))
            wil.save()
            return http.HttpResponseRedirect(reverse('home_page'))
        """
        try:
            method = getattr(self, to_call)
            if method.action_method == True:
                return method(request, wil)
        except AttributeError, e:
            raise self.ActionMethodDoesNotExists()

    def _fetch_data(self):
        '''
        the real fetch function, it is supposed to be overriden in siblings

         * return some valid data if you want get_content work
         * return None if widget.html is the only thing you need
        '''
        # hack for loading dynamic content of simple Widgets TODO: move to different type of widget
        return 'widget'

    def update_next_download(self):
        """
        Update next_download time in the database, set it to now + self.frequency
        """
        now = datetime.now()
        self.next_download = now + self.frequency
        self.last_downloaded = now
        Widget.objects.filter(pk=self.pk).update(last_downloaded=self.last_downloaded, next_download=self.next_download)

    #@transaction.commit_on_success
    def fetch_data(self):
        '''Fetch the widget's data and store it in cache'''
        data = self._fetch_data()
        cache_key = get_data_cache_key(self)

        # set cache timeout to widget's download frequency
        timeout = self.frequency.days*86400 +  self.frequency.seconds
        # double it to be sure
        timeout *= 2

        storage.set(cache_key, data, timeout=timeout)
        self.update_next_download()
        return data

    def modify_data(self, data=None, config={}):
        """
        Override this method to add data modification functionality.
        Data could be modified using config values.
        """
        return data

    def get_data(self, config, allow_fetch=True):
        """
        Returns loaded (+ modified) data from storage backend.

        If there are no data and allow_fetch are True data will be fetched,
        otherwise returns None.
        """
        cache_key = get_data_cache_key(widget=self)
        data = storage.get(cache_key)
        if data is None and allow_fetch:
            data = self.fetch_data()
        if data is not None:
            return self.modify_data(data, config)


    def get_template(self, template_type):
        return [
                '%s.%s/%s/%s' % (self.content_type.app_label, self.content_type.model, self.slug, template_type),
                '%s.%s/%s' % (self.content_type.app_label, self.content_type.model, template_type),
                'widgets.widget/%s' % template_type,
            ]

    def clone(self):
        return clone_model(self)

    def get_widget_in_page_configuration(self, widget_in_page_config, cleaned_data):
        """
        Update current WIP configuration, based on cleaned_data retrieved from form
        """
        widget_in_page_config.update(cleaned_data)
        return widget_in_page_config



class WidgetFetchDataFailedException(Exception): pass

