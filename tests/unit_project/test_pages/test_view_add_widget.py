from djangosanetesting import DestructiveDatabaseTestCase

from django.conf import settings

from unit_project.helpers import create_filled_default_page, build_request
from unit_project import template_loader
from unit_project.testwidgets.models import TestWidget

from mypage.widgets.models import Widget
from mypage.pages.models import Page
from mypage.pages.views import add_widget

class TestViewAddWidget(DestructiveDatabaseTestCase):
    """
    Add Widget to Page view tests

    Only widgets identified via EXTERNALY_ADDABLE_WIGDETS dict can be inserted.
    This view can also make a WIP configuration.
    """

    def setUp(self):
        super(TestViewAddWidget, self).setUp()
        template_loader.templates = {'widgets.widget/widget.html': ''}
        create_filled_default_page(self)
        settings.EXTERNALY_ADDABLE_WIGDETS = {'widgetidentifier': self.widget_a.pk,}

    def tearDown(self):
        super(TestViewAddWidget, self).tearDown()
        template_loader.templates = {}
        settings.EXTERNALY_ADDABLE_WIGDETS = {}

    def test_add_widget(self):
        """
        Add a new widget to page
        """
        widget = Widget.objects.create(title='New Widget', slug='new-widget')
        settings.EXTERNALY_ADDABLE_WIGDETS['newwidgetident'] = widget.pk
        request = build_request()
        response = add_widget(request, 'newwidgetident')
        # redirection after success assertion
        self.assert_equals(response.status_code, 302)
        # was custom page created?
        self.assert_equals(Page.objects.count(), 2)
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        # was new wil created?
        self.assert_equals(len(page.layout.widgets), 4)

    def test_add_widget_allready_in_page(self):
        """
        Add to page an allready assigned widget
        """
        request = build_request()
        response = add_widget(request, 'widgetidentifier')
        self.assert_equals(response.status_code, 302)
        # was custom page created?
        # TODO if configuration via add_widget is not possible, custom page should NOT be created
        self.assert_equals(Page.objects.count(), 2)
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        # wasn't new wil created?
        self.assert_equals(len(page.layout.widgets), 3)

    def test_add_widget_unknown(self):
        """
        Tries to add unknown widget

        404 must be responsed
        """
        request = build_request()
        response = add_widget(request, 'unknownidentifier')
        self.assert_equals(response.status_code, 404)


    '''

    TODO:

    def test_add_and_configure_widget(self):
        """
        Add and configure new widget
        """
        widget = TestWidget.objects.create(title='New Widget', slug='new-widget')
        settings.EXTERNALY_ADDABLE_WIGDETS['newwidgetident'] = widget.pk
        request = build_request(get_query='number=50')
        response = add_widget(request, 'newwidgetident')
        # was new wip on a new custom page configured?
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        wip = WidgetInPage.objects.get(widget=widget, page=page)
        self.assert_equals(wip.config, {'number': 50})

    def test_configure_allready_assigned_widget(self):
        """
        Configure allready assigned widget
        """
        request = build_request(get_query='number=50')
        response = add_widget(request, 'widgetidentifier')
        self.assert_equals(Page.objects.count(), 2)
        # was new wip on a new custom page configured?
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        wip = WidgetInPage.objects.get(
                widget=Widget.objects.get(pk=settings.EXTERNALY_ADDABLE_WIGDETS['widgetidentifier']), 
                page=page)
        self.assert_equals(wip.config, {'number': 50})

    def test_add_and_configure_widget_invalid_form_data(self):
        """
        Add and try to configure widget with invalid form data

        Configuration will fail silently
        """
        widget = TestWidget.objects.create(title='New Widget', slug='new-widget')
        settings.EXTERNALY_ADDABLE_WIGDETS['newwidgetident'] = widget.pk
        request = build_request(get_query='number=5000')
        response = add_widget(request, 'newwidgetident')
        # was new wip on a new custom page configured?
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        wip = WidgetInPage.objects.get(widget=widget, page=page)
        self.assert_equals(wip.config, {})
    '''
