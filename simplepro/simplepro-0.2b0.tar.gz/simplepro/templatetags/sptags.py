import json #line:2
from django import template #line:4
register =template .Library ()#line:6
from import_export .admin import ImportExportMixinBase #line:8
from simplepro import conf #line:9
import simplepro #line:10
@register .simple_tag (takes_context =True )#line:13
def has_import_export (context ):#line:14
    OO0OO00O00O0OOOOO =context .get ('cl')#line:15
    return issubclass (OO0OO00O00O0OOOOO .__class__ ,ImportExportMixinBase )#line:16
@register .simple_tag (takes_context =True )#line:19
def get_display_name (context ):#line:20
    OO00000OO00OO0OOO =context .get ('user')#line:21
    OO0OOO00O0000O000 =OO00000OO00OO0OOO #line:22
    if OO00000OO00OO0OOO :#line:23
        OO0OOO00O0000O000 =''#line:24
        if OO00000OO00OO0OOO .first_name :#line:26
            OO0OOO00O0000O000 +=OO00000OO00OO0OOO .first_name #line:27
        if OO00000OO00OO0OOO .last_name :#line:28
            OO0OOO00O0000O000 +=OO00000OO00OO0OOO .last_name #line:29
    return OO0OOO00O0000O000 #line:30
@register .simple_tag #line:33
def get_server_url ():#line:34
    return conf .get_server_url ()#line:35
@register .simple_tag #line:38
def get_sp_version ():#line:39
    return simplepro .get_version ()#line:40
@register .simple_tag #line:43
def get_device_id ():#line:44
    return conf .get_device_id ()#line:45
