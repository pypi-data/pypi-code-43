from django.contrib import admin

from .models import ContactRequest, ContactInformation


@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'

    list_display = [
        'name',
        'created',
        'contacted',
    ]

    list_filter = [
        'contacted',
    ]

    readonly_fields = [
        'name',
        'email',
        'phone_number',
        'message',
    ]
