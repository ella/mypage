from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.template import Library, Node, TextNode, resolve_variable
from django.template.loader import select_template

from django.template.loader_tags import ExtendsNode

register = Library()

EXTENDED_TEMPLATE_PATTERN = '%s/%s'

class XExtendsNode(ExtendsNode):
    must_be_first = True

    def __init__(self, nodelist, parent_name, parent_name_expr, template_dirs=None, option=None):
        super(XExtendsNode, self).__init__(nodelist, parent_name, parent_name_expr, template_dirs)
        self.option = option

    def __repr__(self):
        if self.parent_name_expr:
            return "<XExtendsNode: xextends %s>" % self.parent_name_expr.token
        return '<XExtendsNode: xextends "%s">' % self.parent_name

    def get_parent(self, context):
        option = resolve_variable(self.option, context)
        if self.parent_name_expr:
            self.parent_name = self.parent_name_expr.resolve(context)
        parent = self.parent_name
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name_expr:
                error_msg += " Got this from the '%s' variable." % self.parent_name_expr.token
            raise TemplateSyntaxError, error_msg
        if hasattr(parent, 'render'):
            return parent # parent is a Template object
        templates = [EXTENDED_TEMPLATE_PATTERN % (option, parent), parent]
        try:
            return select_template(templates)
        except TemplateDoesNotExist:
            raise TemplateSyntaxError, "Template %r cannot be extended, because it doesn't exist" % parent


def do_xextends(parser, token):
    """
    Signal that this template extends a parent template.

    This tag may be used in two ways: ``{% extends "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% extends variable %}`` uses the value of ``variable`` as either the
    name of the parent template to extend (if it evaluates to a string) or as
    the parent tempate itelf (if it evaluates to a Template object).
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError, "'%s' takes two arguments" % bits[0]
    parent_name, parent_name_expr = None, None
    if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
        parent_name = bits[1][1:-1]
    else:
        parent_name_expr = parser.compile_filter(bits[1])
    option = bits[2]
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError, "'%s' cannot appear more than once in the same template" % bits[0]
    if nodelist.get_nodes_by_type(XExtendsNode):
        raise TemplateSyntaxError, "'%s' cannot appear more than once in the same template" % bits[0]
    return XExtendsNode(nodelist, parent_name, parent_name_expr, option=option)


register.tag('xextends', do_xextends)
