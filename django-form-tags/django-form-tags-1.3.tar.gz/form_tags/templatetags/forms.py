import re

from django import template
from django.forms import widgets
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from svg_templatetag.templatetags.svg import get_svg

from ..conf import settings


register = template.Library()

TEXT_INPUT_WIDGETS = (
    widgets.TextInput, widgets.NumberInput, widgets.EmailInput,
    widgets.URLInput, widgets.PasswordInput
)

FIELD_HOLDER = '''
    <div class="fieldholder {fieldholder_class}">
        {label}
        {field}
    </div>'''

FIELD_HOLDER_INLINE = '''
    <td class="table__cell table__cell--inline-edit {fieldholder_class}">
        {field}
    </td>'''

FIELD_WRAPPER = '''
    <div class="fieldwrapper fieldwrapper--{field_type} fieldwrapper--{widget_type} {fieldwrapper_class}">
        {before_field}
        {field}
        {after_field}
        {help_text}
        {errors}
    </div>'''  # noqa

FIELD_WRAPPER_SELECT = FIELD_WRAPPER.replace(
        '{field}',
        '<div class="select">{field}</div>'
    )

FIELD_WRAPPER_CHECKBOX = FIELD_WRAPPER.replace(
        '{field}',
        '''<label class="control checkbox">
            {field}
            <span class="control-indicator"></span>
            <span class="control-label">{control_label}</span>
         </label>'''
    )

COMBINED_FIELD_WRAPPER = '''
    <div class="fieldwrapper {fieldwrapper_class}">
        <div class="fieldwrapper-combined">
            {fields}
        </div>
        {help_text}
        {errors}
    </div>'''

COMBINED_FIELD = '''
    <div class="fieldwrapper-combined__field fieldwrapper--{field_type} fieldwrapper--{widget_type} {fieldwrapper_class}">
       {before_field}
       {field}
       {after_field}
    </div>'''  # noqa

INLINE_VALIDATION = '''
    <div class="inline-validation inline-validation--error">
        {errors}
    </div>'''

BUTTON_PASSWORD = format_html(
    '''<button class="input-icon input-icon__password" type="button" tabindex="-1">
        {icon}
    </button>''',  # noqa
    icon=get_svg(
        'form_tags/icon_eye.svg',
        **{'class': 'icn icn--ic-24 icn--ic-remove-red-eye'}
    ))

LABEL_INLINE_EDIT = format_html(
    '''<label class="label--inline-edit" for="{{for}}" title="{{title}}">
        {icon}
    </label>''',
    icon=get_svg(
        'form_tags/icon_edit.svg',
        **{'class': 'icn icn--ic-24 icn--ic-edit'}
    ))

LABEL_INLINE_EDIT_DATE = format_html(
    '''<label class="label--inline-edit" for="{{for}}" title="{{title}}">
        {icon}
    </label>''',
    icon=get_svg(
        'form_tags/icon_date_range.svg',
        **{'class': 'icn icn--ic-24 icn--ic-date-range'}
    ))


def _add_error_class(classes, field, suppress_errors):
    classes = (classes or '').strip()
    if not suppress_errors and len(field.errors):
        return (classes + ' error').strip()
    return classes


def _help_text(help_text):
    if help_text:
        return format_html(
            '<div class="helptext">{}</div>', help_text)
    return help_text or ''


def _get_field_kwargs(k, **kwargs):
    regex = re.compile(r'field{}_'.format(k))
    return {regex.sub('', key): value
            for key, value in kwargs.items() if regex.match(key)}


def _unit_text(left, right, fieldwrapper_class=''):
    format_kwargs = {}
    if 'fieldwrapper--icon' not in fieldwrapper_class:
        fieldwrapper_class = fieldwrapper_class.strip()
        # left unit icon
        if left:
            format_kwargs['fieldwrapper_class'] = ('fieldwrapper--unit ' + fieldwrapper_class).strip()  # noqa
            format_kwargs['before_field'] = format_html(
                '<i class="input-unit input-unit--left">{}</i>\n', left)
        # right unit icon
        if right:
            format_kwargs['fieldwrapper_class'] = ('fieldwrapper--unit ' + fieldwrapper_class).strip()  # noqa
            format_kwargs['after_field'] = format_html(
                '<i class="input-unit input-unit--right">{}</i>\n', right)
    return format_kwargs


