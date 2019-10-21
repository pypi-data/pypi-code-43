# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from . import models
from django.contrib.contenttypes.admin import GenericTabularInline


class ImagesInline(GenericTabularInline):
    model = models.Image
    fields = ("file",)


class SettingInline(GenericTabularInline):
    model = models.Setting
    fields = ("name", "json_data",)
    extra = 0


class AttachmentInline(GenericTabularInline):
    model = models.Attachment
    fields = ("file",)
    extra = 0


# Register your models here.
@admin.register(models.Trash)
class TrashAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "object_name", "create_time")
    readonly_fields = ("content_type", "object_id", "create_time", "json_data")
    search_fields = ("object_name", )

    def has_add_permission(self, request):
        return False


def recover(modeladmin, request, queryset):
    for v in queryset.all():
        v.recover()
recover.short_description = "还原"


@admin.register(models.VersionHistory)
class VersionHistoryAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "object_name", "version", "create_time")
    readonly_fields = ("content_type", "object_id", "create_time", "json_data")
    search_fields = ("object_name", )
    list_filter = ("content_type",)
    actions = (recover,)

    def has_add_permission(self, request):
        return False

@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "object_id")
    # readonly_fields = ("content_type", "object_id", "json_data")

    # def has_add_permission(self, request):
    #     return False

@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("create_time", "owner", "create_time")
    readonly_fields = ("owner", "content_type")

@admin.register(models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("create_time", "owner", "file", "create_time")
    readonly_fields = ("owner", "content_type")

@admin.register(models.ExcelTask)
class ExcelTaskAdmin(admin.ModelAdmin):
    list_display = ("create_time", "owner", "name", "status")
    readonly_fields = ("owner", "content_type")
    inlines = (AttachmentInline,)


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ("create_time", "name", "object_name")
    readonly_fields = ("create_time", "context")

