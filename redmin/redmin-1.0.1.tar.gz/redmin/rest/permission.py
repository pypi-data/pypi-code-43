from django.urls import reverse
from rest_framework import permissions

from redmin.models import Permission, PermissionItem
from redmin.utils import attr


class RolePermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        path = request.get_full_path()
        if path.startswith(reverse("account-login")) or path.startswith(reverse("account-logout")):
            return True
        model = attr(view, "model")
        if model:
            return Permission.has_permission(request.user, model, PermissionItem.viewable)
        return super().has_permission(request, view)
