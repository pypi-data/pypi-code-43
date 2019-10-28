import markdown2 as md
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
@stringfilter
def to_markdown(value: str) -> str:
    """
    Transforms a Markdown text into HTML.
    """

    classes_dict = {}
    markdowner = md.Markdown(extras={
        'footnotes': None,
        'header-ids': None,
        'fenced-code-blocks': None,
        'html-classes': classes_dict,
    })

    html = mark_safe(markdowner.convert(value))
    return html
