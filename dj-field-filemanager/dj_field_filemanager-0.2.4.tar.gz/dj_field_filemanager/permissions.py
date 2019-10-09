from django.contrib.auth import get_permission_codename

from rest_framework.permissions import BasePermission


class ModelHasPermission(BasePermission):
    def has_permission(self, request, view):
        permissions = {
            'list': 'view',
            'create': 'add',
            'retrieve': 'view',
            # 'update': 'change',
            # 'partial_update': 'change',
            'destroy': 'delete'
        }
        if view.action not in permissions:
            return False
        permission = permissions[view.action]

        opts = type('', (), {})()
        opts.app_label = view.model._meta.app_label
        opts.model_name = view.model._meta.model_name
        codename = get_permission_codename(permission, opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))


class StorageHasPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