@register.simple_tag
def hidden_fields(form):
    return mark_safe('\n'.join(
        [field.as_widget() for field in form.hidden_fields()]
    ))


@register.simple_tag
def non_field_errors(form):
    if len(form.non_field_errors()):
        return format_html(
            INLINE_VALIDATION, errors=mark_safe(form.non_field_errors()))
    return ''


@register.simple_tag
def non_form_errors(formset):
    if len(formset.non_form_errors()):
        return format_html(
            INLINE_VALIDATION, errors=mark_safe(formset.non_form_errors()))
    return ''


@register.simple_tag(name='field')
def field_tag(field, suppress_errors=False, **kwargs):
    if isinstance(field.field.widget, TEXT_INPUT_WIDGETS):
        kwargs.update({
            'class': ('input-field ' + kwargs.get('class', '').strip()).strip()
        })
    classes = _add_error_class(kwargs.get('class', ''), field, suppress_errors)

    kwargs['class'] = (
        field.field.widget.attrs.get('class', '') + ' ' + classes).strip()

    for attr in settings.FIELD_BOOLEAN_ATTRS:
        if attr in kwargs:
            if not kwargs[attr]:
                kwargs.pop(attr)
            else:
                kwargs[attr] = attr

    if "name" in kwargs:
        html_name = kwargs.pop("name")
        render = field.field.widget.render
        field.field.widget.render = lambda name, *args, **kwargs: \
            render(html_name, *args, **kwargs)

    attrs = {k.replace('_', '-'): v for k, v, in kwargs.items()}
    return field.as_widget(attrs=attrs)


@register.simple_tag
def fieldwrapper(field, fieldwrapper_class='', before_field='', after_field='',
                 control_label=None, unit_text_left='', unit_text_right='',
                 **kwargs):
    suppress_errors = kwargs.get('suppress_errors', False)
    classes = _add_error_class(fieldwrapper_class, field, suppress_errors)

    format_kwargs = {
        'fieldwrapper_class': classes,
        'field_type': field.field.__class__.__name__.lower(),
        'widget_type': field.field.widget.__class__.__name__.lower(),
        'before_field': before_field,
        'after_field': after_field,
        'errors': mark_safe(field.errors) if not suppress_errors else '',
        'help_text': _help_text(field.help_text)
    }

    if isinstance(field.field.widget, widgets.Select) and \
            not isinstance(field.field.widget, widgets.RadioSelect):
        field_wrapper = FIELD_WRAPPER_SELECT
    elif isinstance(field.field.widget, widgets.CheckboxInput):
        field_wrapper = FIELD_WRAPPER_CHECKBOX
        if control_label is not None:
            format_kwargs['control_label'] = control_label
        elif field.help_text:
            format_kwargs['control_label'] = field.help_text
            format_kwargs['help_text'] = ''
        else:
            format_kwargs['control_label'] = field.label
    elif isinstance(field.field.widget, widgets.PasswordInput):
        field_wrapper = FIELD_WRAPPER
        format_kwargs['fieldwrapper_class'] = ('fieldwrapper--icon ' + format_kwargs.get('fieldwrapper_class', '')).strip()  # noqa
        format_kwargs['after_field'] = BUTTON_PASSWORD
    elif isinstance(field.field.widget, widgets.DateTimeBaseInput):
        field_wrapper = FIELD_WRAPPER
        format_kwargs['fieldwrapper_class'] = ('fieldwrapper--icon ' + format_kwargs.get('fieldwrapper_class', '')).strip()  # noqa
        format_kwargs['after_field'] = format_html(
            LABEL_INLINE_EDIT_DATE,
            **{
                'for': field.id_for_label,
                'title': _('Edit {}').format(strip_tags(field.label)),
            }
        )
    else:
        field_wrapper = FIELD_WRAPPER

    if isinstance(field.field.widget, TEXT_INPUT_WIDGETS):
        format_kwargs.update(_unit_text(unit_text_left, unit_text_right,
                                        format_kwargs['fieldwrapper_class']))

    if 'input-unit--right' in format_kwargs['after_field']:
        kwargs['class'] = ('input-field--unit-right ' + kwargs.get('class', '')).strip()  # noqa
    if 'input-unit--left' in format_kwargs['before_field']:
        kwargs['class'] = ('input-field--unit-left ' + kwargs.get('class', '')).strip()  # noqa

    format_kwargs['field'] = field_tag(field, **kwargs)

    return format_html(field_wrapper, **format_kwargs)


