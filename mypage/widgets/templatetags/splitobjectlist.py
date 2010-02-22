from django import template
from django.template import TemplateSyntaxError, resolve_variable

register = template.Library()

def split_list(l, cols):
    rows, r = divmod(len(l), cols)
    rows += (r!=0)
    splitted = []
    for i in range(cols):
        x = i*rows
        y = x+rows
        splitted.append(l[x:y])
    return splitted

class SplitObjectListNode(template.Node):

    def __init__(self, object_list, cols, var_name):
        self.object_list = object_list
        self.cols = cols
        self.var_name = var_name

    def render(self, context):
        try:
            object_list = template.resolve_variable(self.object_list, context)
            cols = template.resolve_variable(self.cols, context)
        except template.VariableDoesNotExist, e:
            return ''
        context[self.var_name] = split_list(object_list, cols)
        return ''

@register.tag
def splitobjectlist(self, token):
    """
    {% split <object_list> to <cols> as <var_name> %}
    e.g.:
    {% split object_list to 3 as object_lists %}
    {% for list in object_lists %}
    <ul>
        {% for object in list %}
            <li>{{ object }}</li>
        {% endfor %}
    </ul>
    """
    bits = token.split_contents()
    if len(bits) != 6 or bits[2] != 'to' or bits[4] != 'as':
        raise template.TemplateSyntaxError("Obscure format of '%s' tag. Usage: {% split <object_list> to <count> as <var_name> %}")
    object_list = bits[1]
    cols = bits[3]
    var_name = bits[5]
    return SplitObjectListNode(object_list, cols, var_name)
