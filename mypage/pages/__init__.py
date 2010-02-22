from django.conf import settings

from django import http
from mypage.pages.models import Page, UserPage, SessionPage
from mypage.pages.layout import Layout
from mypage.widgets.models import get_object
from django.db.models import ObjectDoesNotExist

from mypage.pages.migrations.utils.layout_refactor_migration import migrate_page 


def get_page(user, session, for_update=False, defaults=None, from_page=None):
    """
    Get page for the current user. Check if they have a UserPage
    and if so, return it, return the default page otherwise.

    If for_update is specified, only return the defaul page for users
    that can edit Page (has_perm('change_page')) so that regular users won't override
    """
    from_page = from_page or settings.DEFAULT_PAGE_ID
    page = None
    session_page = None
    if for_update:
        session.modified = True
    defaults = defaults or session.get('defaults', {})
    try:
        session_page = SessionPage.objects.get(session_key=session.session_key)
    except SessionPage.DoesNotExist, e:
        pass

    if user.is_authenticated():
        # Authenticated users
        try:
            page = UserPage.objects.get(user=user)
        except UserPage.DoesNotExist, e:
            if session_page:
                # user has a session_page, clone it and save it
                page = UserPage.objects.clone_from_page(
                        page=session_page,
                        defaults=defaults,
                        user=user,
                    )
                # delete the now obsolete session_page
                session_page.delete()
                session_page = None
            elif for_update:
                # create user page from default
                page = UserPage.objects.clone_from_page(
                        page=Page.objects.get_for_id(from_page),
                        defaults=defaults,
                        user=user
                    )
    else:
        # anonymous user
        if session_page:
            # user already as a session page
            page = session_page

        elif for_update:
            # Unknown user without UserPage or SessionPage wanting to edit page must clone SessionPage
            page = SessionPage.objects.clone_from_page(
                    page=Page.objects.get_for_id(from_page),
                    defaults=defaults,
                    session_key=session.session_key
                )
    if not page:
        # read only page
        page = Page.objects.get_for_id(from_page)
        if defaults:
            for k, v in defaults.items():
                setattr(page, k, v)

    if not page.layout_migrated:
        page = migrate_page(page)

    return page


def get_widget_or_404(page, content_type_id, object_id):
    """
    Return a widget using the ct_id and obj_id pair
    """
    try:
        widget = get_object(content_type_id, object_id)
    except ObjectDoesNotExist, e:
        raise http.Http404

    try:
        wil = page.layout.get_widget(int(content_type_id), int(object_id))
    except Layout.WidgetInLayoutDoesNotExist, e:
        raise http.Http404

    return widget, wil


def is_custom_page(page):
    """
    Custom pages could be updated/deleted by users
    """
    return isinstance(page, (UserPage, SessionPage))



