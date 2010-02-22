from django.db import models

from mypage.widgets.models import Widget

from unit_project.testwidgets.forms import TestDisplayForm

class TestWidget(Widget):
    fetched = 0

    def _fetch_data(self):
        self.__class__.fetched += 1
        return {}

    def display_form(self, *args, **kwargs):
        return TestDisplayForm(*args, **kwargs)
