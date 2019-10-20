import logging

from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
)
from django.contrib.auth.models import User

from console import console

__all__ = ['UserAdmin']

console = console(source=__name__)
logger = logging.getLogger('app')


class UserAdmin(DjangoUserAdmin):
    list_filter = ['is_staff', 'is_superuser']
    autocomplete_fields = ['groups', 'user_permissions']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
