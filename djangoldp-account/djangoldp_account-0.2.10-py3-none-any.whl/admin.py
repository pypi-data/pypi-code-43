from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import LDPUser

class LDPUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = LDPUser

class LDPUserAdmin(UserAdmin):
    form = LDPUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('slug',)}),
    )


admin.site.register(LDPUser, LDPUserAdmin)