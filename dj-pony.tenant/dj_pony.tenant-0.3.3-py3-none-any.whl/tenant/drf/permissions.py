from rest_framework.permissions import BasePermission, DjangoModelPermissions


class DjangoTenantModelPermissions(DjangoModelPermissions):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant"):
            kwargs = {"tenant": obj.tenant}
        elif hasattr(obj, "tenants"):
            kwargs = {"tenant__in": obj.tenants.all()}
        else:
            return True

        # TODO: Work out how this line was hit...
        return request.user.relationships.filter(**kwargs).exists()


class IsTenantOwner(BasePermission):
    def has_permission(self, request, view):
        # TODO: Django dropped support for request.user.is_authenticated() as a method as of Django 2.0+
        # So this will need some kind of compatibility if check in order to support the Django 1.11.x LTS
        return (
            request.user.is_authenticated
            and request.user.relationships.filter(groups__name="tenant_owner").exists()
        )

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "tenant"):
            kwargs = {"tenant": obj.tenant}
        elif hasattr(obj, "tenants"):
            kwargs = {"tenant__in": obj.tenants.all()}
        else:
            return True

        # TODO: Django dropped support for request.user.is_authenticated() as a method as of Django 2.0+
        # So this will need some kind of compatibility if check in order to support the Django 1.11.x LTS
        return (
            request.user.is_authenticated
            and request.user.relationships.filter(**kwargs).exists()
        )
