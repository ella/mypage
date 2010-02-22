# -*- coding: utf-8 -*-

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.
import logging
import datetime
import socket
import re
import itertools
import time

import anyjson as json

from django.shortcuts import render_to_response
from django.db.models import ObjectDoesNotExist
from django.db import transaction
from django.template import RequestContext, Template, loader
from django import http
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils.cache import add_never_cache_headers, patch_vary_headers
from django.utils.http import cookie_date
from django.utils.encoding import force_unicode
from django.views.defaults import server_error

import anyjson as json

from mypage.pages.conf import settings
from mypage.pages import get_page, get_widget_or_404, is_custom_page
from mypage.pages.models import Page, Layout, UserPage, SessionPage
from mypage.pages.forms import TemplateConfigForm, TemplateForm, ChromeConfigForm
from mypage.widgets.models import Widget, WidgetFetchDataFailedException
from mypage.widgets.models import get_object

CACHE_PAGE = True

SETTAB_GET_PARAM_NAME = 'settab'
SETTAB_PARSER = re.compile("(?P<widget_ct_id>\d+):(?P<widget_id>\d+):(?P<tab>.*)")

RENDERED_PAGE_KEY = 'Page:%(pk)d:%(show_welcome)d:%(template_config)s'

log = logging.getLogger('mypage.pages.views')


class ConfigureWidgetJsonResponse(http.HttpResponse):

    def __init__(self, result, messages):
        content = json.serialize(dict(
                result=result,
                messages=messages))
        super(ConfigureWidgetJsonResponse, self).__init__(
                content, content_type='application/jsonrequest') # by http://json.org/JSONRequest.html (there are many variations of json content type)


def commit_on_success_response(func):
    SUCCESS_CODES = (200, 302)
    """
    copied from django.db.transaction.commit_on_success

    This decorator activates commit on response. This way, if the view function
    runs successfully, a commit is made; if the viewfunc returns anything but a 200
    or 302, a rollback is made.
    Also, if the view was unsuccesful don't save the session !
    """
    def _commit_on_success(request, *args, **kw):
        try:
            transaction.enter_transaction_management()
            transaction.managed(True)
            try:
                res = func(request, *args, **kw)
            except:
                # TODO: if OperationalError restart the transaction - call func() again
                # just only do it once
                transaction.rollback()
                request.session.modified = False
                raise
            else:
                if not res.status_code in SUCCESS_CODES:
                    transaction.rollback()
                    request.session.modified = False
                else:
                    transaction.commit()
                return res
        finally:
            transaction.leave_transaction_management()
    return wraps(func)(_commit_on_success)


def render_page(request, page, extra_context=None, settab=[]):
    context = RequestContext(request)
    context['page'] = page
    context['show_welcome'] = request.session.get('show_welcome', False)
    context['layout'] = page.layout.render(context, settab=settab)
    context.update(extra_context or {})

    template = loader.get_template(page.template)
    return template.render(context)


def home_page(request):
    """
    Get the page for current user and render it to the user

    This view does not update the page.
    """

    page = get_page(request.user, request.session)

    settab = SETTAB_PARSER.match(request.GET.get(SETTAB_GET_PARAM_NAME, ''))
    if settab:
        settab = settab.groupdict()

    cache_page = (
            getattr(settings, 'MYPAGE_CACHE_PAGE', CACHE_PAGE)
                and
            not settab
                and
            (page.pk == settings.DEFAULT_PAGE_ID and not request.user.is_authenticated())
        )
    cache_key = RENDERED_PAGE_KEY % {
         "pk": page.pk,
         "show_welcome": 'show_welcome' in request.session and 2 or 3,
         "template_config" : page.layout.template_config.as_hash(),
    }

    if cache_page:
        # return default page directly
        out = cache.get(cache_key)
        if out is not None:
            response = http.HttpResponse(out)
            patch_vary_headers(response, ('Cookie',))
            return response

    out = render_page(request, page, settab=settab)

    if cache_page:
        # save default page
        cache.set(cache_key, out, getattr(settings, 'RENDERED_PAGE_TIMEOUT', 60))

    response = http.HttpResponse(out)
    patch_vary_headers(response, ('Cookie',))
    return response

def skinit(request, skin):
    """
    This view does not update the page.
    """
    if skin not in dict(skin_choices()):
        raise http.Http404
    defaults = {'skin': skin}
    request.session['defaults'] = defaults
    page = get_page(request.user, request.session, defaults=defaults)
    return http.HttpResponse(render_page(request, page, extra_context={"skinit": skin}))

def configure_widget(request, content_type_id, object_id):
    """
    Get a widget in page and call it's configure method

    This view updates the page.
    """
    def response(request, *args, **kwargs):
        if request.is_ajax():
            return ConfigureWidgetJsonResponse(*args, **kwargs)
        else:
            return http.HttpResponseRedirect(reverse('home_page'))

    page = get_page(request.user, request.session, for_update=True)

    widget, wil = get_widget_or_404(page, content_type_id, object_id)

    form = widget.display_form(request.POST, request.FILES)

    if not form.is_valid():
        errs = dict( (key, map(force_unicode, value)) for key, value in form.errors.items() )
        return response(request, 'KO', errs)

    wil.configure(form.cleaned_data, widget.get_widget_in_page_configuration)
    page.save()

    return response(request, 'OK', [])

