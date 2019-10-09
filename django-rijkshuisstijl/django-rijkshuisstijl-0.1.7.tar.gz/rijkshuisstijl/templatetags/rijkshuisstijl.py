import json
import re
from uuid import uuid4

from django import template
from django.http import QueryDict
from django.templatetags.static import static
from django.utils import formats
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _
from .rijkshuisstijl_filters import get_attr

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

try:
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse_lazy

register = template.Library()


@register.inclusion_tag('rijkshuisstijl/components/button/button.html')
def button(**kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['icon'] = kwargs.get('icon', None)
    kwargs['id'] = kwargs.get('id', None)
    kwargs['label'] = kwargs.get('label', None)
    kwargs['title'] = kwargs.get('title', kwargs.get('label'))
    kwargs['toggle_target'] = kwargs.get('toggle_target', None)
    kwargs['toggle_modifier'] = kwargs.get('toggle_modifier', None)
    kwargs['type'] = kwargs.get('type', None)
    kwargs['name'] = kwargs.get('name', None)
    kwargs['value'] = kwargs.get('value', None)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/button/link.html')
def button_link(**kwargs):
    kwargs = merge_config(kwargs)

    kwargs['class'] = kwargs.get('class', None)
    kwargs['icon'] = kwargs.get('icon', None)
    kwargs['href'] = kwargs.get('href', '')
    kwargs['target'] = kwargs.get('target', None)
    kwargs['label'] = kwargs.get('label', None)
    kwargs['title'] = kwargs.get('title', kwargs.get('label'))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/confirm-form/confirm-form.html', takes_context=True)
def confirm_form(context, **kwargs):
    def get_id():
        return kwargs.get('id', 'confirm-form-' + str(uuid4()))

    def get_object_list():
        context_object_list = context.get('object_list', [])
        context_queryset = context.get('queryset', context_object_list)
        object_list = kwargs.get('object_list', context_queryset)
        object_list = kwargs.get('queryset', object_list)
        return object_list

    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_confirm'] = parse_kwarg(kwargs, 'label_confirm', _('Bevestig'))

    # kwargs
    kwargs['id'] = get_id()
    kwargs['class'] = kwargs.get('class', None)
    kwargs['method'] = kwargs.get('method', 'post')
    kwargs['object_list'] = get_object_list()
    kwargs['name_object'] = kwargs.get('name_object', 'object')
    kwargs['name_confirm'] = kwargs.get('name_confirm', 'confirm')
    kwargs['status'] = kwargs.get('status', 'warning')
    kwargs['title'] = kwargs.get('title', _('Actie bevestigen'))
    kwargs['text'] = kwargs.get('text', _('Weet u zeker dat u deze actie wilt uitvoeren?'))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/filter/filter.html')
def dom_filter(**kwargs):
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


@register.inclusion_tag('rijkshuisstijl/components/datagrid/datagrid.html', takes_context=True)
def datagrid(context, **kwargs):
    def get_id():
        return kwargs.get('id', 'datagrid-' + str(uuid4()))

    def get_columns():
        columns = parse_kwarg(kwargs, 'columns', [])

        try:
            # Convert dict to dict
            return [{'key': key, 'label': value} for key, value in columns.items()]
        except AttributeError:
            # Convert string to column dict
            if type(columns) == str or type(columns) == SafeText:
                columns = [{'key': columns, 'label': columns}]

            # Convert list to list of dicts
            elif type(columns) == list:
                processed_columns = []
                for column in columns:
                    # Already dict
                    if type(column) == dict:
                        processed_columns.append(column)
                    # Not dict
                    else:
                        processed_columns.append({'key': column, 'label': column})
                columns = processed_columns

            # Get label from model
            for column in columns:
                try:
                    context_queryset = context.get('queryset')
                    queryset = kwargs.get('queryset', context_queryset)
                    model = queryset.model

                    if column['key'] == '__str__':
                        column['label'] = model.__name__
                    else:
                        field = model._meta.get_field(column['key'])
                        column['label'] = field.verbose_name
                except:
                    pass

            return columns

    def get_form_buttons():
        form_actions = parse_kwarg(kwargs, 'form_buttons', {})
        try:
            return [{'name': key, 'label': value} for key, value in form_actions.items()]

        except AttributeError:
            return form_actions

    def get_object_list():
        context_object_list = context.get('object_list', [])
        context_queryset = context.get('queryset', context_object_list)
        object_list = kwargs.get('object_list', context_queryset)
        object_list = kwargs.get('queryset', object_list)

        for obj in object_list:
            add_display(obj)
            add_modifier_class(obj)
        return object_list

    def add_display(obj):
        for column in get_columns():
            key = column['key']
            fn = kwargs.get('get_{}_display'.format(key), None)
            if fn:
                setattr(obj, 'datagrid_display_{}'.format(key), fn(obj))

    def add_modifier_class(obj):
        try:
            key = parse_kwarg(kwargs, 'modifier_key', None)

            if not key:
                return

            modifier_map = parse_kwarg(kwargs, 'modifier_mapping', {})
            object_value = getattr(obj, key)

            for item_key, item_value in modifier_map.items():
                pattern = re.compile(item_key)
                if pattern.match(object_value):
                    obj.datagrid_modifier_class = item_value
        except KeyError:
            pass

    def get_modifier_column():
        return kwargs.get('modifier_column', kwargs.get('modifier_key', False))

    def get_orderable_column_keys():
        orderable_columns = parse_kwarg(kwargs, 'orderable_columns', {})
        try:
            return [key for key in orderable_columns.keys()]
        except AttributeError:
            return []

    def get_ordering():
        request = context['request']
        orderable_columns = parse_kwarg(kwargs, 'orderable_columns', {})
        order_by_index = kwargs.get('order_by_index', False)
        ordering = {}

        try:
            i = 1
            for orderable_column_key, orderable_column_field in orderable_columns.items():
                querydict = QueryDict(request.GET.urlencode(), mutable=True)
                ordering_key = parse_kwarg(kwargs, 'ordering_key', 'ordering')
                ordering_value = str(i) if order_by_index else orderable_column_field
                current_ordering = querydict.get(ordering_key, False)

                directions = {
                    'asc': ordering_value,
                    'desc': '-' + ordering_value
                }

                direction_url = directions['asc']
                direction = None

                if current_ordering == directions['asc']:
                    direction = 'asc'
                    direction_url = directions['desc']
                elif current_ordering == directions['desc']:
                    direction = 'desc'
                    direction_url = directions['asc']

                querydict[ordering_key] = direction_url
                ordering[orderable_column_key] = {
                    'direction': direction,
                    'url': '?' + querydict.urlencode()
                }

                i += 1
        except AttributeError:
            pass

        return ordering

    def add_paginator(ctx):
        paginator_ctx = ctx.copy()
        paginator_ctx['is_paginated'] = kwargs.get('is_paginated', context.get('is_paginated'))

        if paginator_ctx['is_paginated']:
            paginator_ctx['paginator'] = kwargs.get('paginator', context.get('paginator'))
            paginator_ctx['paginator_zero_index'] = kwargs.get('paginator_zero_index')
            paginator_ctx['page_key'] = kwargs.get('page_key', 'page')
            paginator_ctx['page_number'] = kwargs.get('page_number')
            paginator_ctx['page_obj'] = kwargs.get('page_obj', context.get('page_obj'))
            return paginator_ctx
        return paginator_ctx

    kwargs = merge_config(kwargs)
    ctx = kwargs.copy()

    # i18n
    ctx['label_result_count'] = parse_kwarg(kwargs, 'label_result_count', _('resultaten'))
    ctx['label_no_results'] = parse_kwarg(kwargs, 'label_no_results', _('Geen resultaten'))

    # kwargs
    ctx['class'] = kwargs.get('class', None)
    ctx['columns'] = get_columns()
    ctx['orderable_column_keys'] = get_orderable_column_keys()
    ctx['form_action'] = parse_kwarg(kwargs, 'form_action', '')
    ctx['form_buttons'] = get_form_buttons()
    ctx['form_checkbox_name'] = kwargs.get('form_checkbox_name', 'objects')
    ctx['form'] = parse_kwarg(kwargs, 'form', False) or bool(kwargs.get('form_action')) or bool(
        kwargs.get('form_buttons'))
    ctx['id'] = get_id()
    ctx['modifier_column'] = get_modifier_column()
    ctx['object_list'] = get_object_list()
    ctx['ordering'] = get_ordering()
    ctx['urlize'] = kwargs.get('urlize', True)
    ctx['title'] = kwargs.get('title', None)
    ctx['toolbar_position'] = kwargs.get('toolbar_position', 'top')
    ctx['url_reverse'] = kwargs.get('url_reverse', '')
    ctx['request'] = context['request']
    ctx = add_paginator(ctx)

    ctx['config'] = kwargs
    return ctx


@register.filter
def datagrid_label(obj, column_key):
    """
    Formats field in datagrid, supporting get_<column_key>_display() and and date_format().
    :param obj: (Model) Object containing key column_key.
    :param column_key key of field to get label for.
    :return: Formatted string.
    """
    try:
        return getattr(obj, 'datagrid_display_{}'.format(column_key))
    except:
        if column_key == '__str__':
            return str(obj)
        try:
            value = getattr(obj, column_key)
            return formats.date_format(value)
        except (AttributeError, TypeError):
            try:
                val = get_attr(obj, column_key)
                if val:
                    return val
            except:
                pass
            return obj


@register.inclusion_tag('rijkshuisstijl/components/footer/footer.html', takes_context=True)
def footer(context, **kwargs):
    kwargs = merge_config(kwargs)
    kwargs['request'] = context['request']

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/header/header.html')
def header(**kwargs):
    kwargs = merge_config(kwargs)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/icon/icon.html')
def icon(icon, **kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['href'] = kwargs.get('href', None)
    kwargs['icon'] = kwargs.get('icon', None)
    kwargs['label'] = kwargs.get('label', None)

    # args
    kwargs['icon'] = icon

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/image/image.html')
def image(**kwargs):
    kwargs = merge_config(kwargs)
    kwargs['alt'] = kwargs.get('alt', '')
    kwargs['class'] = kwargs.get('class', None)
    kwargs['href'] = kwargs.get('href', '')
    kwargs['object_fit'] = kwargs.get('object_fit', False)
    kwargs['src'] = kwargs.get('src', '')
    kwargs['mobile_src'] = kwargs.get('mobile_src', None)
    kwargs['tablet_src'] = kwargs.get('tablet_src', None)
    kwargs['laptop_src'] = kwargs.get('laptop_src', None)
    kwargs['width'] = kwargs.get('width', None)
    kwargs['height'] = kwargs.get('height', None)
    kwargs['hide_on_error'] = kwargs.get('hide_on_error', False)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/key-value-table/key-value-table.html')
def key_value_table(**kwargs):
    kwargs = merge_config(kwargs)

    def get_fields():
        fields = parse_kwarg(kwargs, 'fields', {})
        # from pdb import set_trace
        # set_trace()

        try:
            return [{'key': key, 'label': value} for key, value in fields.items()]
        except AttributeError:
            return [{'key': fields, 'label': fields} for fields in fields]

    def get_data():
        obj = kwargs.get('object')
        fields = get_fields()

        data = []
        if obj and fields:
            data = [(field.get('label'), getattr(obj, field.get('key'))) for field in fields]

        data = data + parse_kwarg(kwargs, 'data', [])
        return data

    # kwargs
    kwargs['data'] = get_data()

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/login-bar/login-bar.html', takes_context=True)
def login_bar(context, **kwargs):
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_login'] = kwargs.get('label_login', _('Inloggen'))
    kwargs['label_logged_in_as'] = kwargs.get('label_logged_in_as', _('Ingelogd als'))
    kwargs['label_logout'] = kwargs.get('label_logout', _('Uitloggen'))
    kwargs['label_request_account'] = kwargs.get('label_request_account', _('Account aanvragen'))

    # kwargs
    kwargs['details_url'] = kwargs.get('details_url', '#')
    kwargs['logout_url'] = kwargs.get('logout_url', '#')
    kwargs['login_url'] = kwargs.get('login_url', '#')
    kwargs['registration_url'] = kwargs.get('registration_url', '#')
    kwargs['request'] = context['request']

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/logo/logo.html')
def logo(**kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['alt'] = kwargs.get('alt', _('Logo Rijksoverheid'))
    kwargs['src'] = kwargs.get('src', static('rijkshuisstijl/components/logo/logo-tablet.svg'))
    kwargs['mobile_src'] = kwargs.get('mobile_src', static('rijkshuisstijl/components/logo/logo-mobile.svg'))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-css.html')
def meta_css(**kwargs):
    kwargs = merge_config(kwargs)
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-js.html')
def meta_js(**kwargs):
    kwargs = merge_config(kwargs)
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/meta/meta-icons.html')
def meta_icons(**kwargs):
    kwargs = merge_config(kwargs)
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/navigation-bar/navigation-bar.html', takes_context=True)
def navigation_bar(context, **kwargs):
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_login'] = kwargs.get('label_login', _('Inloggen'))
    kwargs['label_logged_in_as'] = kwargs.get('label_logged_in_as', _('Ingelogd als'))
    kwargs['label_logout'] = kwargs.get('label_logout', _('Uitloggen'))
    kwargs['label_request_account'] = kwargs.get('label_request_account', _('Account aanvragen'))

    # kwargs
    kwargs['details_url'] = kwargs.get('details_url', '#')
    kwargs['logout_url'] = kwargs.get('logout_url', '#')
    kwargs['login_url'] = kwargs.get('login_url', '#')
    kwargs['registration_url'] = kwargs.get('registration_url', '#')
    kwargs['search_url'] = kwargs.get('search_url', None)
    kwargs['search_method'] = kwargs.get('search_method', 'get')
    kwargs['search_name'] = kwargs.get('search_name', 'q')
    kwargs['request'] = context['request']

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/paginator/paginator.html', takes_context=True)
def paginator(context, **kwargs):
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


@register.inclusion_tag('rijkshuisstijl/components/search/search.html', takes_context=True)
def search(context, **kwargs):
    kwargs = merge_config(kwargs)
    request = context['request']

    # kwargs
    kwargs['action'] = kwargs.get('action', '')
    kwargs['class'] = kwargs.get('class', None)
    kwargs['method'] = kwargs.get('method', 'GET')
    kwargs['name'] = kwargs.get('name', 'query')
    kwargs['placeholder'] = kwargs.get('placholder', _('Zoeken'))
    request_dict = getattr(request, kwargs['method'], {})
    kwargs['value'] = request_dict.get(kwargs['name'], '')
    kwargs['request'] = context['request']

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink.html')
def skiplink(**kwargs):
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_to_content'] = parse_kwarg(kwargs, 'label_to_content', _('Direct naar de inhoud.'))

    # kwargs
    kwargs['target'] = '#' + kwargs.get('target', 'skiplink-target')

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink-target.html')
def skiplink_target(**kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['id'] = kwargs.get('id', 'skiplink-target')

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/stacked-list/stacked-list.html')
def stacked_list(*args, **kwargs):
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
        item = {'label': get_attr(obj, field)}

        if url_field:
            item['url'] = get_attr(obj, url_field)

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


@register.inclusion_tag('rijkshuisstijl/components/toolbar/toolbar.html')
def toolbar(*args, **kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['items'] = kwargs.get('items', [])

    # args
    for arg in args:
        arg_items = arg
        if not hasattr(arg, '__iter__'):
            arg_items = [arg]

        for item in arg_items:
            kwargs['items'].append(parse_arg(item))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/textbox/textbox.html')
def textbox(**kwargs):
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['status'] = kwargs.get('status', None)
    kwargs['title'] = kwargs.get('title', None)
    kwargs['text'] = kwargs.get('text', None)
    kwargs['wysiwyg'] = kwargs.get('wysiwyg')
    kwargs['urlize'] = kwargs.get('urlize', True)

    kwargs['config'] = kwargs
    return kwargs


def merge_config(kwargs):
    """
    Merges "config" and other items in kwarg to generate configuration dict.
    Other kwargs override items in config.
    :param kwargs: (optional) dict in in kwargs mirroring other kwargs.
    :return: A merged dict containing configuration.
    """
    config = kwargs.pop('config', {})
    _kwargs = config.copy()
    _kwargs.update(kwargs)
    kwargs = _kwargs

    return kwargs


def parse_arg(arg, default=None):
    """
    Parses an argument (or value in kwargs)

    Syntax::

        Comma separated:
        - dict (Key value): "foo:bar,bar:baz" -> {'foo': 'bar', 'bar: 'baz')
        - list: "foo,bar,baz" -> ['foo, 'bar', baz']
        - string: "foo": "foo"

        JSON:
        - "[{"foo": "bar"}, {"bar": "baz"}]" -> [{'foo': 'bar'}, {'bar: 'baz')]

        Edge case:
        Given a dict as default ({}) list is converted into matching pair dict:
        - parse_arg("foo,bar,baz", {}) -> {'foo': 'foo', 'bar': 'bar', 'baz': 'baz}

        Given None returns default:
        - None -> default

        Given a non-string arg returns value directly.
        - True -> True

    :param arg: The input value to parse.
    :param default: Returned when arg is None.
    :return: The parsed arg.
    """
    if arg is None:
        return default

    if type(arg) != str and type(arg) != SafeText:
        return arg

    if ',' in arg or ':' in arg:
        try:
            return json.loads(arg)
        except JSONDecodeError:
            pass

        lst = [entry.strip() for entry in arg.strip().split(',') if entry]

        if ':' in arg or isinstance(default, dict):
            dct = {}
            for value in lst:
                try:
                    key, val = value.split(':')
                except ValueError:
                    key = value
                    val = value
                dct[key] = val or key
            return dct
        return lst
    return arg


def parse_kwarg(kwargs, name, default=None):
    """
    Parses value of name of kwargs.
    See parse_arg for syntax of value.

    :param kwargs:  Dict containing key name.
    :param name: The key in kwargs to parse.
    :param default: The default value if the kwargs[name] is None.
    :return: The parsed value of kwargs[name].
    """
    value = kwargs.get(name, default)
    return parse_arg(value, default)
