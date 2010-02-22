import anyjson as json

from django import template
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ChoiceField, MultipleChoiceField

import anyjson as json

from mypage.widgets.models import get_object, WidgetFetchDataFailedException
from mypage.widgets.forms import FieldChoice


register = template.Library()


@register.tag('widget')
def widget(parser, token):
    '''
    {% widget WIDGET_VAR WIDGETINPAGE_VAR [get_data] %}

    or

    {% widget CT_ID.PK PAGE_ID [get_data] %}
    '''
    valid_syntax = 'valid syntax is: {% widget WIDGET_VAR WIDGETINPAGE_VAR [get_data] %} || {% widget CT_ID.PK PAGE_ID [get_data] %}'

    bits = token.split_contents()
    l = len(bits)

    widget = None
    widget_in_page = None
    get_data = False

    if l < 3:
        raise template.TemplateSyntaxError("too short\n%s" % valid_syntax)
    if not '.' in bits[1]:
        # variant: widget WIDGET_VAR WIDGETINPAGE_VAR ...
        widget = template.Variable(bits[1])
        widget_in_page = template.Variable(bits[2])
    elif bits[1].count('.') == 1:
        # variant: widget CT_ID.PK PAGE_ID ...
        widget = bits[1].split('.')
        page_id = bits[2]

        try:
            widget = get_object(*widget)
            widget_in_page = widget.widgetinpage_set.get(page=page_id)
        except ObjectDoesNotExist, e:
            raise template.TemplateSyntaxError("invalid id for page or widget's type,pk\n%s" % valid_syntax)
    else:
        raise template.TemplateSyntaxError("invalid first param\n%s" % valid_syntax)

    if l == 3:
        # variant: widget .. ..
        pass
    elif l == 4 and bits[3] == 'get_data':
        # variant: widget .. .. get_data
        get_data = True
    else:
        raise template.TemplateSyntaxError("too long (%d) or invalid third param\n%s" % (l, valid_syntax))

    return WidgetNode(widget, widget_in_page, get_data)

class WidgetNode(template.Node):
    def __init__(self, widget, widget_in_page, get_data):
        self.widget, self.widget_in_page, self.get_data= widget, widget_in_page, get_data

    def render(self, context):
        widget = self.widget
        widget_in_page = self.widget_in_page
        get_data = self.get_data

        if isinstance(widget, template.Variable):
            try:
                widget = widget.resolve(context)
            except template.VariableDoesNotExist:
                # TODO: log
                return ''
        if isinstance(widget_in_page, template.Variable):
            try:
                widget_in_page = widget_in_page.resolve(context)
            except template.VariableDoesNotExist:
                # TODO: log
                return ''

        context['widget'] = widget
        context['widget_in_page'] = widget_in_page
        context['get_data'] = self.get_data

        return render_to_string(widget.get_template(widget.TEMPLATE), context)

@register.tag('widgetcontent')
def widget(parser, token):
    '''
    {% widgetcontent CT_ID.PK PAGE_ID [get_data] %}{json_config}{% endwidgetcontent %}

    TODO:
    add [using TEMPLATE_NAME] option
    and use select_template in widget.html - maybe not needed any more because of cached select_template
    '''
    valid_syntax = 'valid syntax is: {% widgetcontent CT_ID.PK PAGE_ID [get_data] %}{json_config}{% endwidgetcontent %}'

    bits = token.split_contents()
    l = len(bits)

    widget = None
    page_id = None
    get_data = False

    if l < 3:
        raise template.TemplateSyntaxError("too short\n%s" % valid_syntax)
    if bits[1].count('.') == 1:
        # variant: widgetcontent CT_ID.PK PAGE_ID ...
        widget = bits[1].split('.')
        page_id = bits[2]

        try:
            widget = get_object(*widget)
        except ObjectDoesNotExist, e:
            raise template.TemplateSyntaxError("invalid widget's type,pk\n%s" % valid_syntax)
    else:
        raise template.TemplateSyntaxError("invalid first param\n%s" % valid_syntax)

    if l == 3:
        # variant: widgetcontent .. ..
        pass
    elif l == 4 and bits[3] == 'get_data':
        # variant: widgetcontent .. .. get_data
        get_data = True
    else:
        raise template.TemplateSyntaxError("too long (%d) or invalid third param\n%s" % (l, valid_syntax))

    # parse the rest
    nodelist_config = parser.parse(('end'+bits[0],))
    parser.delete_first_token()

    return WidgetContentNode(widget, page_id, get_data, nodelist_config)

class WidgetContentNode(template.Node):
    def __init__(self, widget, page_id, get_data, nodelist_config):
        self.widget, self.page_id, self.get_data= widget, page_id, get_data
        self.nodelist_config = nodelist_config

    def render(self, context):
        """
        render widget conent

        similar to mypage.pages.views.get_content
        but does not fetch data (if not get_data given)
        """
        config = self.nodelist_config.render(context).strip()
        if config:
            config = json.deserialize(config)
        else:
            config = {}

        try:
            return self.widget.get_content(config, context, allow_fetch=self.get_data)
        except WidgetFetchDataFailedException, e:
            return render_to_string('widgets.widget/content500.html')


@register.filter
def choice_list(bound_field):
    """
    {% for choice in form.somemultiplechoicefield|choice_list %}
        <input type="checkbox... {{ choice.value }} {{ choice.name }} {{ choice.is_checked }} ...
    {% endfor %}
    """

    def get_data(bound_field):
        if bound_field.form.is_bound:
            return bound_field.data
        data = bound_field.form.initial.get(bound_field.name, bound_field.field.initial)
        if callable(data):
            return data()
        return data

    data = get_data(bound_field)

    if isinstance(bound_field.field, MultipleChoiceField):
        if data is None: data = []
        checker = lambda x, y: str(x) in map(str, y)
    elif isinstance(bound_field.field, ChoiceField):
        checker = lambda x, y: str(x) == str(y)
    else:
         raise template.TemplateSyntaxError("choice_list filter can be used only on ChoiceField or MultipleChoiceField object.")

    return [FieldChoice(choice, checker(choice[0], data)) for choice in bound_field.field.choices]
