# Imports from entity.
from entity.models import Person
from entity.serializers import PersonSerializer
from entity.viewsets.base import BaseViewSet


class PersonViewSet(BaseViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
