from django import http
from django.core.urlresolvers import reverse

from mypage.pages.views import get_page
from mypage.rsswidgets.forms import RSSCreationConfigForm
from mypage.rsswidgets.models import RSSWidget


def add_rss_widget(request):

    creation_form = RSSCreationConfigForm(request.GET)

    if not creation_form.is_valid():
        return http.HttpResponseBadRequest('')

    page = get_page(request.user, request.session, for_update=True)

    url, title = creation_form.cleaned_data['feed']
    w, was_created =  RSSWidget.objects.get_or_create(
        feed_url=url,
        defaults={'title': title, 'slug': ''})

    page.add_widget(w)
    page.save()

    return http.HttpResponseRedirect(reverse('home_page'))
