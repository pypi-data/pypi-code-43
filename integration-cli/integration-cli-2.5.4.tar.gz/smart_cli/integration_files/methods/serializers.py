import validators
from rest_framework import serializers
from .models import CustomAPIMethod, BaseAPIMethod


class BaseAPIMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseAPIMethod
        fields = [
            "id",
            "name",
            "endpoint",
            'is_filter_method',
            'is_data_method',
            "params",
            "definition"
        ]
        extra_kwargs = {
            "id": {"read_only": True, "required": False},
        }

    def validate_definition(self, value):
        if not 'default' or 'change_keys' not in value.keys():
            raise serializers.ValidationError("definition must have 'default' and 'change_keys' in keys")

        return value


class CustomAPIMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAPIMethod
        fields = [
            "id",
            'name',
            'config',
            'definition',
        ]
        extra_kwargs = {
            "id": {"read_only": True, "required": False}
        }

    def validate_config(self, config):
        if 'methods' not in config:
            raise serializers.ValidationError('"methods" must in config')

        return config
