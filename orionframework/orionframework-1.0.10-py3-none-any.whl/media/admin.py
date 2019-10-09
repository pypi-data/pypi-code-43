from django.contrib import admin

from orionframework.media.settings import Document, Image


class DocumentAdmin(admin.ModelAdmin):
    model = Document
    list_display = ["id", "title", "filename", "file", "parent_type", "parent_id"]
    search_fields = ["title", "filename"]


class ImageAdmin(admin.ModelAdmin):
    model = Image
    list_display = ["id", "title", "filename", "file", "parent_type", "parent_id", "width", "height"]
    search_fields = ["title", "filename"]
