import itertools
import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mypage.pages.models import Page, Widget
from mypage.rsswidgets.models import RSSWidget
from mypage.rsswidgets.forms import RSSCreationConfigForm

log = logging.getLogger('mypage.pages.forms')


class AddOrRemoveWidgetForm(forms.Form):

    COMMAND_CHOICES = [
        ('add-widget', _(u'add widget')),
        ('remove-widget', _(u'remove widget')),
    ]

    widget = forms.ModelChoiceField(queryset=None, empty_label=None)
    command = forms.ChoiceField(choices=COMMAND_CHOICES)
    
    def __init__(self, page, data=None, files=None, *args, **kwargs):
        if data is not None and data.get('command', None) not in ('add-widget', 'remove-widget'):
            data = files = None
        super(AddOrRemoveWidgetForm, self).__init__(data, files, *args, **kwargs)
        self.page = page
        commercial_ids = [id for id, x in getattr(settings, 'COMMERCIAL_EQUIVALENTS', [])]
        widget_ids = [id for id in itertools.chain(*getattr(settings, 'AVAILABLE_WIDGETS', {}).values())
                      if id not in commercial_ids]
        self.fields["widget"].queryset = Widget.objects.filter(pk__in=widget_ids)
        
    def get_available_widgets(self):
        """
        Returns available widgets grouped by category to be used in a template 
        """
        active_ids = self.page.widgets.values_list('pk', flat=True)
        choices = dict(self.fields['widget'].choices)        
        return [(group, [{'id':id, 'title': choices[id], 'active': id in active_ids} 
                         for id in ids if id in choices]) 
                for group, ids in getattr(settings, 'AVAILABLE_WIDGETS', {}).items()]
        
    def save(self):
        """
        Adds or removes a widget to/from a page
        """
        widget = self.cleaned_data['widget']
        if self.cleaned_data['command'] == 'add-widget':
            try:
                self.page.add_widget(widget)
            except ValueError, err:
                log.error("Widget %s not added: %s" % (str(widget), str(err)))
            
            for commercial_id, normal_id in getattr(settings, 'COMMERCIAL_EQUIVALENTS', []):
                if widget.pk == normal_id:
                    self.page.remove_widget(Widget.objects.get(pk=commercial_id))
        if self.cleaned_data['command'] == 'remove-widget': 
            self.page.remove_widget(widget)
            

class RemoveCustomWidgetForm(forms.Form):
    
    widget = forms.ModelChoiceField(queryset=None, empty_label=None)
    
    def __init__(self, page, data=None, files=None, *args, **kwargs):
        if data is not None and data.get('command', None) != ('remove-custom-widget'):
            data = files = None
        super(RemoveCustomWidgetForm, self).__init__(data, files, *args, **kwargs)
        self.page = page
        global_widgets_ids = list(itertools.chain(*getattr(settings, 'AVAILABLE_WIDGETS', {}).values()))
        queryset = page.widgets.filter(content_type=14).exclude(pk__in=global_widgets_ids)
        self.fields["widget"].queryset = queryset 
        
    def get_custom_widgets(self):
        """
        Returns a list of custom widgets to be used in a template
        """
        choices = dict(self.fields['widget'].choices)    
        return [{'id':id, 'title': choices[id]} for id in choices]
    
    def save(self):
        """
        Removes a widget from a page
        """
        self.page.remove_widget(self.cleaned_data["widget"])


class AddCustomWidgetForm(RSSCreationConfigForm):
    
    def __init__(self, page, data=None, files=None, *args, **kwargs):
        if data is not None and data.get('command', None) != ('add-custom-widget'):
            data = files = None
        super(AddCustomWidgetForm, self).__init__(data, files, *args, **kwargs)
        self.page = page
        
    def save(self):
        """
        Creates a rss widget and adds it to a page
        """
        url, title = self.cleaned_data['feed']
        widget, was_created = RSSWidget.objects.get_or_create(
              feed_url=url, defaults={'title': title, 'slug': ''})
        self.page.add_widget(widget)


class MyRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices)


class TemplateForm(forms.Form):

    template = Page._meta.get_field('template').formfield(widget=MyRadioSelect)

    def __init__(self, page, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.page = page
        self.initial = dict(template=page.template)

    def save(self):
        self.page.update_template(self.cleaned_data['template'])
        self.page.save()


class TemplateConfigForm(forms.Form):

    def __init__(self, page, *args, **kwargs):
        super(TemplateConfigForm, self).__init__(*args, **kwargs)
        self.page = page
        self.initial = page.layout.template_config
        self.fill_fields()

    def fill_fields(self):
        options =  getattr(settings, 'PAGE_TEMPLATE_OPTIONS', {})
        for option, value in options.items():
            self.fields[option] = forms.ChoiceField(widget=MyRadioSelect, choices=value[0], initial=value[1], required=False)

    def save(self):
        self.page.layout.template_config.update(self.cleaned_data)
        self.page.layout.template_config.save()
        self.page.save()


class ChromeConfigForm(TemplateConfigForm):
    """
    Setup template and template_config together
    """

    template = Page._meta.get_field('template').formfield(widget=MyRadioSelect)

    def __init__(self, page, *args, **kwargs):
        super(ChromeConfigForm, self).__init__(*args, **kwargs)
        self.initial.update(dict(template=page.template))

    def save(self):
        self.page.update_template(self.cleaned_data['template'])
        super(ChromeConfigForm, self).save()

