from django.contrib import admin
from django.forms import Textarea
from django.db import models
from deeppages.models import Template, Page


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identification', {
            'fields': ('name', ),
        }),
        ('Content', {
            'fields': ('content', )
        }),
    )

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 20, 'style': 'width: 99%;'})
        },
    }

    search_fields = ['name', ]
    list_display = ('id', 'name', 'created_at', 'changed_at', )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identification', {
            'fields': (('name', 'slug'), 'path', ),
        }),
        ('Content', {
            'fields': ('content', )
        }),
    )

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 20, 'style': 'width: 99%;'})
        },
    }

    readonly_fields = ('slug', )
    search_fields = ['name', 'slug', 'path']
    list_display = ('id', 'name', 'slug', 'path', 'created_at', 'changed_at', )
