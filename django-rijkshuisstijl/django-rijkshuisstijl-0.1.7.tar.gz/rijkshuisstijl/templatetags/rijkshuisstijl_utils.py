from django import template

register = template.Library()


class CaptureNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output
        return ''


@register.tag
def capture(parser, token):
    """
    Captures contents and assigns them to variable.
    Allows capturing templatetags that don't support "as".

    Example:

        {% capture as body %}{% lorem 20 w random %}{% endcapture %}
        {% include 'components/text/text.html' with body=body only %}
    """
    args = token.split_contents()
    if len(args) < 3 or args[-2] != 'as':
        raise template.TemplateSyntaxError("'capture' tag requires a variable name after keyword 'as'.")
    var_name = args[-1]
    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, var_name)


@register.tag('try')
def tryexcept(parser, token):
    """
    Creates try/except blog within a template.

    Example:

        {% try %}
            {% foo %}
        {% except %}
            Something went wrong...
        {% endtry %}
    """
    nodelist_try = parser.parse(('except',))
    parser.next_token()
    nodelist_except = parser.parse(('endtry',))
    parser.delete_first_token()
    return TryNode(nodelist_try, nodelist_except)


class TryNode(template.Node):
    def __init__(self, nodelist_try, nodelist_except):
        self.nodelist_try = nodelist_try
        self.nodelist_except = nodelist_except

    def render(self, context):
        try:
            return self.nodelist_try.render(context)
        except:
            return self.nodelist_except.render(context)

