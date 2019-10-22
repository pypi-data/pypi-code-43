import json
import html
from django.contrib import admin
from django import forms
from django.urls import path
from django.db import models
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import format_html
from .models import Host, HostGroup, SshKey
from .utils import get_host_uptime, get_host_info
# Register your models here.


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('ip', 'host_group', 'ssh_user',
                    'system_type', 'display_status', 'valid', 'update_time', 'create_time', 'display_options')
    list_filter = ('status', 'valid', 'host_group__name', 'system_type')
    list_editable = ('valid',)
    search_fields = ('ip', 'description')
    change_list_template = 'admin/asset/host_change_list.html'

    def get_urls(self):
        base_urls = super().get_urls()
        urls = [
            path('getHostUptime/', self.admin_site.admin_view(
                self.get_host_uptime_view, cacheable=True), name='get_host_uptime'),
            path('getHostInfo/', self.admin_site.admin_view(
                self.get_host_info_view, cacheable=True), name='get_host_uptime'),
            path('terminal/', self.admin_site.admin_view(
                self.terminal_view, cacheable=True), name='terminal'),
        ]
        return urls + base_urls

    def display_status(self, obj):
        # callback_html = '''<div>$[ hostUptime.''' + \
        #     str(obj.id) + ''' ] ''' + obj.get_status_display() + '''</div>'''

        callback_html = '''
        <div v-if="hostUptime.host_{host_id}" ref='host_{host_id}' data-host-id={host_id} data-toggle="tooltip" :data-original-title="hostUptime.host_{host_id}.uptime">
            <span v-if="hostUptime.host_{host_id}.status=='ONLINE'" class="label label-success">$[hostUptime.host_{host_id}.status]</span>
            <span v-if="hostUptime.host_{host_id}.status=='OFFLINE'" class="label label-danger">$[hostUptime.host_{host_id}.status]</span>
        </div>
        <div v-else ref='host_{host_id}' data-host-id={host_id}><i class="fa fa-refresh fa-spin"></i></div>
        '''.format(
            host_id=str(obj.id), host_status=obj.get_status_display()
        )
        return format_html(callback_html)

    def display_options(self, obj):
        return format_html('''
        <a target="_blank" href='/admin/asset/host/terminal/?host_id={host_id}'>Open terminal</a>
        '''.format(host_id=obj.id))

    def get_host_uptime_view(self, request):
        host_id = request.GET.get('host_id')
        response_data = {}
        if not host_id:
            response_data['message'] = 'host_id is required.'
            return JsonResponse(response_data, status=400)

        callback = get_host_uptime(host_id)

        response_data = callback
        return JsonResponse(response_data, safe=False)

    def get_host_info_view(self, request):
        host_id = request.GET.get('host_id')
        response_data = {}
        if not host_id:
            response_data['message'] = 'host_id is required.'
            return JsonResponse(response_data, status=400)

        callback = get_host_info(host_id)

        response_data = callback
        return JsonResponse(response_data, safe=False)

    def terminal_view(self, request):
        host_id = request.GET.get('host_id')
        context = dict(
            self.admin_site.each_context(request),
        )
        if host_id:
            try:
                context['object'] = Host.objects.get(id=host_id)
            except:
                context['object'] = []
        else:
            context['object'] = []

        return render(request, 'admin/asset/host_terminal.html', context=context)


@admin.register(SshKey)
class SshKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ssh_key')
    search_fields = ('name',)


@admin.register(HostGroup)
class HostGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
