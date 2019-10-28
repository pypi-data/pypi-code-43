import re
from uuid import uuid4

from django.http import QueryDict
from django.utils import formats
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.templatetags.rijkshuisstijl import register
from .rijkshuisstijl_filters import get_attr_or_get
from .rijkshuisstijl_helpers import merge_config, parse_kwarg, get_field_label, get_recursed_field_value


@register.inclusion_tag('rijkshuisstijl/components/datagrid/datagrid.html', takes_context=True)
def datagrid(context, **kwargs):
    """
    Renders a table like component with support for filtering, ordering* and  paginating**. It's main use if to display
    data from a listview.
   *The actual ordering is not implemented in the datagrid itself and should be provided by the view.
   **The actual pagination is not implemented in the datagrid itself and should be provided by the view.

    Example:

        {% datagrid config=config %}
        {% datagrid option1='foo' option2='bar' %}

    Available options
    =================

        Showing data
        ------------

        Data is shown based on a internal "object" list which can be populated by either a "queryset" or an
        "object_list option. Columns are specified by a "columns" option which may define an additional label to show in
        the table header. Columns match fields in the objects in the internal object_list.

        - object_list: Optional, A list containing the object_list*** to show. if possible, use queryset instead.
          ***The internally used object_list is obtained by looking for these values in order:

            1) kwargs['queryset']
            2) kwargs['object_list']
            3) context['queryset']
            4) context['object_list']

        - queryset: Optional, A queryset containing the objects to show.

        - columns: Required, a dict or a list defining which columns/values to show for each object in object_list or
          queryset.

            - If a dict is passed, each key will represent a field in an object to obtain the data from and each value
              will represent the label to use for the column heading.
              Example: {'author': 'Written by', 'title': 'Title'}

            - If a list is passed, each item will represent a field in an object to obtain the data from and will also
              represent the label to use for the column heading.
              Example: ['author', 'title']


        Pagination
        ----------

        Data my be paginated using a Django paginator. Pagination detais may be obtained from the context if not
        explicitly set.
        **The actual pagination is not implemented in the datagrid itself and should be provided by the view.

        - paginator: Optional, A Django Paginator instance, may be obtained from context.
        - page_obj: Optional, The paginator page object, may be obtained from context.
        - page_number: Optional, The current page number.
        - page_key: Optional, The GET parameter to use for the page, defaults to 'page'.
        - paginator_zero_index: Optional, Use zero-based indexing for page numbers, not fully supported.


        Ordering
        --------

        An interface for ordering can be creating by defining the fields that should be made orderable. Orderable
        columns are specified by the "orderable_columns" option which may define a field lookup which defaults to the
        field. Inverted field lookups are proceeded with a dash "-" character and set to the GET parameter specified by
        the "ordering_key" setting.
        *The actual ordering is not implemented in the datagrid itself and should be provided by the view.

        - orderable_columns: Optional, a dict or a list defining which columns should be orderable.

            - If a dict is passed each key will map to a field (the key) in columns, each value will be used to describe
              a field lookup.
              Example: {"author": "author__first_name"}

            - If a list is passed each value will map to a field (the key) in columns and will also be used to describe
              a field lookup
              Example: ['author', 'title']

        - ordering: Optional, represents the field on which the object_list/queryset should be ordered.
          Example: "author__first_name" or "-author__first_name"
          *The actual ordering is not implemented in the datagrid itself and should be provided by the view.

        - ordering_key: Optional, describes which GET parameter should be used in hyperlinks (set on the table captions)
          to indicate which order the view should provide, defaults to "ordering".
          *The actual ordering is not implemented in the datagrid itself and should be provided by the view.


        Custom presentation (get_<field>_display)
        -----------------------------------------

        - get_<field>_display: Optional, allows a callable to be used to generate a custom cell display value. Replace
         <field> with a key which will map to a field (a key in columns) and set a callable as it's value.

         The callable will receive the row's object and shoud return SafeText.
         Example: lambda object: mark_safe(<a href="{}">{}</a>.format(object.author.get_absolute_url, object.author))


        Manipulating data (form)
        ------------------------

        A form can be generated POSTing data to the url specified by the "form_action" option. When a form is active
        each row gets a checkbox input with a name specified by the "form_checkbox_name" option. Various actions can be
        defined by the "form_buttons" option which are placed either in the top, bottom or at both position based on the
        value of the "toolbar_postion" option.

        - form: Optional, if true, adds a form to the datagrid, useful for allowing user manipulations on the dataset.
          Defaults to false, unless "form_action" or "form_buttons" is set.

        - form_action: Optional, specifies the url to submit form actions to. If set, form will default to True.

        - form_buttons: Optional, a list_of_dict (label, [href], [icon], [name], [target], [title]) defining which
          buttons to create (see rijkshuisstijl_form.button). The name attribute of the buttons should be used to
          specify the performed action.
          example: [{'name': 'delete', 'label': 'delete' 'class': 'button--danger'}]

        - toolbar_position: Optional, can be set to one of "top", "bottom", or "both" indicating the position of the
          toolbar containing the buttons specified by form_buttons.

        - form_checkbox_name: Optional, specifies the name for each checkbox input for an object in the table. This
          should be used for determining which objects should be manipulated by the performed action.


        Color coded rows
        ----------------

        Rows can be configured to show a color coded border and a colored cell value based on the value of a certain
        field. The field to look for is defined by the "modifier_key" option if this is any different than the column
        key it should color the cell for, the column can be specified by the "modifier_column" options. This defaults
        to the value of the "modifier_key" option. The field value is matched against a mapping (specified by the
        "modifier_mapping" options) to define the color. The value should contain the value in the mapping.

        - modifier_key Optional, a string defining the field in an object to get the value to match for.
        - modifier_column Optional, a string defining the column key to apply the colored styling for.
        - modifier_mapping, a dict containing a key which possibly partially matches an object's field value and which
          value is one of the supported colors****.
          Example: [{'1984': 'purple'}]

        The supported colors are:

         - purple
         - purple-shade-1
         - purple-shade-2
         - violet
         - violet-shade-1
         - violet-shade-2
         - ruby
         - ruby-shade-1
         - ruby-shade-2
         - pink
         - pink-shade-1
         - pink-shade-2
         - red
         - red-shade-1
         - red-shade-2
         - orange
         - orange-shade-1
         - orange-shade-2
         - dark-yellow
         - dark-yellow-shade-1
         - dark-yellow-shade-2
         - yellow
         - yellow-shade-1
         - yellow-shade-2
         - dark-brown
         - dark-brown-shade-1
         - dark-brown-shade-2
         - brown
         - brown-shade-1
         - brown-shade-2
         - dark-green
         - dark-green-shade-1
         - dark-green-shade-2
         - green
         - green-shade-1
         - green-shade-2
         - moss-green
         - moss-green-shade-1
         - moss-green-shade-2
         - mint-green
         - mint-green-shade-1
         - mint-green-shade-2
         - dark-blue
         - dark-blue-shade-1
         - dark-blue-shade-2
         - heaven-blue
         - heaven-blue-shade-1
         - heaven-blue-shade-2
         - light-blue
         - light-blue-shade-1
         - light-blue-shade-2


        Additional options
        ------------------

        - class: Optional, a string with additional CSS classes.
        - id: Optional, a string specifying the datagrid id, defaults to a generated uuid4 string.
        - urlize: Optional, if True (default) cell values are passed to "urlize" template filter, automatically creating
          hyperlinks if applicable in every cell.
        - title: Optional, if set, a title will be shown above the datagrid.
        - url_reverse: Optional, A URL name to reverse using the object's 'pk' attribute as one and only attribute,
          creates hyperlinks in the first cell. If no url_reverse if passed get_absolute_url is tried in order to find
          a url.

    :param context:
    :param kwargs:
    """

    def get_id():
        """
        Gets the id to put on the datagrid based on kwargs["id'}, if no id is provided a uuid4 is created and prefixed
        with "datagrid-".
        :return: A str which should be unique to this datagrid.
        """
        return kwargs.get('id', 'datagrid-' + str(uuid4()))

    def get_columns():
        """
        Gets the columns to show based on kwargs['columns']. If no label is provided an attempt is made to create it
        based on the model or a simple replacement of dashes and underscores.
        :return: A list_of_dict where each dict contains "key" and "label" keys.
        """
        columns = parse_kwarg(kwargs, 'columns', [])

        try:
            # Convert dict to list_of_dict.
            return [{'key': key, 'label': value} for key, value in columns.items()]
        except AttributeError:
            # Convert string to list_of_dict.
            if type(columns) == str or type(columns) == SafeText:
                columns = [{'key': columns, 'label': columns}]

            # Convert list to list_of_dict.
            elif type(columns) is list or type(columns) is tuple:
                processed_columns = []
                for column in columns:
                    # Already dict
                    if type(column) == dict:
                        processed_columns.append(column)
                    # Not dict
                    else:
                        processed_columns.append({'key': column, 'label': column})
                columns = processed_columns

            # Get column label.
            for column in columns:
                context_queryset = context.get('queryset')
                queryset = kwargs.get('queryset', context_queryset)

                column['label'] = get_field_label(queryset, column['label'])
            return columns

    def get_form_buttons():
        """
        Gets the buttons to use for the form based on kwargs['form_buttons'].
        :return: A list_of_dict where each dict contains at least "name" and "label" keys.
        """
        form_actions = parse_kwarg(kwargs, 'form_buttons', {})

        # Convert dict to list_of_dict
        try:
            return [{'name': key, 'label': value} for key, value in form_actions.items()]
        except AttributeError:
            return form_actions

    def get_object_list():
        """
        Looks for the object_list to use based on the presence of these variables in order:

            1) kwargs['queryset']
            2) kwargs['object_list']
            3) context['queryset']
            4) context['object_list']

        add_display and add_modifier_class() are called for every object in the found object_list.
        :return: A list of objects to show data for.
        """
        context_object_list = context.get('object_list', [])
        context_queryset = context.get('queryset', context_object_list)
        object_list = kwargs.get('object_list', context_queryset)
        object_list = kwargs.get('queryset', object_list)

        for obj in object_list:
            add_display(obj)
            add_modifier_class(obj)
        return object_list

    def add_display(obj):
        """
        If a get_<field>_display callable is set, add the evaluated result to the datagrid_display_<field> field on the
        object passed to obj.
        :param obj:
        """
        for column in get_columns():
            key = column['key']
            fn = kwargs.get('get_{}_display'.format(key), None)
            if fn:
                setattr(obj, 'datagrid_display_{}'.format(key), fn(obj))

    def add_modifier_class(obj):
        """
        If a modifier configuration is set, add the result color as datagrid_modifier_class to the object passed to
        obj.
        :param obj:
        """
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
        """
        Returns the key of the column to colorize the value of is a modifier configuration is set. Defaults to hte value
        of the modifier_key option.
        :return: A string othe modifier column or False.
        """
        return kwargs.get('modifier_column', kwargs.get('modifier_key', False))

    def get_orderable_column_keys():
        """
        Returns the keys of the fields which should be made orderable.
        :return: list_of_str
        """
        orderable_columns = parse_kwarg(kwargs, 'orderable_columns', {})
        try:
            return [key for key in orderable_columns.keys()]
        except AttributeError:
            return orderable_columns

    def get_ordering():
        """
        Returns a dict containing ordering information for every orderable column
        :return: dict
        """
        request = context['request']
        orderable_columns = parse_kwarg(kwargs, 'orderable_columns', {})
        order_by_index = kwargs.get('order_by_index', False)
        ordering = {}

        # Convert list to list_of_dict.
        if type(orderable_columns) is list or type(orderable_columns) is tuple:
            orderable_columns = {column: column for column in orderable_columns}

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
        """
        Return ctx with added paginator configuration.
        :param ctx: A processed clone of kwargs.
        """
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
            val = get_attr_or_get(obj, column_key)
            return formats.date_format(val)
        except (AttributeError, TypeError):
            try:
                if type(obj) is list:
                    val = obj.get(column_key)
                else:
                    val = get_recursed_field_value(obj, column_key)
                if val:
                    return val
            except:
                pass
            return obj
