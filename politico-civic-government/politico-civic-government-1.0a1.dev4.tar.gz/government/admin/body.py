# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from other dependencies.
from entity.models import Organization


# Imports from government.
from government.models import Body, Jurisdiction


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "name"):
            return obj.name
        else:
            return obj.label


class BodyAdminForm(forms.ModelForm):
    jurisdiction = CustomModelChoiceField(queryset=Jurisdiction.objects.all())
    organization = CustomModelChoiceField(queryset=Organization.objects.all())
    parent = CustomModelChoiceField(
        queryset=Body.objects.all(), required=False
    )


class BodyAdmin(admin.ModelAdmin):
    form = BodyAdminForm
    list_display = ("label", "get_jurisdiction")
    list_filter = (
        ("jurisdiction__name", custom_titled_filter("jurisdiction")),
    )
    search_fields = ("label",)
    ordering = ("label", "jurisdiction__name")
    readonly_fields = ["uid"]

    fieldsets = (
        ("Names and labeling", {"fields": ("label", "short_label")}),
        (
            "Relationships",
            {"fields": ("jurisdiction", "organization", "parent")},
        ),
        ("Record locators", {"fields": ("slug", "uid")}),
    )

    def get_jurisdiction(self, obj):
        return obj.jurisdiction.name

    get_jurisdiction.short_description = "Jurisdiction"
