# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from government.
from government.models import Jurisdiction


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "name"):
            return obj.name
        else:
            return obj.label


class JurisdictionAdminForm(forms.ModelForm):
    parent = CustomModelChoiceField(
        queryset=Jurisdiction.objects.all(), required=False
    )


class JurisdictionAdmin(admin.ModelAdmin):
    form = JurisdictionAdminForm
    list_display = ("name", "get_division")
    search_fields = ("name",)
    ordering = ("name", "division__label")
    readonly_fields = ("slug", "uid")

    fieldsets = (
        ("Names and labeling", {"fields": ("name",)}),
        ("Relationships", {"fields": ("division", "parent")}),
        ("Record locators", {"fields": ("slug", "uid")}),
    )

    def get_division(self, obj):
        return obj.division.label

    get_division.short_description = "Division"
