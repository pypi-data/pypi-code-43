# Imports from Django.
from django.contrib import admin


# Imports from entity.
from entity.models import OrganizationImage


class OrganizationImageInline(admin.StackedInline):
    model = OrganizationImage
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationImageInline]

    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Profile",
            {
                "fields": (
                    "classification",
                    "national_headquarters",
                    "founding_date",
                    "dissolution_date",
                )
            },
        ),
        ("Hierarchy", {"fields": ("parent",)}),
        (
            "Descriptions",
            {"fields": ("summary", "description", "identifiers", "links")},
        ),
        ("Record locators", {"fields": ("id", "uid", "slug")}),
    )
    readonly_fields = ("id", "uid", "slug")

    search_fields = ("name",)
    ordering = ("name",)
