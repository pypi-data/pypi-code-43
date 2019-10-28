from django import template
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.templatetags.rijkshuisstijl import register
from .rijkshuisstijl_filters import get_attr_or_get
from .rijkshuisstijl_helpers import merge_config, parse_kwarg, parse_arg, get_field_label

try:
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse_lazy


@register.inclusion_tag('rijkshuisstijl/components/filter/filter.html')
def dom_filter(**kwargs):
    """
    Renders a realtime text filter for element in the DOM.
    Elements matching the given value are shown, others are hidden.
    All items are shown by default.

    Example:

        {% dom_filter config=config %}
        {% dom_filter option1='foo' option2='bar' %}

    Available options:

        - filter_target: Required, a queryselector string matching items which should be filtered.

        - class: Optional, a string with additional CSS classes.
        - label_placeholder: Optional, alternative label to show as placeholder.
        - name: Optional, The name of the input.
        - value Optional, The (default) value of the input.

    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_placeholder'] = parse_kwarg(kwargs, 'label_placeholder', _('Filteren op pagina'))

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['filter_target'] = kwargs.get('filter_target', '')
    kwargs['name'] = kwargs.get('name', None)
    kwargs['value'] = kwargs.get('value', None)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/icon/icon.html')
def icon(icon=None, **kwargs):
    """
    Renders an icon.

    Example:

        {% icon 'foo' %}
        {% icon config=config %}
        {% icon option1='foo' option2='bar' %}

    Available options:

        - icon: Optional, The name of the icon to be rendered, can be defined by first argument.
        - src: Optional, The source of the icon to be rendered.

        - class: Optional, a string with additional CSS classes.
        - href: Optional, an optional url to link to.
        - label: Optional, An additional label to show.

    :param icon:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['href'] = kwargs.get('href', None)
    kwargs['icon'] = kwargs.get('icon', None)
    kwargs['label'] = kwargs.get('label', None)
    kwargs['src'] = kwargs.get('src', None)

    # args
    kwargs['icon'] = icon

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/key-value-table/key-value-table.html')
def key_value_table(**kwargs):
    """
    Renders an key/value table.

    Example:

        {% key_value_table config=config %}
        {% key_value_table option1='foo' option2='bar' %}

    Available options:

        - fields: Required, A dict (key, label) or a list defining which attributes of object to show.
        - object: Required, An object containing the keys defined fields.

        - class: Optional, a string with additional CSS classes.§

    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    def get_fields():
        obj = kwargs.get('object')
        fields = parse_kwarg(kwargs, 'fields', {})

        try:
            fields = [{'key': key, 'label': value} for key, value in fields.items()]
        except AttributeError:
            fields = [{'key': field, 'label': field} for field in fields]

        if obj:
            for field in fields:
                field['label'] = get_field_label(obj, field['label'])

        return fields

    def get_data():
        obj = kwargs.get('object')
        fields = get_fields()

        data = []
        if obj and fields:
            data = [(field.get('label'), getattr(obj, field.get('key'))) for field in fields]
        data = data + list(parse_kwarg(kwargs, 'data', []))
        return data

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['data'] = get_data()

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/paginator/paginator.html', takes_context=True)
def paginator(context, **kwargs):
    """
    Renders a paginator.

    Example:

        {% paginator config=config %}
        {% paginator option1='foo' option2='bar' %}

    Available options:

        - paginator: Required, A Django Paginator instance, may be obtained from context.
        - page_obj: Required, The paginator page object, may be obtained from context.

        - class: Optional, a string with additional CSS classes.
        - form: Optional, if true (default), treat the paginator as form, only works if tag is set to 'form'.
        - is_paginated: Optional, if true (default), render the paginator.
        - label_first: Optional, alternative label to show for first page.
        - label_previous: Optional, alternative label to show for previous page.
        - label_next: Optional, alternative label to show for next page.
        - label_last: Optional, alternative label to show for last page.

        - page_number: Optional, The current page number.
        - page_key: Optional, The GET parameter to use for the page, defaults to 'page'.
        - tag: Optional, The outer tag used for the paginator, defaults to 'form'.
        - zero_index: Optional, Use zero-based indexing for page numbers, not fully supported.

    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    def get_page_min():
        zero_index = kwargs.get('zero_index', False)

        if zero_index:
            return 0
        return 1

    def get_page_max():
        paginator = kwargs.get('paginator')
        zero_index = kwargs.get('zero_index', False)

        if zero_index:
            return paginator.num_pages - 1
        return paginator.num_pages

    def get_page_number():
        page_obj = kwargs.get('page_obj')
        zero_index = kwargs.get('zero_index', False)

        if page_obj:
            return page_obj.number

        return kwargs.get('page_number', 0 if zero_index else 1)

    # i18n
    kwargs['label_first'] = parse_kwarg(kwargs, 'first', _('Eerste'))
    kwargs['label_previous'] = parse_kwarg(kwargs, 'first', _('Vorige'))
    kwargs['label_next'] = parse_kwarg(kwargs, 'first', _('Volgende'))
    kwargs['label_last'] = parse_kwarg(kwargs, 'first', _('Laatste'))

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['form'] = parse_kwarg(kwargs, 'form', True)
    kwargs['is_paginated'] = kwargs.get('is_paginated', context.get('is_paginated'))
    kwargs['paginator'] = kwargs.get('paginator', context.get('paginator'))
    kwargs['page_min'] = get_page_min()
    kwargs['page_max'] = get_page_max()
    kwargs['page_number'] = get_page_number()
    kwargs['page_key'] = kwargs.get('page_key', 'page')
    kwargs['page_obj'] = kwargs.get('page_obj', context.get('page_obj'))
    kwargs['tag'] = 'div' if not kwargs['form'] else 'form'
    kwargs['zero_index'] = kwargs.get('zero_index', False)

    kwargs['request'] = context['request']
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/stacked-list/stacked-list.html')
def stacked_list(*args, **kwargs):
    """
    Renders a stacked list, optionally containing hyperlinks.

    Example:

        {% stacked_list 'foo' 'bar' %}
        {% stacked_list config=config %}
        {% stacked_list option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - field: Optional, a key in every object in object_list.
        - items: Optional, a dict (label, [url]) or a list defining with values to show, can be obtained from args.
        - url_field: Optional, A key in every object on object_list for a URL, creates hyperlinks.
        - url_reverse: Optional, A URL name to reverse using the object's 'pk' attribute as one and only attribute,
          creates hyperlinks.
        - object_list: Optional, a list of objects for which to show the value of the attribute defined by field.

    :param args:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    def get_items():
        object_list = kwargs.get('object_list')
        field = kwargs.get('field')
        items = []

        if object_list and field:
            items = [get_item(obj, field) for obj in object_list]

        return items + kwargs.get('items', [])

    def get_item(obj, field):
        url_field = kwargs.get('url_field')
        url_reverse = kwargs.get('url_reverse')
        item = {'label': get_attr_or_get(obj, field)}

        if url_field:
            item['url'] = get_attr_or_get(obj, url_field)

        if url_reverse:
            item['url'] = reverse_lazy(url_reverse, object.pk)

        if 'url' in item and not item['url']:
            try:
                if item.get_absolute_url:
                    item['url'] = item.get_absolute_url
            except AttributeError:
                pass

        return item

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['items'] = get_items()

    # args
    for arg in args:
        arg_items = arg
        if not hasattr(arg, '__iter__'):
            arg_items = [arg]

        for item in arg_items:
            kwargs['items'].append(parse_arg(item))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/title-header/title-header.html")
def title_header(title, **kwargs):
    """
    Renders a title.

    Example:

        {% title_header config=config %}
        {% title_header option1='foo' option2='bar' %}

    Available options:

        - title: Required, The title to show, may be obtained from first argument.

        - class: Optional, a string with additional CSS classes.

    :param title:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["class"] = title
    kwargs["title"] = title

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/toolbar/toolbar.html')
def toolbar(*args, **kwargs):
    """
    Renders a toolbar populated with buttons, (see rijkshuisstijl_form.button).

    Example:

        {% toolbar config=config %}
        {% toolbar option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - items: Optional, a list_of_dict (label, [href], [icon], [name], [target], [title]) defining which buttons to
          create (see rijkshuisstijl_form.button).

    :param args:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['items'] = kwargs.get('items', [])

    # args
    for arg in args:
        arg_items = arg
        if not hasattr(arg, '__iter__'):
            arg_items = [arg]

        for item in arg_items:
            kwargs['items'].append(parse_arg(item))

    for item in kwargs['items']:
        item['config'] = item

    kwargs['config'] = kwargs
    return kwargs
