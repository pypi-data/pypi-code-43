from django .contrib .admin .models import LogEntry #line:1
from django .contrib .auth .admin import GroupAdmin #line:2
from django .contrib import admin #line:4
from django .contrib .auth .models import Permission #line:5
from django .contrib .contenttypes .models import ContentType #line:6
@admin .register (ContentType )#line:9
class ContentTypeAdmin (admin .ModelAdmin ):#line:10
    list_display =('id','app_label','model')#line:11
    list_per_page =20 #line:12
    search_fields =('app_label','model')#line:13
@admin .register (Permission )#line:16
class PermissionAdmin (admin .ModelAdmin ):#line:17
    list_filter =('content_type',)#line:18
    list_display =('id','name','content_type','codename')#line:19
    list_per_page =20 #line:20
    search_fields =('name','codename')#line:21
@admin .register (LogEntry )#line:24
class LogEntryAdmin (admin .ModelAdmin ):#line:25
    list_display =('id','user','content_type','action_flag','action_time')#line:26
    list_filter =('user','content_type','action_flag','action_time')#line:27
    list_per_page =20 #line:28
