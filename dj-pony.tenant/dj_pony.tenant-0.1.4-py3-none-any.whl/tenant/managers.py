from django.db.models import Manager
from dj_pony.tenant.helpers import get_current_tenant


class SingleTenantModelManager(Manager):
    def get_original_queryset(self, *args, **kwargs):
        return super(SingleTenantModelManager, self).get_queryset(*args, **kwargs)

    def get_queryset(self, tenant=None, *args, **kwargs):
        if not tenant:
            tenant = get_current_tenant()
            if tenant:
                return (
                    super(SingleTenantModelManager, self)
                    .get_queryset(*args, **kwargs)
                    .filter(tenant=tenant)
                )
            else:
                return (
                    super(SingleTenantModelManager, self)
                    .get_queryset(*args, **kwargs)
                    .none()
                )
        else:
            return (
                super(SingleTenantModelManager, self)
                .get_queryset(*args, **kwargs)
                .filter(tenant=tenant)
            )

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        # TODO: Something here to avoid silently losing changes in bulk create calls...
        # print()
        print("Hit Bulk Create")
        # print()
        super(SingleTenantModelManager, self).bulk_create(
            objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts
        )

    def bulk_update(self, objs, fields, batch_size=None):
        # TODO: Something here to avoid silently losing changes in bulk update calls...
        # print()
        print("Hit Bulk Update")
        # print()
        super(SingleTenantModelManager, self).bulk_update(
            objs, fields, batch_size=batch_size
        )


class MultipleTenantModelManager(Manager):
    def get_original_queryset(self, *args, **kwargs):
        return super(MultipleTenantModelManager, self).get_queryset(*args, **kwargs)

    def get_queryset(self, tenant=None, *args, **kwargs):
        if not tenant:
            tenant = get_current_tenant()
            if tenant:
                return (
                    super(MultipleTenantModelManager, self)
                    .get_queryset(*args, **kwargs)
                    .filter(tenants=tenant)
                )
            else:
                return (
                    super(MultipleTenantModelManager, self)
                    .get_queryset(*args, **kwargs)
                    .none()
                )
        else:
            return (
                super(MultipleTenantModelManager, self)
                .get_queryset(*args, **kwargs)
                .filter(tenants=tenant)
            )

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        # TODO: Something here to avoid silently losing changes in bulk create calls...
        # print()
        print("Hit Bulk Create")
        # print()
        super(MultipleTenantModelManager, self).bulk_create(
            objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts
        )

    def bulk_update(self, objs, fields, batch_size=None):
        # TODO: Something here to avoid silently losing changes in bulk update calls...
        # print()
        print("Hit Bulk Update")
        # print()
        super(MultipleTenantModelManager, self).bulk_update(
            objs, fields, batch_size=batch_size
        )
