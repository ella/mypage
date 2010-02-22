import feedparser

from django import forms
from django.utils.translation import ugettext_lazy as _

from mypage.widgets.forms import BaseDisplayForm, BaseConfigForm
from mypage.rsswidgets.conf import settings


def validate_feed(feed_url):
    """
    Downloads and parses feed from given URL

    Returns feed URL and title pair tuple.
    """
    rssfeed = feedparser.parse(feed_url)
    if rssfeed.bozo:
        raise forms.util.ValidationError(_("'%s' is not a valid RSS Feed") % feed_url)
    return feed_url, rssfeed.feed.title

class RSSFeedField(forms.URLField):
    def clean(self, value):
        value = super(RSSFeedField, self).clean(value)
        return validate_feed(value)

class RSSDisplayForm(BaseDisplayForm):
    item_count = forms.ChoiceField(choices=tuple((i, i) for i in range(3, 9)), label=_("Displayed items"), initial=settings.DEFAULT_ITEM_COUNT)

class RSSCreationConfigForm(BaseConfigForm):
    feed = RSSFeedField(label=_("Feed URL"))
