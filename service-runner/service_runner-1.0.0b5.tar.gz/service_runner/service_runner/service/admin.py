from django.contrib import admin

from .models import ServiceTask, ServiceTaskRecord, ServiceTaskResponse, ServiceType

# Register your models here.


@admin.register(ServiceTask)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceTaskRecord)
class ServiceTaskRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceTaskResponse)
class ServiceTaskResponseAdmin(admin.ModelAdmin):
    pass
