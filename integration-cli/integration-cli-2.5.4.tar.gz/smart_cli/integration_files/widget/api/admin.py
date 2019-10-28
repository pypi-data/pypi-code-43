from django.contrib import admin
from .models import Credential


class CredentialAdmin(admin.ModelAdmin):
    list_display = ('login', 'platform_id', 'user_id', 'client_service_id', 'id')
    list_filter = ('platform_id',)

    class Meta:
        model = Credential


admin.site.register(Credential, CredentialAdmin)
