from collections import OrderedDict, defaultdict

from rest_framework.metadata import SimpleMetadata

from redmin.models import Field, Choice
from redmin.utils import attr


class RedminMetadata(SimpleMetadata):

    def determine_metadata(self, request, view):
        metadata = OrderedDict()
        metadata['name'] = view.get_view_name()
        metadata['description'] = view.get_view_description()
        metadata['renders'] = [renderer.media_type for renderer in view.renderer_classes]
        metadata['parses'] = [parser.media_type for parser in view.parser_classes]

        model = attr(view, "model")
        if model:
            fields = []
            choices = defaultdict(list)
            for choice in Choice.objects.filter(field__base__app=model.__module__.split(".")[0], field__base__name=model.__name__):
                choices[choice.field.attribute].append(OrderedDict(title=choice.title, value=choice.value))
            for field in Field.get_default_fields(view.model).values():
                if field.serializable and "." not in field.attribute:
                    attributes = OrderedDict(
                        name=field.attribute,
                        type=field.data_type,
                        label=field.title,
                        required=not field.nullable,
                        default=field.default,
                        sortable=field.sortable,
                        searchable=field.searchable,
                        description=field.help_text,
                        maxLength=field.max_length,
                        readOnly=not field.form_editable
                    )
                    field_choices = choices.get(field.attribute, None)
                    if field_choices:
                        attributes["choices"] = field_choices
                    fields.append(attributes)
            metadata['fields'] = fields
        return {"schema": metadata}
