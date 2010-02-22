from djangosanetesting.cases import DatabaseTestCase

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser

from mypage.pages.models import Page
from mypage.pages.views import get_page

from unit_project.helpers import create_filled_default_page, SessionWrapper
from unit_project import template_loader


class TestGetPage(DatabaseTestCase):

    def setUp(self):
        super(TestGetPage, self).setUp()
        template_loader.templates = {
            'widgets.widget/widget.html': '',
            'testwidgets.testwidget/widget-a/widget.html' : '',
            'testwidgets.testwidget/widget.html' : '',
        }
        create_filled_default_page(self)

        self.user = User.objects.create()
        self.anonymous_user = AnonymousUser()
        self.default_page = Page.objects.get_for_id(settings.DEFAULT_PAGE_ID)


    def get_session(self, key=u'123', session_dict=None):
        session = SessionWrapper(session_dict or {})
        session.session_key = key
        return session

    def test_default_page_retrieved_for_anonymous_user(self):
        page = get_page(user=self.anonymous_user, session=self.get_session())
        self.assert_equals(self.default_page, page)

    def test_default_page_retrieved_for_authenticated_user(self):
        page = get_page(user=self.user, session=self.get_session())
        self.assert_equals(self.default_page, page)

    def test_new_page_for_anonymous_created_when_forced(self):
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        self.assert_not_equals(self.default_page, page)

    def test_new_page_for_authenticated_created_when_forced(self):
        page = get_page(user=self.user, session=self.get_session(), for_update=True)
        self.assert_not_equals(self.default_page, page)

    def test_anonymous_session_page_cloned_with_default_layout(self):
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        self.assert_equals(self.default_page.layout, page.layout)

    def test_user_page_cloned_with_default_layout(self):
        page = get_page(user=self.user, session=self.get_session(), for_update=True)
        self.assert_equals(self.default_page.layout, page.layout)

    def test_page_with_same_config_for_anonymous_retrieved_on_next_visit(self):
        page = get_page(user=self.user, session=self.get_session(), for_update=True)
        page.add_widget(self.widget_u)
        page.save()

        page_again = get_page(user=self.user, session=self.get_session(), for_update=True)

        self.assert_equals(page.layout, page_again.layout)

    def test_anonymous_modifications_preserved_when_logging_in_with_same_session(self):
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        page.add_widget(self.widget_u)
        page.save()

        page_again = get_page(user=self.user, session=self.get_session())

        self.assert_equals(page.layout, page_again.layout)
        self.assert_not_equals(self.default_page.layout, page_again.layout)

    def test_anonymous_page_destroyed_after_converting_to_user_page(self):
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        page.add_widget(self.widget_u)
        page.save()

        # converting to user page
        get_page(user=self.user, session=self.get_session())

        # default page now retrieved
        page = get_page(user=self.anonymous_user, session=self.get_session())
        self.assert_equals(self.default_page, page)

    def test_user_page_takes_preference_over_modified_anonymous_page(self):
        # convert session page to user
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        get_page(user=self.user, session=self.get_session())

        # create modified anonymous page
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        page.add_widget(self.widget_u)
        page.save()

        # unmodified user page should be shown after next login
        page = get_page(user=self.user, session=self.get_session())
        self.assert_equals(self.default_page.layout, page.layout)

    def test_anonymous_page_deleted_even_after_second_conversion(self):
        # this behaviour could change. See #3483

        # convert session page to user
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        get_page(user=self.user, session=self.get_session())

        # create modified anonymous page
        session_page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        session_page.add_widget(self.widget_u)
        session_page.save()

        # log in again
        get_page(user=self.user, session=self.get_session())
        self.assert_equals(self.default_page.layout, page.layout)

        # our second modification of anonymous page preserved
        page = get_page(user=self.anonymous_user, session=self.get_session(), for_update=True)
        self.assert_equals(session_page.layout, page.layout)


    def tearDown(self):
        super(TestGetPage, self).tearDown()
        template_loader.templates = {}
