# -*- coding:utf8 -*-
# Author:DenisHuang
# Date:
# Usage:

from django.contrib import admin
from . import models

@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'type', 'from_id', 'to_id', 'content')
    search_fields = ('from_id', 'to_id')
    # date_hierarchy = 'create_time'


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'openid', 'province', 'city', 'user', 'subscribe_time')
    raw_id_fields = ('user',)
    readonly_fields = ('user',)
    search_fields = ('nickname', 'openid', 'user__username')

