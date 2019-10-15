from rest_framework import serializers

from terra_utils.tests.test_app.models import DummyModel


class DummySerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyModel
        fields = ('name', 'properties')
