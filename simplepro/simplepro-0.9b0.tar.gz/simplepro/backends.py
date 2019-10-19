import datetime #line:1
import json #line:2
import os #line:3
import re #line:4
import struct #line:5
import time #line:6
import requests #line:8
import rsa as rsa #line:9
from django .contrib .auth .admin import GroupAdmin #line:10
from django .core .paginator import Paginator #line:11
from django .db .models import Model ,Q #line:12
from django .http import HttpResponse #line:13
from django .shortcuts import render #line:14
from django .urls import reverse #line:15
from django .utils .html import format_html #line:16
from simplepro import conf #line:17
from simplepro .utils import LazyEncoder ,has_permission ,write ,get_model_info ,search_placeholder ,get_custom_button ,get_menus ,write_obj #line:19
URL_CACHE ={}#line:21
import base64 #line:23
cache_d =None #line:25
def O0O0OOO0OOO0OO0O0 (OOOO0O000OOOOO0O0 =False ):#line:28
    try :#line:29
        O0000000OOOOO0O0O =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:31
        if not os .path .exists (O0000000OOOOO0O0O +'/simplepro/simpepro.lic'):#line:32
            return False #line:33
        global cache_d #line:34
        if OOOO0O000OOOOO0O0 :#line:35
            cache_d =None #line:36
        if cache_d :#line:38
            return cache_d #line:39
        OOOO0OO0O0O00OO0O =open (O0000000OOOOO0O0O +'/simplepro/simpepro.lic','rb')#line:40
        OO00O0O0OOO000O00 =OOOO0OO0O0O00OO0O .read ()#line:41
        O000OO0O000OOOOOO ,=struct .unpack ('h',OO00O0O0OOO000O00 [0 :2 ])#line:42
        O00O000O0OO0OOOO0 ,=struct .unpack ('h',OO00O0O0OOO000O00 [2 :4 ])#line:43
        OOOO0OO0OO00OOO00 =OO00O0O0OOO000O00 [4 :O000OO0O000OOOOOO +4 ]#line:44
        OO0O00000O0OO0O0O =base64 .b64decode (OO00O0O0OOO000O00 [O000OO0O000OOOOOO +4 :])#line:46
        OOOO0O00O0O0OOO0O =rsa .PrivateKey .load_pkcs1 (OO0O00000O0OO0O0O )#line:48
        OO0OO00O0OO0OOO0O =rsa .decrypt (OOOO0OO0OO00OOO00 ,OOOO0O00O0O0OOO0O ).decode ()#line:49
        O0000O00OOOOOOOO0 =json .loads (OO0OO00O0OO0OOO0O )#line:50
        cache_d =O0000O00OOOOOOOO0 #line:51
    except Exception as O00000O0O00OO0000 :#line:52
        pass #line:53
    return O0000O00OOOOOOOO0 #line:54
def OO0O0OO0OOO0OO0O0 (request ):#line:57
    try :#line:58
        OO000O00OO00O00O0 =O0O0OOO0OOO0OO0O0 ()#line:59
        O000OOO0O0O0000OO =OO000O00OO00O00O0 .get ('end_date').split (' ')[0 ]#line:61
        OO00OO00O0O00OO0O =datetime .datetime .strptime (O000OOO0O0O0000OO ,'%Y-%m-%d')#line:62
        O0OOOO00O000000OO =datetime .datetime .now ()#line:63
        if O0OOOO00O000000OO >OO00OO00O0O00OO0O :#line:64
            request .msg ='激活码已经过期，请重新购买！'#line:65
            return False #line:66
        OO0OO00OOOOOO0OO0 =OO000O00OO00O00O0 .get ('device_id')#line:67
        if str (conf .get_device_id ())!=str (OO0OO00OOOOOO0OO0 ):#line:68
            request .msg ='激活码和设备不匹配，请重新激活！'#line:69
            return False #line:70
        return True #line:71
    except Exception as OOO00OO000OO0OO00 :#line:72
        pass #line:74
    return False #line:75
