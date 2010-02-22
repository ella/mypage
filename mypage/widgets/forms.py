from django import forms

class BaseDisplayForm(forms.Form):
    pass

class BaseConfigForm(forms.Form):
    pass


class FieldChoice(object):
    def __init__(self, choice, is_checked):
        self.choice = choice
        self.is_checked = is_checked

    @property
    def name(self):
        return self.choice[1]

    @property
    def value(self):
        return self.choice[0]
