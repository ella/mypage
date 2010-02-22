from djangosanetesting import UnitTestCase

from django import forms
from django.http import QueryDict

from mypage.widgets.templatetags.widgets import choice_list

class TestForm(forms.Form):
    choice_field = forms.ChoiceField(choices=tuple((i, i) for i in range(1, 5)), initial=3)
    multiple_choice_field = forms.MultipleChoiceField(choices=tuple((i, i) for i in range(1, 5)), initial=[1, 3])

class TestChoiceListTemplateFilter(UnitTestCase):

    def test_choice_list_for_choice_field_unbound_form(self):
        """
        Tests choice_list for choice field on unbound form expecting field initial data usage
        """
        choices = choice_list(TestForm()['choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [3])

    def test_choice_list_for_multiple_choice_field_unbound_form(self):
        """
        Tests choice_list for multiple choice field on unbound form expecting field initial data usage
        """
        choices = choice_list(TestForm()['multiple_choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [1, 3])

    def test_choice_list_for_multiple_choice_field_unbound_form_initial_data_given(self):
        """
        Tests choice_list for multiple choice field on unbound form expecting initial data usage
        """
        choices = choice_list(TestForm(initial=dict(multiple_choice_field=[1, 2]))['multiple_choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [1, 2])

    def test_choice_list_for_multiple_choice_field_bound_form(self):
        """
        Tests choice_list for multiple choice field on unbound form expecting form data usage
        """
        choices = choice_list(TestForm(dict(multiple_choice_field=[2, 4]))['multiple_choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [2, 4])

    def test_choice_list_for_multiple_choice_field_none_field_data_given(self):
        choices = choice_list(TestForm(dict(multiple_choice_field=None))['multiple_choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [])

    def test_choice_list_for_choice_field_bound_form_querystring_data_given(self):
        """
        Tests choice_list for choice field checked var types comparsion

        Str vs. int
        """
        choices = choice_list(TestForm(QueryDict('choice_field=2'))['choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [2])

    def test_choice_list_for_muliple_choice_field_bound_form_querystring_data_given(self):
        """
        Tests choice_list for multiple choice field checked var types comparsion

        Str vs. int
        """
        choices = choice_list(TestForm(QueryDict('multiple_choice_field=2&multiple_choice_field=4'))['multiple_choice_field'])
        self.assert_equals([ch.value for ch in choices if ch.is_checked], [2, 4])


