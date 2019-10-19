from django.contrib import admin
from .models import EmailModel
from .modeladmin import EmailModelAdmin


# Register your models here.
admin.site.register(EmailModel, EmailModelAdmin)