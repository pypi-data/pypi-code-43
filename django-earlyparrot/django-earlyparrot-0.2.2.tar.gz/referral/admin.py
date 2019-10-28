from django.contrib import admin

from .models import Campaign, Subscriber


class SubscriberAdmin(admin.TabularInline):
    model = Subscriber
    extra = 3


class CampaignAdmin(admin.ModelAdmin):
    inlines = (SubscriberAdmin, )
    list_filter = ('status', )
    list_display = (
        'campaign_id',
        'name',
        'status',
        'total_users',
    )


admin.site.register(Campaign, CampaignAdmin)
