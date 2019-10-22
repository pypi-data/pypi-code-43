from django.contrib import admin
from .models import NomencladorHPGD


@admin.register(NomencladorHPGD)
class NomencladorHPGDAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'uid', 'descripcion', 'arancel', 'observaciones']