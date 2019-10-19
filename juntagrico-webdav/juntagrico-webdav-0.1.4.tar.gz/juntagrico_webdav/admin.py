from django.contrib import admin

from juntagrico_webdav.entity.servers import WebdavServer


class WebdavServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'menu_title', 'active', 'type')
    search_fields = ('name', 'url', 'menu_title', 'path')


admin.site.register(WebdavServer, WebdavServerAdmin)
