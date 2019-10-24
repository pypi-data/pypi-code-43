from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Circle, CircleMember


class TeamInline(admin.TabularInline):
    model = CircleMember
    extra = 0


class CircleAdmin(GuardedModelAdmin):
    exclude = ('jabberID', 'jabberRoom')
    inlines = [TeamInline]


admin.site.register(Circle, CircleAdmin)