@register.simple_tag(takes_context=True)
def fieldholder(context, field, fieldholder_class='', horizontal=None,
                label_tag=None, label=None, **kwargs):
    fieldholder_class = fieldholder_class.strip()
    if horizontal is None and context.get('horizontal') or horizontal:
        fieldholder_class = ('fieldholder--horizontal ' + fieldholder_class).strip()  # noqa

    suppress_errors = kwargs['suppress_errors'] = \
        kwargs.get('suppress_errors', context.get('suppress_errors', False))
    classes = _add_error_class(fieldholder_class, field, suppress_errors)

    if label_tag is None and label is not None:
        label_tag = format_html(
            '<label for="{id_for_label}" title="{title_label}">{label}</label>',  # noqa
            id_for_label=field.id_for_label,
            title_label=strip_tags(label),
            label=label
        )

    return format_html(
        FIELD_HOLDER,
        field=fieldwrapper(field, **kwargs),
        label=label_tag if label_tag is not None else field.label_tag(
            attrs={'title': strip_tags(field.label)}),
        fieldholder_class=classes
    )


@register.simple_tag(takes_context=True)
def fieldholder_inline(context, field, fieldholder_class='', label_tag=None,
                       **kwargs):
    kwargs.pop('unit_text_left', None)
    kwargs.pop('unit_text_right', None)
    fieldholder_class = fieldholder_class.strip()

    if isinstance(field.field.widget, widgets.ChoiceWidget):
        kwargs.update({
            'fieldwrapper_class': ('select--inline-edit ' + kwargs.get('fieldwrapper_class', '')).strip(),  # noqa
        })
    elif isinstance(field.field.widget, TEXT_INPUT_WIDGETS):
        kwargs.update({
            'fieldwrapper_class': ('fieldwrapper--inline-edit ' + kwargs.get('fieldwrapper_class', '')).strip(),  # noqa
            'class': ('input-field--inline-edit ' + kwargs.get('class', '')).strip(),  # noqa
            'after_field': format_html(
                LABEL_INLINE_EDIT,
                **{
                    'for': field.id_for_label,
                    'title': _('Edit {}').format(strip_tags(field.label)),
                }
            ) if label_tag is None else label_tag,
            'placeholder': kwargs.get('placeholder', field.label)
        })

    suppress_errors = kwargs['suppress_errors'] = \
        kwargs.get('suppress_errors', context.get('suppress_errors', False))
    classes = _add_error_class(fieldholder_class, field, suppress_errors)

    return format_html(
        FIELD_HOLDER_INLINE,
        field=fieldwrapper(field, **kwargs),
        fieldholder_class=classes
    )


