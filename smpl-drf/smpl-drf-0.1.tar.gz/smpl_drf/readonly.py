
from rest_framework import viewsets
from rest_framework import serializers

from .pagination import Pagination


def get_readonly_view(model_class):

    _ = type(f'{model_class.__name__}_AutoSerializer', (serializers.ModelSerializer,), dict(
        Meta=type('Meta', (object,), dict(
            model=model_class,
            fields='__all__',
        ))
    ))

    class ReadonlyModelView(viewsets.ReadOnlyModelViewSet):
        queryset = model_class.objects.all()
        pagination_class = Pagination
        serializer_class = _

    return ReadonlyModelView
