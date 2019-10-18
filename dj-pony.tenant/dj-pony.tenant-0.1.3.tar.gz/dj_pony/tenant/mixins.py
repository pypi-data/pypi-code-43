from django.db import models
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.managers import SingleTenantModelManager, MultipleTenantModelManager
from dj_pony.tenant.helpers import get_current_tenant
from dj_pony.tenant.exceptions import TenantNotFoundError


def get_default_tenant():
    from dj_pony.tenant.models import Tenant

    return Tenant.objects.filter(slug=get_setting("DEFAULT_TENANT_SLUG")).first()


class SingleTenantModelMixin(models.Model):
    """
    Instances of models inheriting from this mixin are associated with one tenant.

    One Tenant -> Many instances of a Model

    Example:
        Tenant 1 - Instance 1
        Tenant 1 - Instance 2
        Tenant 2 - Instance 3
        Tenant 1 - Instance 4
        Tenant 2 - Instance 5
    """

    tenant = models.ForeignKey(
        "tenant.Tenant", default=get_default_tenant, on_delete=models.CASCADE
    )

    objects = SingleTenantModelManager()

    original_manager = models.Manager()
    tenant_objects = SingleTenantModelManager()

    class Meta:
        abstract = True
        default_manager_name = "objects"
        base_manager_name = "objects"

    def save(self, *args, **kwargs):
        if not hasattr(self, "tenant"):
            self.tenant = get_current_tenant()

        if getattr(self, "tenant", False):
            return super(SingleTenantModelMixin, self).save(*args, **kwargs)
        else:
            raise TenantNotFoundError()


class MultipleTenantsModelMixin(models.Model):
    """
    Instances of models inheriting from this are associated with one or more tenant.

    Many Tenant -> Many instances of a Model

    Example:
        Tenant 1              - Instance 1
        Tenant 1 and Tenant 2 - Instance 2
        Tenant 2              - Instance 3
        Tenant 2 and Tenant 3 - Instance 4
        Tenant 3              - Instance 5
    """

    tenants = models.ManyToManyField("tenant.Tenant")

    objects = MultipleTenantModelManager()

    tenant_objects = MultipleTenantModelManager()
    original_manager = models.Manager()

    class Meta:
        abstract = True
        default_manager_name = "objects"
        base_manager_name = "objects"

    # TODO: This doesnt look like safe behaviour, automatically adding the tenant if we have the object?
    def save(self, *args, **kwargs):
        tenant = get_current_tenant()

        if tenant:
            instance = super(MultipleTenantsModelMixin, self).save(*args, **kwargs)
            self.tenants.add(tenant)
            return instance
        else:
            raise TenantNotFoundError()