def set_state(request, content_type_id, object_id):
    """
    This view updates the page.
    """
    page = get_page(request.user, request.session, for_update=True)

    widget, wil = get_widget_or_404(page, content_type_id, object_id)

    try:
        wil.state = request.POST.get('state')
        page.save()
    except (ValueError), e: # TODO DataError
        return http.HttpResponseBadRequest(json.serialize(['KO', 'Invalid state value']))

    return http.HttpResponse()

def reset_page(request):
    """
    This view does not update the page.
    """
    page = get_page(request.user, request.session)
    if is_custom_page(page):
        page.delete()
    return http.HttpResponseRedirect(reverse('home_page'))

def set_theme(request, theme):
    try:
        from_page = settings.PAGE_THEMES[theme]
    except KeyError, e:
        raise http.Http404
    page = get_page(request.user, request.session)
    if is_custom_page(page):
        page.delete()
    page = get_page(request.user, request.session, for_update=True, from_page=from_page)
    return http.HttpResponseRedirect(reverse('home_page'))

def widget_action(request, content_type_id, object_id, to_call):
    """
    Get a widget in page and call it's to_call method

    This view can update the page by POST request.
    """
    for_update = request.method == 'POST'
    page = get_page(request.user, request.session, for_update=for_update)

    widget, wil = get_widget_or_404(page, content_type_id, object_id)
    try:
        result = widget.action_dispatcher(request, wil, to_call=to_call)
    except WidgetFetchDataFailedException, e:
        return render_to_response('widgets.widget/content500.html')
    except Widget.ActionMethodDoesNotExists, e:
        raise http.Http404
    if for_update and page.layout.changed:
        page.save()
    if isinstance(result, http.HttpResponse):
        return result
    return http.HttpResponse(result)

def get_content(request, content_type_id, object_id):
    """
    Get rendered widget content

    This view always fetches data for now
    and generates cache.
    This view does not update the page.
    """
    lock_key = 'get_content_lock:%s:%s' % (content_type_id, object_id)
    lock = cache.get(lock_key)
    if lock:
        # content locked - failed import - do not download
        return render_to_response('widgets.widget/content500.html')

    page = get_page(request.user, request.session)

    widget, wil = get_widget_or_404(page, content_type_id, object_id)

    tab = request.GET.get('tab', None)
    tab = request.POST.get('tab', tab)

    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(5)
    try:
        # it would be better to lock here, but we cannot do so because of mailwidget
        out = http.HttpResponse(widget.get_content(wil.config, RequestContext(request), allow_fetch=True, tab=tab))
        cache.delete(lock_key)
        return out
    except WidgetFetchDataFailedException, e:
        # TODO:
        # or should this be cached as well?
        # there will be inconsistency with mypage.widgets.templatetags.widgets.EMPTY_CONTENT
        log.warning(u'Fetching for %s failed (%r).', widget, e)

        # lock for 5 minutes to avoid other threads from doing the same mistake
        cache.set(lock_key, 'LOCKED', 300)

        return render_to_response('widgets.widget/content500.html')
    finally:
        socket.setdefaulttimeout(old)

def get_display_form(request, content_type_id, object_id):
    """
    This view does not update the page.
    """

    page = get_page(request.user, request.session)

    widget, wil = get_widget_or_404(page, content_type_id, object_id)

    form = widget.display_form(None, initial=wil.config)

    response = render_to_response(widget.get_template(widget.DISPLAY_FORM_TEMPLATE), {'form': form, 'widget': widget}, context_instance=RequestContext(request))
    add_never_cache_headers( response )
    return response



def check_containers(containers):
    """
    Transforms string ids to ints
    """
    return [map(lambda x: map(lambda y: int(y), x), c) for c in containers]


@commit_on_success_response
def update_layout(request):
    """
    This view updates the page.
    """

    layout = request.POST.get('layout', None)

    if layout is None:
        return http.HttpResponseBadRequest()
    try:
        layout = json.deserialize(layout)
    except ValueError: # No JSON object could be decoded
        return http.HttpResponseBadRequest()

    # temporary from [u'1', u'1'] -> [1, 1]
    layout['containers'] = check_containers(layout['containers'])

    page = get_page(request.user, request.session, for_update=True)

    if layout['timestamp'] <= page.layout['timestamp']:
        return http.HttpResponseForbidden(json.serialize(['KO', 'Expired']))

    page.layout.arrange_widgets(layout['containers'])
    page.layout['timestamp'] = layout['timestamp']
    page.save()

    return http.HttpResponse()


