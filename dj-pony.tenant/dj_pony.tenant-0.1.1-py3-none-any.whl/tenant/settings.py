from django.conf import settings


def get_setting(settings_name):
    tenant_settings = getattr(settings, "SHARED_SCHEMA_TENANTS", {})
    DEFAULT_TENANT_SETTINGS_FIELDS = tenant_settings.get(
        "DEFAULT_TENANT_SETTINGS_FIELDS", {}
    )
    DEFAULT_TENANT_EXTRA_DATA_FIELDS = tenant_settings.get(
        "DEFAULT_TENANT_EXTRA_DATA_FIELDS", {}
    )

    settings_dict = {
        "TENANT_SERIALIZER": (
            tenant_settings.get("SERIALIZERS", {}).get(
                "TENANT_SERIALIZER", "dj_pony.tenant.drf.serializers.TenantSerializer"
            )
        ),
        "TENANT_SITE_SERIALIZER": (
            tenant_settings.get("SERIALIZERS", {}).get(
                "TENANT_SITE_SERIALIZER",
                "dj_pony.tenant.drf.serializers.TenantSiteSerializer",
            )
        ),
        "TENANT_SETTINGS_SERIALIZER": (
            tenant_settings.get("SERIALIZERS", {}).get(
                "TENANT_SETTINGS_SERIALIZER",
                "dj_pony.tenant.drf.serializers.TenantSettingsSerializer",
            )
        ),
        "TENANT_RELATIONSHIP_SERIALIZER": (
            tenant_settings.get("SERIALIZERS", {}).get(
                "TENANT_SITE_SERIALIZER",
                "dj_pony.tenant.drf.serializers.TenantSiteSerializer",
            )
        ),
        "DEFAULT_TENANT_SETTINGS_FIELDS": DEFAULT_TENANT_SETTINGS_FIELDS,
        "DEFAULT_TENANT_SETTINGS": {
            key: value.get("default")
            for key, value in DEFAULT_TENANT_SETTINGS_FIELDS.items()
        },
        "DEFAULT_TENANT_EXTRA_DATA_FIELDS": DEFAULT_TENANT_EXTRA_DATA_FIELDS,
        "DEFAULT_TENANT_EXTRA_DATA": {
            key: value.get("default")
            for key, value in DEFAULT_TENANT_EXTRA_DATA_FIELDS.items()
        },
        "DEFAULT_SITE_DOMAIN": tenant_settings.get("DEFAULT_SITE_DOMAIN", "localhost"),
        "DEFAULT_TENANT_SLUG": tenant_settings.get("DEFAULT_TENANT_SLUG", "default"),
        "TENANT_RETRIEVERS": tenant_settings.get(
            "TENANT_RETRIEVERS",
            [
                "dj_pony.tenant.tenant_retrievers.retrieve_by_domain",
                "dj_pony.tenant.tenant_retrievers.retrieve_by_http_header",
                "dj_pony.tenant.tenant_retrievers.retrieve_by_session",
            ],
        ),
        "ADD_TENANT_TO_SESSION": tenant_settings.get("ADD_TENANT_TO_SESSION", True),
        "TENANT_HTTP_HEADER": tenant_settings.get("TENANT_HTTP_HEADER", "Tenant-Slug"),
        "DEFAULT_TENANT_OWNER_PERMISSIONS": tenant_settings.get(
            "DEFAULT_TENANT_OWNER_PERMISSIONS",
            [
                # 'dj_pony.tenant.add_tenant',
                # 'shared_schema_tenants.add_tenant',
                "tenant.add_tenant",
                "tenant.change_tenant",
                "tenant.delete_tenant",
                "tenant.add_tenantsite",
                "tenant.change_tenantsite",
                "tenant.delete_tenantsite",
                "tenant.add_tenantrelationship",
                "tenant.delete_tenantrelationship",
                "tenant.change_tenantrelationship",
            ],
        ),
    }

    return settings_dict.get(settings_name)
