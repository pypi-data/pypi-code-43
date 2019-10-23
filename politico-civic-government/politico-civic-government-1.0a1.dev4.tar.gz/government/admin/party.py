# Imports from Django.
from django.contrib import admin


class PartyAdmin(admin.ModelAdmin):
    list_display = ("label", "ap_code")
    search_fields = ("label", "ap_code")
    ordering = ("label",)
    readonly_fields = ("uid",)

    fieldsets = (
        ("Names and labeling", {"fields": ("label", "short_label")}),
        ("Relationships", {"fields": ("organization",)}),
        (
            "Election display information",
            {"fields": ("ap_code", "aggregate_candidates")},
        ),
        ("Record locators", {"fields": ("slug", "uid")}),
    )
