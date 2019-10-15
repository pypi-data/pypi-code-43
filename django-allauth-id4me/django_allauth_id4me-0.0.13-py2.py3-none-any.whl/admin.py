from django.contrib import admin

from .models import ID4meStore


class ID4meStoreAdmin(admin.ModelAdmin):
    pass


admin.site.register(ID4meStore, ID4meStoreAdmin)
