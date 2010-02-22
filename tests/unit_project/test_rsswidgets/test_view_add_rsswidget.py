from djangosanetesting import DatabaseTestCase

from django.conf import settings
from django import forms

from unit_project.helpers import create_filled_default_page, build_request
from unit_project import template_loader

from mypage.rsswidgets.models import RSSWidget
from mypage.rsswidgets import forms as rss_forms
from mypage.rsswidgets.views import add_rss_widget
from mypage.pages.models import Page

def validate_feed(feed_url):
    if feed_url == 'http://example.com/valid_rss_feed/':
        return feed_url, 'fake feed title'
    else:
        raise forms.util.ValidationError('')

class TestViewAddRSSWidget(DatabaseTestCase):
    """
    Add RSSWidget to Page view tests

    Based on get_or_create by given feed_url (If an RSSWidget object 
    with given feed_url allready exists, it will be asigned to page, 
    otherwise new RSSWidget will be created and assigned).
    """

    def setUp(self):
        super(TestViewAddRSSWidget, self).setUp()
        template_loader.templates = {'widgets.widget/widget.html': ''}
        create_filled_default_page(self)
        self.origin_validate_field = rss_forms.validate_feed
        rss_forms.validate_feed = validate_feed

    def tearDown(self):
        super(TestViewAddRSSWidget, self).tearDown()
        template_loader.templates = {}
        rss_forms.validate_feed = self.origin_validate_field
        del(self.origin_validate_field)

    def test_create_and_add_rss_widget(self):
        request = build_request(get_query='feed=http://example.com/valid_rss_feed/')
        response = add_rss_widget(request)
        # redirection after success assertion
        self.assert_equals(response.status_code, 302)
        # was new widget created?
        self.assert_equals(RSSWidget.objects.count(), 1)
        # was custom page created?
        self.assert_equals(Page.objects.count(), 2)
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        # was new wil created?
        self.assert_equals(len(page.layout.widgets), 4)

    def test_add_rss_widget(self):
        new_widget = RSSWidget.objects.create(title='Some RSS Feed', feed_url='http://example.com/valid_rss_feed/')
        self.page.add_widget(new_widget)
        request = build_request(get_query='feed=http://example.com/valid_rss_feed/')
        response = add_rss_widget(request)
        # redirection after success assertion
        self.assert_equals(response.status_code, 302)
        # wasn't new widget created?
        self.assert_equals(RSSWidget.objects.count(), 1)
        # was custom page created?
        self.assert_equals(Page.objects.count(), 2)
        page = Page.objects.exclude(pk=settings.DEFAULT_PAGE_ID).get()
        # was new wil created?
        self.assert_equals(len(page.layout.widgets), 4)

    def test_add_rss_vidget_bad_feed(self):
        request = build_request(get_query='feed=http://example.com/INVALID_rss_feed/')
        response = add_rss_widget(request)
        # bad request after failure
        # TODO if not used as ajax rss fedd insertion, return somethin better than bad request
        self.assert_equals(response.status_code, 400)
        # wasn't custom page created?
        self.assert_equals(Page.objects.count(), 1)

    def test_add_rss_vidget_bad_arg(self):
        request = build_request()
        response = add_rss_widget(request)
        self.assert_equals(response.status_code, 400)
