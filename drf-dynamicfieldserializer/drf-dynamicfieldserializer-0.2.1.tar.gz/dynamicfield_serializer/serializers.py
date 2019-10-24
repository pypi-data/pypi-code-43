from rest_framework.serializers import Serializer, ListSerializer, LIST_SERIALIZER_KWARGS
from collections import Mapping, OrderedDict
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField, empty


class DynamicFieldSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('response_fields', [])
        super(DynamicFieldSerializer, self).__init__(*args, **kwargs)
        self.response_fields = fields or self.context.get("response_fields", [])
        if self.response_fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        else:
            self.response_fields = list(self.fields.keys())

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            # initial_data may not be a valid type
            if not isinstance(self.initial_data, Mapping):
                return OrderedDict()

            return_list = []
            fields = self.response_fields
            for return_field in fields:
                field = self.fields.get(return_field)
                if field:
                    if (field.get_value(self.initial_data) is not empty) \
                            and not field.read_only:
                        return_list.append((return_field, field.get_value(self.initial_data)))
            return OrderedDict(return_list) if return_list else OrderedDict([
                (field_name, field.get_value(self.initial_data))
                for field_name, field in self.fields.items()
                if (field.get_value(self.initial_data) is not empty) and not field.read_only
            ])
        else:
            return_list = []
            for return_field in self.response_fields:
                field = self.fields.get(return_field)
                if field and not field.read_only:
                    return_list.append((field.field_name, field.get_initial()))
            return OrderedDict(return_list) if return_list else OrderedDict([
                (field.field_name, field.get_initial())
                for field in self.fields.values()
                if not field.read_only
            ])

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        read_fields = {field.field_name: field for field in self._readable_fields}
        fields = (read_fields[field] for field in self.response_fields if read_fields.get(field))

        for field in fields:
            if field.field_name in self.response_fields:
                try:
                    attribute = field.get_attribute(instance)
                except SkipField:
                    continue

                # We skip `to_representation` for `None` values so that fields do
                # not have to explicitly deal with that case.
                #
                # For related fields with `use_pk_only_optimization` we need to
                # resolve the pk value.
                check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
                if check_for_none is None:
                    ret[field.field_name] = None
                else:
                    ret[field.field_name] = field.to_representation(attribute)
        return ret

    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
        }
        response_fields = kwargs.pop("response_fields", [])
        list_kwargs["context"] = kwargs.pop("context", {})
        list_kwargs["context"]["response_fields"] = response_fields
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', ListSerializer)
        return list_serializer_class(*args, **list_kwargs)
