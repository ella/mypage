
from django import template

register = template.Library()

def add_remove_widget_form(widget):    
    return {'widget': widget}

register.inclusion_tag('add_remove_widget_form.html')(add_remove_widget_form)