from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.UploadedFile)
admin.site.register(models.UploadedFileVersion)