def pre_process (request ,view_func ):#line:78
    if not OO0O0OO0OOO0OO0O0 (request ):#line:79
        return process_active (request )#line:80
    if '_popup'in request .GET or not request .user .is_authenticated :#line:83
        pass #line:84
    elif hasattr (view_func ,'admin_site'):#line:85
        if request .user and not request .user .is_superuser :#line:87
            request .menus =get_menus (request ,view_func .admin_site )#line:88
    elif 'model_admin'in view_func .__dict__ :#line:89
        request .model_admin =view_func .model_admin #line:92
        if isinstance (view_func .model_admin ,GroupAdmin ):#line:94
            class O0O0OO0OO0000O0O0 :#line:95
                js =('admin/group/js/group.js',)#line:96
            view_func .model_admin .Media =O0O0OO0OO0000O0O0 #line:98
            view_func .model_admin .list_display =('id','name')#line:99
            view_func .model_admin .list_per_page =10 #line:100
        O00000O0OO00OOO00 =request .path #line:101
        OO00OOOO00O0O0O0O =view_func .model_admin .opts #line:103
        OO00OOOOOOOOOO0OO ='admin:{}_{}_changelist'.format (OO00OOOO00O0O0O0O .app_label ,OO00OOOO00O0O0O0O .model_name )#line:104
        if reverse (OO00OOOOOOOOOO0OO )==O00000O0OO00OOO00 :#line:106
            URL_CACHE [request .path ]=view_func .model_admin #line:108
            return process_list (request ,view_func .model_admin )#line:109
def custom_action (request ,model_admin ):#line:112
    ""#line:113
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:116
    O000OO0O0O0OOO000 ={'state':True ,'msg':'操作成功！',}#line:121
    try :#line:122
        O00O0OOO0OO0000OO =request .POST #line:123
        OOO00OO00OOO00OO0 =O00O0OOO0OO0000OO .get ('all')#line:125
        OOO000OOOO0O0OO0O =O00O0OOO0OO0000OO .get ('ids')#line:126
        OO000OO0O0O00000O =O00O0OOO0OO0000OO .get ('key')#line:127
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:133
        OOO0O00O00OOOO00O =model_admin .model #line:134
        OOO0O00OOOOOO0OO0 =OOO0O00O00OOOO00O .objects .get_queryset ()#line:135
        if OOO00OO00OOO00OO0 =='0':#line:138
            O000OO0OO00OO0000 ={}#line:139
            O000OO0OO00OO0000 [OOO0O00O00OOOO00O .id .field_name +'__in']=OOO000OOOO0O0OO0O .split (',')#line:140
            OOO0O00OOOOOO0OO0 =OOO0O00OOOOOO0OO0 .filter (**O000OO0OO00OO0000 )#line:142
        O0O00O00000O0000O =getattr (model_admin ,OO000OO0O0O00000O )#line:144
        O00O00OOOOOO00OO0 =O0O00O00000O0000O (request ,OOO0O00OOOOOO0OO0 )#line:145
        if O00O00OOOOOO00OO0 and isinstance (O00O00OOOOOO00OO0 ,dict ):#line:148
            O000OO0O0O0OOO000 =O00O00OOOOOO00OO0 #line:149
    except Exception as OOOO0OOO0OOOO00OO :#line:151
        O000OO0O0O0OOO000 ={'state':False ,'msg':OOOO0OOO0OOOO00OO .args [0 ]}#line:155
    return HttpResponse (json .dumps (O000OO0O0O0OOO000 ,cls =LazyEncoder ),content_type ='application/json')#line:157
