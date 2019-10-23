# Imports from Django.
from django.contrib import admin


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "get_jurisdiction", "get_body")
    list_filter = (
        ("body__label", custom_titled_filter("body")),
        ("jurisdiction__name", custom_titled_filter("jurisdiction")),
    )
    search_fields = ("name", "label")
    ordering = ("name", "body__label", "jurisdiction__name")
    readonly_fields = ("slug", "uid")

    fieldsets = (
        (
            "Names and labeling",
            {"fields": ("name", "label", "short_label", "senate_class")},
        ),
        ("Relationships", {"fields": ("division", "body", "jurisdiction")}),
        ("Record locators", {"fields": ("slug", "uid")}),
    )

    def get_body(self, obj):
        if obj.body:
            return obj.body.label
        else:
            return None

    def get_jurisdiction(self, obj):
        return obj.jurisdiction.name

    get_body.short_description = "Body"
    get_jurisdiction.short_description = "Jurisdiction"
