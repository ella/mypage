from django import forms
from django.utils.translation import ugettext_lazy as _

from mypage.widgets.forms import BaseDisplayForm

DEFAULT_ITEM_COUNT = 8

class MagazinesDisplayForm(BaseDisplayForm):
    item_count = forms.ChoiceField(
            choices=tuple((i, i) for i in range(3, 9)), 
            label=_("Displayed items"), 
            initial=DEFAULT_ITEM_COUNT)
