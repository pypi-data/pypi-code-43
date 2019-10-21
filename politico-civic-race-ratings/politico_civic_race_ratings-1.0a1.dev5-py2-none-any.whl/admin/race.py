# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from other dependencies.
from election.models import ElectionCycle


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "name"):
            return obj.name
        elif hasattr(obj, "date"):
            return obj.date
        else:
            return obj.label


class RaceAdminForm(forms.ModelForm):
    cycle = CustomModelChoiceField(queryset=ElectionCycle.objects.all())


class RaceAdmin(admin.ModelAdmin):
    form = RaceAdminForm
    list_display = ("get_office", "get_cycle", "special")
    autocomplete_fields = ["office"]
    search_fields = ["office__label", "cycle__name", "label"]
    ordering = ("office__label", "cycle__name")
    readonly_fields = ("uid", "slug")

    fieldsets = (
        (
            "Names and labeling",
            {"fields": ("label", "short_label", "special", "description")},
        ),
        ("Relationships", {"fields": ("office", "cycle")}),
        ("Record locators", {"fields": ("uid", "slug")}),
    )

    def get_office(self, obj):
        return obj.office.label

    def get_cycle(self, obj):
        return obj.cycle.name

    get_office.short_description = "Office"
    get_cycle.short_description = "Cycle"
