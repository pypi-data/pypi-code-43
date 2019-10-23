from contextlib import contextmanager

from django.contrib.sites.models import Site
from django.contrib.auth.models import Group, Permission
from django.db import transaction

from dj_pony.tenant.settings import get_setting


def get_current_tenant():
    from dj_pony.tenant.middleware import TenantMiddleware

    return TenantMiddleware.get_current_tenant()


def set_current_tenant(tenant_slug):
    from dj_pony.tenant.middleware import TenantMiddleware

    return TenantMiddleware.set_tenant(tenant_slug)


def clear_current_tenant():
    from dj_pony.tenant.middleware import TenantMiddleware

    return TenantMiddleware.clear_tenant()


def create_tenant(name, slug, extra_data, domains=[], user=None):
    from dj_pony.tenant.models import Tenant

    with transaction.atomic():
        tenant = Tenant.objects.create(name=name, slug=slug, extra_data=extra_data)

        if len(domains) > 0:
            for domain in domains:
                site = Site.objects.create(name=name, domain=domain)
                tenant.tenant_sites.create(site=site)

        if user:
            rel = tenant.relationships.create(user=user)
            rel.groups.add(create_default_tenant_groups()[0])

        return tenant


def update_tenant(tenant, name=None, slug=None, extra_data=None):
    from dj_pony.tenant.helpers import TenantExtraDataHelper

    with transaction.atomic():
        tenant.name = name if name else tenant.name
        tenant.slug = slug if slug else tenant.slug

        extra_data_helper = TenantExtraDataHelper(instance=tenant)
        tenant = extra_data_helper.update_fields(
            extra_data if extra_data else {}, commit=False
        )

        tenant.save()

        return tenant


def create_default_tenant_groups():
    with transaction.atomic():
        group, created = Group.objects.get_or_create(name="tenant_owner")

        if created:
            for perm in get_setting("DEFAULT_TENANT_OWNER_PERMISSIONS"):
                try:
                    group.permissions.add(
                        Permission.objects.get(
                            content_type__app_label=perm.split(".")[0],
                            codename=perm.split(".")[1],
                        )
                    )
                # TODO: Work out how to test this code branch.
                #  Its ok for now since its a 'do nothing' branch,
                #  but I would still like to have test coverage over it.
                except Permission.DoesNotExist:  # pragma: no cover
                    pass  # pragma: no cover

        return [group]


@contextmanager
def current_tenant(tenant):
    set_current_tenant(tenant.slug)
    yield
    clear_current_tenant()
