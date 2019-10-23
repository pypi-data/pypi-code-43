from dj_pony.tenant.settings import get_setting

from dj_pony.tenant.helpers import TenantJSONFieldHelper


class TenantSettingsHelper(TenantJSONFieldHelper):
    def __init__(self, instance=None):
        super(TenantSettingsHelper, self).__init__(
            instance_field_name="settings",
            instance=instance,
            tenant_fields=get_setting("DEFAULT_TENANT_SETTINGS_FIELDS"),
            tenant_default_fields_values=get_setting("DEFAULT_TENANT_SETTINGS"),
        )
