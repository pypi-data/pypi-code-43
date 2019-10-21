from django.contrib import admin

from . import models


class GenericTypeformFeedbackAdmin(admin.ModelAdmin):
    list_filter = ('typeform_type', )
    list_display = (
        'object_id', 'content_type',
        'quiz_slug', 'url', 'typeform_type',
        'created', 'modified',
    )


class UserGenericTypeformFeedbackAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = (
        'user', 'feedback',
        'response', 'status',
        'created', 'modified',
    )


admin.site.register(models.GenericTypeformFeedback, GenericTypeformFeedbackAdmin)
admin.site.register(models.UserGenericTypeformFeedback, UserGenericTypeformFeedbackAdmin)
