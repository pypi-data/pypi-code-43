from django.contrib import admin
from .models import Credential


class CredentialAdmin(admin.ModelAdmin):
    list_display = ('login', 'client_service_id', 'platform_id', 'id')
    list_filter = ('platform_id',)
    search_fields = ('login',)

    class Meta:
        model = Credential


admin.site.register(Credential, CredentialAdmin)
