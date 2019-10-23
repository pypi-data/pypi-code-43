# Imports from Django.
from django.contrib import admin


# Imports from entity.
from entity.models import PersonImage


class PersonImageInline(admin.StackedInline):
    model = PersonImage
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonImageInline]

    fieldsets = (
        (
            "Name",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "suffix",
                    "full_name",
                )
            },
        ),
        (
            "Demographics",
            {
                "fields": (
                    "gender",
                    "race",
                    "nationality",
                    "state_of_residence",
                )
            },
        ),
        (None, {"fields": ("birth_date", "death_date")}),
        (
            "Descriptions",
            {"fields": ("summary", "description", "identifiers", "links")},
        ),
        ("Record locators", {"fields": ("id", "uid", "slug")}),
    )
    readonly_fields = ("id", "uid", "slug")

    search_fields = ("first_name", "last_name")
    ordering = ("last_name",)
