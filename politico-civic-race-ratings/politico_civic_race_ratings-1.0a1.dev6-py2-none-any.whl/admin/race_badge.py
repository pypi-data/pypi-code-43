# Imports from Django.
from django.contrib import admin


class RaceBadgeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("race",)
