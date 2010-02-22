from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.conf import settings

from mypage.pages.models import Page
from mypage.pages.layout import WidgetInLayout
from mypage.widgets.models import Widget
from unit_project.testwidgets.models import TestWidget
import anyjson as json

def create_default_page(case):
    """
    Creates a default page and stick it to given test case
    """
    p = Page(template='page.html', skin='', layout_json='{"static_containers": [], "containers": []}', id=settings.DEFAULT_PAGE_ID, layout_migrated=True)
    p.save()
    case.page = p

def create_filled_default_page(case):
    """
    Creaates a default page filled with three test widgets and stick it to given test case
    """

    create_default_page(case)
    case.widget_a = w_a = TestWidget.objects.create(title='Widget A', slug='widget-a')
    case.widget_b = w_b = TestWidget.objects.create(title='Widget B', slug='widget-b')
    case.widget_c = w_c = TestWidget.objects.create(title='Widget C', slug='widget-c')
    # widget_unassigned (to page or whatever)
    case.widget_u = w_u = TestWidget.objects.create(title='Widget U', slug='widget-u')

    stored_layout = {
        'static_containers': [],
        'containers': [[
                {
                    'widget_ct_id': w_a.content_type_id,
                    'widget_id': w_a.pk,
                    'config': {},
                    'state': WidgetInLayout.STATE_NEW,
                },
                {
                    'widget_ct_id': w_b.content_type_id,
                    'widget_id': w_b.pk,
                    'config': {},
                    'state': WidgetInLayout.STATE_NEW,
                },
            ],[
                {
                    'widget_ct_id': w_c.content_type_id,
                    'widget_id': w_c.pk,
                    'config': {},
                    'state': WidgetInLayout.STATE_NEW,
                },
            ]]
    }
    case.page.layout_json = json.serialize(stored_layout)
    case.page.save()

def build_layout_containers(*widgets_in_containers):
    containers = []
    for container in widgets_in_containers:
        containers.append([[unicode(widget.content_type_id), unicode(widget.pk)] for widget in container])
    return containers

class SessionWrapper(dict):
    pass

def build_request(get_query=None, post_query=None, session={}, cookies={}, ip_address=None):
    """
    Returns request object with useful attributes
    """
    from django.http import HttpRequest, QueryDict
    from django.contrib.auth.middleware import LazyUser
    request = HttpRequest()
    # GET and POST
    if get_query:
        request.GET = QueryDict(get_query)
    if post_query:
        request.POST = QueryDict(post_query)
    # Session and cookies
    request.session = SessionWrapper(session)
    request.session.session_key = 'XXX'
    request.COOKIES = cookies
    # User
    request.__class__.user = LazyUser()
    # Meta
    request.META['REMOTE_ADDR'] = ip_address or '0.0.0.0'
    return request

def get_widget(pk):
    return Widget.objects.get(pk=pk).get_child()