def process_list (request ,model_admin ):#line:160
    OO0OOO0OO000O0OOO =request .POST .get ('action')#line:161
    OO0O0OOOO0OOO0OO0 ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:168
    if OO0OOO0OO000O0OOO and OO0OOO0OO000O0OOO not in OO0O0OOOO0OOO0OO0 :#line:170
        pass #line:171
    elif OO0OOO0OO000O0OOO :#line:172
        OO00OO00OO0OO0O00 ={}#line:174
        OOO0OOO0O0OO0OO0O =model_admin .get_changelist_instance (request )#line:175
        if OOO0OOO0O0OO0OO0O .has_filters :#line:176
            for OOOOO0OOOOOO00OO0 in OOO0OOO0O0OO0OO0O .filter_specs :#line:177
                O00O0O000O000O0O0 =None #line:178
                if hasattr (OOOOO0OOOOOO00OO0 ,'field_path'):#line:179
                    O00O0O000O000O0O0 =OOOOO0OOOOOO00OO0 .field_path #line:180
                elif hasattr (OOOOO0OOOOOO00OO0 ,'parameter_name'):#line:181
                    O00O0O000O000O0O0 =OOOOO0OOOOOO00OO0 .parameter_name #line:182
                elif hasattr (OOOOO0OOOOOO00OO0 ,'lookup_kwarg'):#line:183
                    O00O0O000O000O0O0 =OOOOO0OOOOOO00OO0 .lookup_kwarg #line:184
                if O00O0O000O000O0O0 :#line:185
                    OO00OO00OO0OO0O00 [O00O0O000O000O0O0 ]=OOOOO0OOOOOO00OO0 #line:186
        model_admin .filter_mappers =OO00OO00OO0OO0O00 #line:187
        return OO0O0OOOO0OOO0OO0 [OO0OOO0OO000O0OOO ](request ,model_admin )#line:189
    else :#line:192
        OOO0OOO0O0OO0OO0O =model_admin .get_changelist_instance (request )#line:196
        model_admin .has_filters =OOO0OOO0O0OO0OO0O .has_filters #line:197
        model_admin .filter_specs =OOO0OOO0O0OO0OO0O .filter_specs #line:198
        OO0OOOOOOOOO0000O =[]#line:199
        if model_admin .has_filters :#line:200
            for OOOOO0OOOOOO00OO0 in model_admin .filter_specs :#line:201
                if hasattr (OOOOO0OOOOOO00OO0 ,'field_path'):#line:203
                    OO0OOOOOOOOO0000O .append (OOOOO0OOOOOO00OO0 .field_path )#line:204
                elif hasattr (OOOOO0OOOOOO00OO0 ,'parameter_name'):#line:205
                    OO0OOOOOOOOO0000O .append (OOOOO0OOOOOO00OO0 .parameter_name )#line:206
                elif hasattr (OOOOO0OOOOOO00OO0 ,'lookup_kwarg'):#line:207
                    OO0OOOOOOOOO0000O .append (OOOOO0OOOOOO00OO0 .lookup_kwarg )#line:208
        OO0OOOOO0000OOOO0 =None #line:211
        if hasattr (model_admin ,'Media'):#line:213
            O0O0O00OO0O00OO00 =model_admin .Media #line:214
            OO0OOOOO0000OOOO0 ={}#line:215
            if hasattr (O0O0O00OO0O00OO00 ,'js'):#line:216
                OO00O0OOO00O0OOOO =[]#line:217
                OO0O0OOO0O0OOO0OO =getattr (O0O0O00OO0O00OO00 ,'js')#line:219
                for OOOO000O00O0O0OO0 in OO0O0OOO0O0OOO0OO :#line:221
                    if not OOOO000O00O0O0OO0 .endswith ('import_export/action_formats.js'):#line:222
                        OO00O0OOO00O0OOOO .append (OOOO000O00O0O0OO0 )#line:223
                OO0OOOOO0000OOOO0 ['js']=OO00O0OOO00O0OOOO #line:225
            if hasattr (O0O0O00OO0O00OO00 ,'css'):#line:226
                OO0OOOOO0000OOOO0 ['css']=getattr (O0O0O00OO0O00OO00 ,'css')#line:227
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':OO0OOOOO0000OOOO0 ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OO0OOOOOOOOO0000O ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:246
def delete_data (request ,model_admin ):#line:249
    ""#line:254
    O0OOO0OOOOO0O0000 =model_admin .model #line:256
    OO00O000OO0O0OOOO =O0OOO0OOOOO0O0000 .objects .get_queryset ()#line:257
    OO0OOO0OOO0000O0O =request .POST .get ('ids')#line:258
    O0O0OO00OOOOOOO00 ={'state':True ,'msg':'删除成功！'}#line:263
    if OO0OOO0OOO0000O0O :#line:265
        OO0OOO0OOO0000O0O =OO0OOO0OOO0000O0O .split (',')#line:266
        O0O00O0OO00O0000O ={}#line:267
        O0O00O0OO00O0000O [O0OOO0OOOOO0O0000 .id .field_name +'__in']=OO0OOO0OOO0000O0O #line:268
        OO00O000OO0O0OOOO =OO00O000OO0O0OOOO .filter (**O0O00O0OO00O0000O )#line:269
        try :#line:271
            if hasattr (model_admin ,'delete_queryset'):#line:272
                OO0O0O0O000OO00O0 =getattr (model_admin ,'delete_queryset')(request ,OO00O000OO0O0OOOO )#line:273
                if OO0O0O0O000OO00O0 :#line:274
                    OO00O000OO0O0OOOO =OO0O0O0O000OO00O0 #line:275
                    OO00O000OO0O0OOOO .delete ()#line:276
        except Exception as OOOOO0OOOOOO0O0OO :#line:278
            O0O0OO00OOOOOOO00 ={'state':False ,'msg':OOOOO0OOOOOO0O0OO .args [0 ]}#line:282
    return write (O0O0OO00OOOOOOO00 )#line:283
