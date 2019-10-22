from django.contrib import admin

from telebaka_toxic.models import ToxicityRating, String


@admin.register(ToxicityRating)
class ToxicityRatingAdmin(admin.ModelAdmin):
    list_display = 'chat_id', 'date', 'user_id', 'username', 'name', 'rating'


@admin.register(String)
class StringAdmin(admin.ModelAdmin):
    list_display = 'min_rating', 'text'
    ordering = ['min_rating']
