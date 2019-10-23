from django.contrib import admin

from .models import Service, ServiceConfig, ServiceType

# Register your models here.


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceConfig)
class ServiceConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    pass