def field_tags(*fields, **kwargs):
    suppress_errors = kwargs.pop('suppress_errors', False)

    def get_format_kwargs():
        for k, field in enumerate(fields):
            field_kwargs = _get_field_kwargs(k, **kwargs)
            before_field = field_kwargs.pop('before_field', '')
            after_field = field_kwargs.pop('after_field', '')
            unit_text_left = field_kwargs.pop('unit_text_left', '')
            unit_text_right = field_kwargs.pop('unit_text_right', '')

            format_kwargs = {
                'fieldwrapper_class': _add_error_class('', field, suppress_errors),  # noqa
                'field_type': field.field.__class__.__name__.lower(),
                'widget_type': field.field.widget.__class__.__name__.lower(),
                'before_field': before_field,
                'after_field': after_field,
            }

            if isinstance(field.field.widget, widgets.ChoiceWidget):
                format_kwargs['fieldwrapper_class'] = ('select ' + format_kwargs.get('fieldwrapper_class', '')).strip()  # noqa
            elif isinstance(field.field.widget, widgets.PasswordInput):
                format_kwargs['fieldwrapper_class'] = ('fieldwrapper--icon ' + format_kwargs.get('fieldwrapper_class', '')).strip()  # noqa
                format_kwargs['after_field'] = BUTTON_PASSWORD
            elif isinstance(field.field.widget, widgets.DateTimeBaseInput):
                format_kwargs['fieldwrapper_class'] = ('fieldwrapper--icon ' + format_kwargs.get('fieldwrapper_class', '')).strip()  # noqa
                format_kwargs['after_field'] = format_html(
                    LABEL_INLINE_EDIT_DATE,
                    **{
                        'for': field.id_for_label,
                        'title': _('Edit {}').format(strip_tags(field.label)),
                    }
                )

            if isinstance(field.field.widget, TEXT_INPUT_WIDGETS) and \
                    'placeholder' not in field.field.widget.attrs:
                field_kwargs['placeholder'] = \
                    field_kwargs.get('placeholder', field.label)

                format_kwargs.update(_unit_text(
                    unit_text_left, unit_text_right,
                    format_kwargs['fieldwrapper_class']))

            if 'input-unit--right' in format_kwargs['after_field']:
                field_kwargs['class'] = ('input-field--unit-right ' + field_kwargs.get('class', '')).strip()  # noqa
            if 'input-unit--left' in format_kwargs['before_field']:
                field_kwargs['class'] = ('input-field--unit-left ' + field_kwargs.get('class', '')).strip()  # noqa

            format_kwargs['field'] = field_tag(
                field, suppress_errors=suppress_errors, **field_kwargs)

            yield format_kwargs

    return mark_safe('\n'.join(format_html(COMBINED_FIELD, **fkwargs)
                               for fkwargs in get_format_kwargs()))


@register.simple_tag
def fieldwrapper_combined(*fields, **kwargs):
    suppress_errors = kwargs.get('suppress_errors', False)

    format_kwargs = {
        'fieldwrapper_class': kwargs.pop('fieldwrapper_class', '').strip(),
        'fields': field_tags(*fields, **kwargs),
        'errors': (mark_safe('\n'.join([str(x.errors) for x in fields]))
                   if not suppress_errors else ''),
        'help_text':
            mark_safe('\n'.join([_help_text(x.help_text) for x in fields]))
    }

    return format_html(COMBINED_FIELD_WRAPPER, **format_kwargs)


@register.simple_tag(takes_context=True)
def fieldholder_combined(context, *fields, **kwargs):
    fieldholder_class = kwargs.pop('fieldholder_class', '').strip()
    horizontal = kwargs.pop('horizontal', None)
    label_tag = kwargs.pop('label_tag', None)
    label = kwargs.pop('label', None)

    if horizontal is None and context.get('horizontal') or horizontal:
        fieldholder_class = ('fieldholder--horizontal ' + fieldholder_class).strip()  # noqa

    kwargs['suppress_errors'] = \
        kwargs.get('suppress_errors', context.get('suppress_errors', False))

    if label_tag is None and label is not None:
        label_tag = format_html(
            '<label for="{id_for_label}" title="{title_label}">{label}</label>',  # noqa
            id_for_label=fields[0].id_for_label,
            title_label=strip_tags(label),
            label=label
        )

    return format_html(
        FIELD_HOLDER,
        field=fieldwrapper_combined(*fields, **kwargs),
        label=label_tag if label_tag is not None else fields[0].label_tag(
            attrs={'title': strip_tags(fields[0].label)}),
        fieldholder_class=fieldholder_class
    )
