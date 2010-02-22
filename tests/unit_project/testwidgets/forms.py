from django import forms

from mypage.widgets.forms import BaseDisplayForm

class TestDisplayForm(BaseDisplayForm):
    number = forms.IntegerField(min_value=0, max_value=100)