@commit_on_success_response
def add_widget(request, identifier):
    """
    This view updates the page.
    """

    try:
        widget = Widget.objects.get(pk=getattr(settings, 'EXTERNALY_ADDABLE_WIGDETS', {})[identifier])
    except (KeyError, Widget.DoesNotExist):
        return http.HttpResponseNotFound()

    page = get_page(request.user, request.session, for_update=True)
    page.add_widget(widget)
    page.save()

    # WIL configuration - failed silently if form data are invalid
    if request.GET:
        form = widget.get_child().display_form(request.GET)
        if form.is_valid():
            page.layout.configure_widget_by_instance(widget)
            page.save()

    return http.HttpResponseRedirect(reverse('home_page'))


@commit_on_success_response
def fill_my_page(request):
    """
    Fills page with all available widgets

    This view updates the page.
    """
    page = get_page(request.user, request.session, for_update=True)
    widgets = Widget.objects.filter(
            pk__in=itertools.chain(*settings.AVAILABLE_WIDGETS.values()))
    page.add_widgets(widgets)
    page.layout.arrange_containers(len(page.layout['containers']))
    page.save()
    return http.HttpResponseRedirect(reverse('home_page'))


class SetupPageView(object):

    template = None
    form_class = None

    def __call__(self, request):
        if request.method == 'POST':
            return self.POST(request)
        return self.GET(request)

    def GET(self, request):
        page = get_page(request.user, request.session)
        form = self.form_class(page)
        return self.response(request, page=page, form=form)

    def POST(self, request):
        page = get_page(request.user, request.session, for_update=True)
        form = self.form_class(page, data=request.POST)

        # valid input
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return ConfigureWidgetJsonResponse('OK', [])
            else:
                return http.HttpResponseRedirect(reverse('home_page'))

        # invalid input
        if request.is_ajax():
            errors = dict((key, map(force_unicode, value)) for key, value in form.errors.items())
            return ConfigureWidgetJsonResponse('KO', errors)
        else:
            return self.response(request, page=page, form=form)

    def response(self, request, **context):
        response = render_to_response(self.template, context, context_instance=RequestContext(request))
        add_never_cache_headers(response)
        return response


class SetupPageTemplateView(SetupPageView):
    template = 'setup_page_template.html'
    form_class = TemplateForm


class SetupPageTemplateConfigView(SetupPageView):
    template = 'setup_page_template_config.html'
    form_class = TemplateConfigForm


class SetupPageChromeView(SetupPageView):
    template = 'setup_page_chrome.html'
    form_class = ChromeConfigForm


def reset_page_template(request):
    page = get_page(request.user, request.session)
    if is_custom_page(page):
        default_page = Page.objects.get_for_id(settings.DEFAULT_PAGE_ID)
        page.template = default_page.template
        page.save()
    return http.HttpResponseRedirect(reverse('home_page'))


def reset_page_template_config(request):
    page = get_page(request.user, request.session)
    if is_custom_page(page):
        default_page = Page.objects.get_for_id(settings.DEFAULT_PAGE_ID)
        page.layout['template_config'] = default_page.layout.template_config
        page.layout.save()
        page.save()
    return http.HttpResponseRedirect(reverse('home_page'))


# ===================
# Setup page widgets:

from mypage.pages.forms import AddOrRemoveWidgetForm, RemoveCustomWidgetForm, \
                               AddCustomWidgetForm

@commit_on_success_response
def setup_page_widgets(request):
    """
    Setup page where user can add or remove widgets

    This view updates the page (POST method called).
    """
    page = get_page(request.user, request.session, for_update=(request.method == 'POST'))

    add_or_remove_widget_form = AddOrRemoveWidgetForm(page, data=request.POST)
    if add_or_remove_widget_form.is_valid():
        add_or_remove_widget_form.save()
        if request.is_ajax():
            widget = add_or_remove_widget_form.cleaned_data["widget"]
            widget.active = add_or_remove_widget_form.cleaned_data["command"] == 'add-widget'
            return render_to_response('add_remove_widget_form.html', {
                  'widget': widget,
            })
        return http.HttpResponseRedirect(reverse('setup_page_widgets'))

    remove_custom_widget_form = RemoveCustomWidgetForm(page, data=request.POST)
    if remove_custom_widget_form.is_valid():
        remove_custom_widget_form.save()
        return http.HttpResponseRedirect(reverse('setup_page_widgets'))

    add_rss_widget_form = AddCustomWidgetForm(page, data=request.POST)
    if add_rss_widget_form.is_valid():
        widget = add_rss_widget_form.save()
        return http.HttpResponseRedirect(reverse('setup_page_widgets'))

    if request.is_ajax():
        # There is no normal way to send ajax request with invalid form
        return http.HttpResponseServerError("Invalid request")
    context = {
        'add_or_remove_widget_form': add_or_remove_widget_form,
        'available_widgets': add_or_remove_widget_form.get_available_widgets(),
        'remove_custom_widget_form': remove_custom_widget_form,
        'custom_widgets': remove_custom_widget_form.get_custom_widgets(),
        'add_rss_widget_form': add_rss_widget_form,
        'page': page,
    }
    response = render_to_response('setup-page-widgets.html', context,
                              context_instance=RequestContext(request))
    add_never_cache_headers(response)
    return response


# End setup page widgets
# ===================

def custom500(request):
    if request.is_ajax():
        return server_error(request, template_name='widgets.widget/content500.html')
    return server_error(request)

