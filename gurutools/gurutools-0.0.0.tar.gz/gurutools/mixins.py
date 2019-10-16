from rest_framework import decorators, response
from django.http import Http404
from django.utils.module_loading import import_string
from .mixincore import BaseActionMixin

class MultiSerializerMixin():
    '''
    A mixins that allows you to easily specify different serializers for various verbs
    '''

    def get_serializer_class(self):
        default_serializer = self.default_serializer_class
        return self.serializer_map.get(self.action, default_serializer)

class SchemaMixin():
    '''
    Adds a /schema/ list view which dumps an empty serializer
    '''

    @decorators.list_route()
    def schema(self, request):
        klass = self.get_serializer_class()
        return response.Response(klass().data)

class SetOwnersPermissionsMixin():

    def perform_create(self, serializer):
        serializer.save(owners=[self.request.user])

    def perform_update(self, serializer):
        serializer.save(owners=[self.request.user])
