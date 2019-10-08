from rest_framework import serializers
from collections import Mapping, OrderedDict
from rest_framework.relations import Hyperlink, PKOnlyObject
from rest_framework.fields import SkipField
from decimal import Decimal

from .utils import calculate, replacer, get_operations


class DynamicFieldSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(DynamicFieldSerializer, self).__init__(*args, **kwargs)
        fields = self.context.get("fields")
        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            # initial_data may not be a valid type
            if not isinstance(self.initial_data, Mapping):
                return OrderedDict()

            if self.context.get("fields"):
                return_list = list()
                fields = self.context["fields"]
                for fname in fields:
                    for field_name, field in self.fields.items():
                        if (field.get_value(self.initial_data) is not empty) \
                            and not field.read_only \
                            and field.field_name == fname:
                            return_list.append((field_name, field.get_value(self.initial_data)))
                return OrderedDict(return_list)
            return OrderedDict([
                (field_name, field.get_value(self.initial_data))
                for field_name, field in self.fields.items()
                if (field.get_value(self.initial_data) is not empty) and
                not field.read_only
            ])
        if self.context.get("fields"):
            return_list = list()
            fields = self.context["fields"]
            for fname in fields:
                for field in self.fields.values():
                    if not field.read_only and field.field_name == fname:
                        return_list.append((field.field_name, field.get_initial()))
            return OrderedDict(return_list)
        else:
            return OrderedDict([
                (field.field_name, field.get_initial())
                for field in self.fields.values()
                if not field.read_only
            ])

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        if self.context.get("fields"):
            flds = self.context.get("fields")
            for fname in flds:
                for field in fields:
                    if fname == field.field_name:
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
        else:
            for field in fields:
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
        if self.context.get("calculation"):
            calc = get_operations(self.context.get("calculation"))
            for name, value in ret.items():
                if name in calc:
                    data = replacer(calc[name], ret)
                    ret[name] = calculate(data)

        return ret