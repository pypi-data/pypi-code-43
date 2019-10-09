
from rest_framework_extensions.key_constructor.constructors import DefaultListKeyConstructor


class ListKeyConstructor(DefaultListKeyConstructor):

    def get_key(self, view_instance, view_method, request, args, kwargs):
        key = super().get_key(view_instance, view_method, request, args, kwargs)
        meta = view_instance.queryset.model._meta
        return f'{meta.app_label}.{meta.object_name}.{key}'


list_cache_key_func = ListKeyConstructor()
