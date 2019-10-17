import json #line:2
from django import template #line:4
register =template .Library ()#line:6
from import_export .admin import ImportExportMixinBase #line:8
from simplepro import conf #line:9
import simplepro #line:10
import simpleui #line:11
@register .simple_tag (takes_context =True )#line:14
def has_import_export (context ):#line:15
    OO0O000O00OO0OO0O =context .get ('cl')#line:16
    return issubclass (OO0O000O00OO0OO0O .__class__ ,ImportExportMixinBase )#line:17
@register .simple_tag (takes_context =True )#line:20
def get_display_name (context ):#line:21
    OO0OO00O0000O0O00 =context .get ('user')#line:22
    if OO0OO00O0000O0O00 :#line:24
        O0O00OO0OO00OO00O =''#line:25
        if OO0OO00O0000O0O00 .first_name :#line:27
            O0O00OO0OO00OO00O +=OO0OO00O0000O0O00 .first_name #line:28
        if OO0OO00O0000O0O00 .last_name :#line:29
            O0O00OO0OO00OO00O +=OO0OO00O0000O0O00 .last_name #line:30
    if not O0O00OO0OO00OO00O :#line:31
        O0O00OO0OO00OO00O =str (OO0OO00O0000O0O00 )#line:32
    return O0O00OO0OO00OO00O #line:33
@register .simple_tag #line:36
def get_server_url ():#line:37
    return conf .get_server_url ()#line:38
@register .simple_tag #line:41
def get_sp_version ():#line:42
    return simplepro .get_version ()#line:43
@register .simple_tag #line:46
def get_device_id ():#line:47
    return conf .get_device_id ()#line:48
@register .simple_tag #line:51
def get_simple_version ():#line:52
    return simpleui .get_version ()#line:53