def list_data (request ,model_admin ):#line:286
    ""#line:292
    """
        admin 中字段设置
        fields_options={
            'id':{
                'fixed':'left',
                'width':'100px',
                'algin':'center'
            }
        }
    """#line:302
    OOO00OO0000O000O0 ={}#line:303
    O0OOOO0O0OOOOO000 =request .POST .get ('current_page')#line:305
    if O0OOOO0O0OOOOO000 :#line:306
        O0OOOO0O0OOOOO000 =int (O0OOOO0O0OOOOO000 )#line:307
    else :#line:308
        O0OOOO0O0OOOOO000 =1 #line:309
    OO0OOO0OOO0000000 ,OO000O00OOOO0OO00 ,O00O00000OOOO000O ,OOOOOOOO000OO0O00 ,OO0OO0OO0O0OO0O0O =get_model_info (model_admin ,request )#line:311
    O0OO00000O00OOO00 ='-'+model_admin .model .id .field_name #line:313
    if 'order_by'in request .POST :#line:315
        O000OOOOO0OO0O000 =request .POST .get ('order_by')#line:316
        if O000OOOOO0OO0O000 and O000OOOOO0OO0O000 !=''and O000OOOOO0OO0O000 !='null':#line:317
            O0OO00000O00OOO00 =O000OOOOO0OO0O000 #line:318
    OO000OOOO0OOOO0O0 =model_admin .model #line:320
    O0O00O0O0OO0OOOO0 =model_admin .get_queryset (request )#line:323
    if not O0O00O0O0OO0OOOO0 :#line:324
        O0O00O0O0OO0OOOO0 =OO000OOOO0OOOO0O0 .objects .get_queryset ()#line:326
    OOOO00O00O0O0000O =request .POST .get ('filters')#line:328
    O0O000OO0O00000OO ={}#line:331
    OO0OO0000000O00OO =request .POST .get ('search')#line:334
    if OO0OO0000000O00OO and OO0OO0000000O00OO !='':#line:335
        OOO0OOOOO00O0O0O0 =Q ()#line:336
        O0OOOOO0000OO000O =model_admin .search_fields #line:337
        for O00O00O0O0OO0OOO0 in O0OOOOO0000OO000O :#line:338
            OOO0OOOOO00O0O0O0 =OOO0OOOOO00O0O0O0 |Q (**{O00O00O0O0OO0OOO0 +"__icontains":OO0OO0000000O00OO })#line:339
        O0O00O0O0OO0OOOO0 =O0O00O0O0OO0OOOO0 .filter (OOO0OOOOO00O0O0O0 )#line:340
    if OOOO00O00O0O0000O :#line:342
        OOOO00O00O0O0000O =json .loads (OOOO00O00O0O0000O )#line:343
        for O0OO0OOO0OO0O0OO0 in OOOO00O00O0O0000O :#line:344
            if O0OO0OOO0OO0O0OO0 in model_admin .filter_mappers :#line:346
                OOO00000O00OOOO00 =model_admin .filter_mappers [O0OO0OOO0OO0O0OO0 ]#line:348
                OOO00000O00OOOO00 .used_parameters =OOOO00O00O0O0000O #line:349
                O0O00O0O0OO0OOOO0 =OOO00000O00OOOO00 .queryset (request ,O0O00O0O0OO0OOOO0 )#line:351
            else :#line:352
                OOO000OO0OOOO0O00 =OOOO00O00O0O0000O .get (O0OO0OOO0OO0O0OO0 )#line:358
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',OOO000OO0OOOO0O00 ):#line:360
                    OO00OOO00OOOOO00O =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OOO000OO0OOOO0O00 )#line:361
                    if OO00OOO00OOOOO00O :#line:362
                        OO00OO000OOO0O00O =OO00OOO00OOOOO00O [0 ]#line:363
                        OOOOOOOOO00000OOO =datetime .datetime .strptime (OO00OO000OOO0O00O ,'%Y-%m-%d %H:%M:%S')#line:364
                        OOO000OO0OOOO0O00 =OOOOOOOOO00000OOO +datetime .timedelta (hours =8 )#line:365
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OOO000OO0OOOO0O00 ):#line:366
                    OOO000OO0OOOO0O00 =datetime .datetime .strptime (OOO000OO0OOOO0O00 ,'%Y-%m-%d %H:%M:%S')#line:368
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',OOO000OO0OOOO0O00 ):#line:369
                    OOO000OO0OOOO0O00 =datetime .datetime .strptime (OOO000OO0OOOO0O00 ,'%Y-%m-%d')#line:371
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',OOO000OO0OOOO0O00 ):#line:372
                    OOO000OO0OOOO0O00 =time .strptime (OOO000OO0OOOO0O00 ,' %H:%M:%S')#line:374
                O0O000OO0O00000OO [O0OO0OOO0OO0O0OO0 ]=OOO000OO0OOOO0O00 #line:375
    OOOO0000OO000O00O =O0O00O0O0OO0OOOO0 .filter (**O0O000OO0O00000OO ).order_by (O0OO00000O00OOO00 )#line:377
    O0O0O00OO00O000OO =model_admin .list_per_page #line:378
    if 'page_size'in request .POST :#line:379
        O0O00OOOO00OOOOOO =int (request .POST .get ('page_size'))#line:380
        if O0O00OOOO00OOOOOO !=0 :#line:381
            O0O0O00OO00O000OO =O0O00OOOO00OOOOOO #line:382
    O000OO00O0000000O =Paginator (OOOO0000OO000O00O ,O0O0O00OO00O000OO )#line:384
    if O0OOOO0O0OOOOO000 >O000OO00O0000000O .num_pages :#line:385
        O0OOOO0O0OOOOO000 =O000OO00O0000000O .num_pages #line:386
    OOO0OOOOO0000OO00 =O000OO00O0000000O .page (O0OOOO0O0OOOOO000 )#line:387
    OO000O0O0OO0O0OOO =OOO0OOOOO0000OO00 .object_list #line:388
    O0OO00O000O00000O =[]#line:392
    OOOO0OO0OO00O00O0 =()#line:393
    if hasattr (model_admin ,'list_display_links'):#line:394
        OOOO0OO0OO00O00O0 =model_admin .list_display_links #line:395
    if not OOOO0OO0OO00O00O0 :#line:397
        OOOO0OO0OO00O00O0 =()#line:399
    for OOOO000O0OOO0OOOO in OO000O0O0OO0O0OOO :#line:401
        O00000OO0OO000OO0 ={}#line:402
        for O000OOOOO0OO0O000 in OO0OOO0OOO0000000 :#line:403
            O0OO0OOO0OO0O0OO0 =O000OOOOO0OO0O000 +'_choices'#line:404
            if O0OO0OOO0OO0O0OO0 in OO0OO0OO0O0OO0O0O :#line:405
                OOOO0000OO0OO0OO0 =getattr (OOOO000O0OOO0OOOO ,O000OOOOO0OO0O000 )#line:406
                OO0O00OO0OOO00OOO =OO0OO0OO0O0OO0O0O [O0OO0OOO0OO0O0OO0 ]#line:407
                if OOOO0000OO0OO0OO0 in OO0O00OO0OOO00OOO :#line:408
                    OOOO0000OO0OO0OO0 =OO0O00OO0OOO00OOO .get (OOOO0000OO0OO0OO0 )#line:409
            elif O000OOOOO0OO0O000 in OO0OO0OO0O0OO0O0O :#line:410
                OOOO0000OO0OO0OO0 =getattr (OOOO000O0OOO0OOOO ,O000OOOOO0OO0O000 )#line:411
                OO0O00OO0OOO00OOO =OO0OO0OO0O0OO0O0O [O000OOOOO0OO0O000 ]#line:412
                if OOOO0000OO0OO0OO0 in OO0O00OO0OOO00OOO :#line:413
                    OOOO0000OO0OO0OO0 =OO0O00OO0OOO00OOO .get (OOOO0000OO0OO0OO0 )#line:414
            else :#line:415
                OOOO0000OO0OO0OO0 =getattr (OOOO000O0OOO0OOOO ,O000OOOOO0OO0O000 )#line:416
            if OOOOOOOO000OO0O00 :#line:420
                OOOO0000OO0OO0OO0 =OOOOOOOO000OO0O00 (OOOO000O0OOO0OOOO ,O000OOOOO0OO0O000 ,OOOO0000OO0OO0OO0 )#line:421
            elif issubclass (OOOO0000OO0OO0OO0 .__class__ ,Model ):#line:422
                OOOO0000OO0OO0OO0 =str (OOOO0000OO0OO0OO0 )#line:423
            if O000OOOOO0OO0O000 in OOOO0OO0OO00O00O0 and not OOOOOOOO000OO0O00 :#line:426
                O000OO0OOO0OO000O =model_admin .opts #line:427
                O000O00O0O0O0000O =reverse ('admin:{}_{}_changelist'.format (O000OO0OOO0OO000O .app_label ,O000OO0OOO0OO000O .model_name ))#line:428
                _OOOO0O00OO00O000O =getattr (OOOO000O0OOO0OOOO ,model_admin .model .id .field_name )#line:429
                O000O00O0O0O0000O =O000O00O0O0O0000O +'{}/change'.format (_OOOO0O00OO00O000O )#line:430
                OOOO0000OO0OO0OO0 =format_html ('<a href="{}">{}</a>',O000O00O0O0O0000O ,str (OOOO0000OO0OO0OO0 ))#line:431
            O00000OO0OO000OO0 [O000OOOOO0OO0O000 ]=OOOO0000OO0OO0OO0 #line:433
        for O0000O0OOO0O0OO0O in OO000O00OOOO0OO00 :#line:435
            try :#line:436
                if O0000O0OOO0O0OO0O =='__str__':#line:437
                    if hasattr (model_admin .model ,'__str__'):#line:438
                        OOOO0000OO0OO0OO0 =getattr (model_admin .model ,'__str__')(OOOO000O0OOO0OOOO )#line:439
                    else :#line:440
                        OOOO0000OO0OO0OO0 =None #line:441
                elif hasattr (model_admin ,O0000O0OOO0O0OO0O ):#line:443
                    OOOO0000OO0OO0OO0 =getattr (model_admin ,O0000O0OOO0O0OO0O ).__call__ (OOOO000O0OOO0OOOO )#line:444
                else :#line:445
                    OOOO0000OO0OO0OO0 =getattr (model_admin .model ,O0000O0OOO0O0OO0O ).__call__ (OOOO000O0OOO0OOOO )#line:446
                if OOOOOOOO000OO0O00 :#line:447
                    OOOO0000OO0OO0OO0 =OOOOOOOO000OO0O00 (OOOO000O0OOO0OOOO ,O0000O0OOO0O0OO0O ,OOOO0000OO0OO0OO0 )#line:448
                O00000OO0OO000OO0 [O0000O0OOO0O0OO0O ]=OOOO0000OO0OO0OO0 #line:449
            except Exception as O000O00O000O0O00O :#line:450
                raise Exception (O000O00O000O0O00O .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (O0000O0OOO0O0OO0O .__qualname__ ,O0000O0OOO0O0OO0O .__qualname__ ))#line:452
        O00000OO0OO000OO0 ['_id']=getattr (OOOO000O0OOO0OOOO ,model_admin .model .id .field_name )#line:454
        O0OO00O000O00000O .append (O00000OO0OO000OO0 )#line:455
    if O0OOOO0O0OOOOO000 <=1 :#line:463
        OO0OOOO00000O00O0 =True #line:464
        if hasattr (model_admin ,'actions_show'):#line:465
            OO0OOOO00000O00O0 =getattr (model_admin ,'actions_show')!=False #line:466
        OOO00OO0000O000O0 ['headers']=O00O00000OOOO000O #line:467
        OOO00OO0000O000O0 ['exts']={'showId':'id'in OO0OOO0OOO0000000 ,'actions_show':OO0OOOO00000O00O0 ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:473
        OOO00OO0000O000O0 ['custom_button']=get_custom_button (request ,model_admin )#line:477
    OOO00OO0000O000O0 ['rows']=O0OO00O000O00000O #line:485
    OOO00OO0000O000O0 ['paginator']={'page_size':O0O0O00OO00O000OO ,'count':O000OO00O0000000O .count ,'page_count':O000OO00O0000000O .num_pages }#line:491
    return write (OOO00OO0000O000O0 )#line:493
def process_active (request ):#line:496
    OO0OO0O0OO0OO0OO0 =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:498
    OOOOOOOOOO0OOO0OO =request .path #line:499
    O0O0O000O000OO00O =request .POST #line:501
    O00O00000OOO000O0 =O0O0O000O000OO00O .get ('action')#line:502
    if O00O00000OOO000O0 :#line:503
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:504
    elif OOOOOOOOOO0OOO0OO not in OO0OO0O0OO0OO0OO0 :#line:505
        return render (request ,'admin/active.html')#line:506
def process_lic (request ):#line:509
    O00O00O00000000O0 =conf .get_device_id ()#line:511
    OOO0OO0O0O0O0O0OO =request .POST .get ('active_code')#line:512
    OO0000000O0OO0OOO =conf .get_server_url ()+'/active'#line:514
    OOO00OO0OOO00OO00 =requests .post (OO0000000O0OO0OOO ,data ={'device_id':O00O00O00000000O0 ,'active_code':OOO0OO0O0O0O0O0OO })#line:518
    if OOO00OO0OOO00OO00 .status_code ==200 :#line:520
        O0OOOO0000O0OOO00 =OOO00OO0OOO00OO00 .json ()#line:521
        if O0OOOO0000O0OOO00 .get ('state')is True :#line:522
            OOOOOOO0OOO00O0O0 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:524
            O00O0OOOOOOO000O0 =open (OOOOOOO0OOO00O0O0 +'/simplepro/simpepro.lic','wb')#line:527
            OO00O0OOO0O00O000 =base64 .b64decode (O0OOOO0000O0OOO00 .get ('license'))#line:530
            OOOO000O000O000O0 =base64 .b64encode (bytes (O0OOOO0000O0OOO00 .get ('private_key'),encoding ='utf8'))#line:531
            O00O0OOOOOOO000O0 .write (struct .pack ('h',len (OO00O0OOO0O00O000 )))#line:533
            O00O0OOOOOOO000O0 .write (struct .pack ('h',len (OOOO000O000O000O0 )))#line:534
            O00O0OOOOOOO000O0 .write (OO00O0OOO0O00O000 )#line:535
            O00O0OOOOOOO000O0 .write (OOOO000O000O000O0 )#line:536
            O00O0OOOOOOO000O0 .close ()#line:537
            O0O0OOO0OOO0OO0O0 (True )#line:538
            print ('写入激活文件，位置：{}'.format (OOOOOOO0OOO00O0O0 +'/simpepro.lic'))#line:540
        return write_obj (O0OOOO0000O0OOO00 )#line:542
    return write ({},'error',False )#line:543
def process_info (request ):#line:546
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:550
