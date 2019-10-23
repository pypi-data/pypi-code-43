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
def O0O0OOO0OOO0OO0O0 (OOO0O00O0000OO000 =False ):#line:28
    try :#line:29
        O000OOOOOOOO0O0OO =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:31
        if not os .path .exists (O000OOOOOOOO0O0OO +'/simplepro/simpepro.lic'):#line:32
            return False #line:33
        global cache_d #line:34
        if OOO0O00O0000OO000 :#line:35
            cache_d =None #line:36
        if cache_d :#line:38
            return cache_d #line:39
        O000OOOO0O0OO0OOO =open (O000OOOOOOOO0O0OO +'/simplepro/simpepro.lic','rb')#line:40
        OO00OOO00OO0O0000 =O000OOOO0O0OO0OOO .read ()#line:41
        OO0O0O0OO00OOO000 ,=struct .unpack ('h',OO00OOO00OO0O0000 [0 :2 ])#line:42
        O00OO000OO0O00O0O ,=struct .unpack ('h',OO00OOO00OO0O0000 [2 :4 ])#line:43
        OOO00O0O0O0O0O00O =OO00OOO00OO0O0000 [4 :OO0O0O0OO00OOO000 +4 ]#line:44
        OO00OOO00000OO0OO =base64 .b64decode (OO00OOO00OO0O0000 [OO0O0O0OO00OOO000 +4 :])#line:46
        O0000000OOO0O00O0 =rsa .PrivateKey .load_pkcs1 (OO00OOO00000OO0OO )#line:48
        O0OO00000OO0O0OOO =rsa .decrypt (OOO00O0O0O0O0O00O ,O0000000OOO0O00O0 ).decode ()#line:49
        OOOOO0OO00O0O0000 =json .loads (O0OO00000OO0O0OOO )#line:50
        cache_d =OOOOO0OO00O0O0000 #line:51
    except Exception as O0OOOOO00OO000O0O :#line:52
        pass #line:53
    return OOOOO0OO00O0O0000 #line:54
def OO0O0OO0OOO0OO0O0 (request ):#line:57
    try :#line:58
        OO0O00000OOOOO0OO =O0O0OOO0OOO0OO0O0 ()#line:59
        O0OOO000OOO0OOOO0 =OO0O00000OOOOO0OO .get ('end_date').split (' ')[0 ]#line:61
        OO0O0OOOO0OOOOO00 =datetime .datetime .strptime (O0OOO000OOO0OOOO0 ,'%Y-%m-%d')#line:62
        O0O0000OO0OOOO0O0 =datetime .datetime .now ()#line:63
        if O0O0000OO0OOOO0O0 >OO0O0OOOO0OOOOO00 :#line:64
            request .msg ='激活码已经过期，请重新购买！'#line:65
            return False #line:66
        O000000O0O0000O00 =OO0O00000OOOOO0OO .get ('device_id')#line:67
        if str (conf .get_device_id ())!=str (O000000O0O0000O00 ):#line:68
            request .msg ='激活码和设备不匹配，请重新激活！'#line:69
            return False #line:70
        return True #line:71
    except Exception as O0O0OOO0OOOOOO0O0 :#line:72
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
            class OO00000OOOO00OOOO :#line:95
                js =('admin/group/js/group.js',)#line:96
            view_func .model_admin .Media =OO00000OOOO00OOOO #line:98
            view_func .model_admin .list_display =('id','name')#line:99
            view_func .model_admin .list_per_page =10 #line:100
        OO0OO00OO00O000OO =request .path #line:101
        O0OOO0OOOO0O0O0OO =view_func .model_admin .opts #line:103
        O0O0OOOOOOO0OOOO0 ='admin:{}_{}_changelist'.format (O0OOO0OOOO0O0O0OO .app_label ,O0OOO0OOOO0O0O0OO .model_name )#line:104
        if reverse (O0O0OOOOOOO0OOOO0 )==OO0OO00OO00O000OO :#line:106
            URL_CACHE [request .path ]=view_func .model_admin #line:108
            return process_list (request ,view_func .model_admin )#line:109
def custom_action (request ,model_admin ):#line:112
    ""#line:113
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:116
    O000O0OOO0O00OO0O ={'state':True ,'msg':'操作成功！',}#line:121
    try :#line:122
        O0OOOO0OO0O00000O =request .POST #line:123
        OOO0OO00O0000O00O =O0OOOO0OO0O00000O .get ('all')#line:125
        OOOO000O0OO000OOO =O0OOOO0OO0O00000O .get ('ids')#line:126
        OOO0OO0O00O00OOOO =O0OOOO0OO0O00000O .get ('key')#line:127
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:133
        O00OOO00OOO0O000O =model_admin .model #line:134
        OOO0OOO0O00OOOO0O =O00OOO00OOO0O000O .objects .get_queryset ()#line:135
        if OOO0OO00O0000O00O =='0':#line:138
            O0O000OO0O00O000O ={}#line:139
            O0O000OO0O00O000O [O00OOO00OOO0O000O .id .field_name +'__in']=OOOO000O0OO000OOO .split (',')#line:140
            OOO0OOO0O00OOOO0O =OOO0OOO0O00OOOO0O .filter (**O0O000OO0O00O000O )#line:142
        OO0O0O0OOO000000O =getattr (model_admin ,OOO0OO0O00O00OOOO )#line:144
        OOO00O0OOOOO0OO0O =OO0O0O0OOO000000O (request ,OOO0OOO0O00OOOO0O )#line:145
        if OOO00O0OOOOO0OO0O and isinstance (OOO00O0OOOOO0OO0O ,dict ):#line:148
            O000O0OOO0O00OO0O =OOO00O0OOOOO0OO0O #line:149
    except Exception as O0O00000OOOOO00O0 :#line:151
        O000O0OOO0O00OO0O ={'state':False ,'msg':O0O00000OOOOO00O0 .args [0 ]}#line:155
    return HttpResponse (json .dumps (O000O0OOO0O00OO0O ,cls =LazyEncoder ),content_type ='application/json')#line:157
def process_list (request ,model_admin ):#line:160
    O0000OO00OO0O00OO =request .POST .get ('action')#line:161
    OO000O0000OO00000 ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:168
    if O0000OO00OO0O00OO and O0000OO00OO0O00OO not in OO000O0000OO00000 :#line:170
        pass #line:171
    elif O0000OO00OO0O00OO :#line:172
        OOOOO00OO000O0OO0 ={}#line:174
        O0O0O0000O0000OOO =model_admin .get_changelist_instance (request )#line:175
        if O0O0O0000O0000OOO .has_filters :#line:176
            for OOO00OOOO00O0OOO0 in O0O0O0000O0000OOO .filter_specs :#line:177
                O0O00OOOOO0O0OOOO =None #line:178
                if hasattr (OOO00OOOO00O0OOO0 ,'field_path'):#line:179
                    O0O00OOOOO0O0OOOO =OOO00OOOO00O0OOO0 .field_path #line:180
                elif hasattr (OOO00OOOO00O0OOO0 ,'parameter_name'):#line:181
                    O0O00OOOOO0O0OOOO =OOO00OOOO00O0OOO0 .parameter_name #line:182
                elif hasattr (OOO00OOOO00O0OOO0 ,'lookup_kwarg'):#line:183
                    O0O00OOOOO0O0OOOO =OOO00OOOO00O0OOO0 .lookup_kwarg #line:184
                if O0O00OOOOO0O0OOOO :#line:185
                    OOOOO00OO000O0OO0 [O0O00OOOOO0O0OOOO ]=OOO00OOOO00O0OOO0 #line:186
        model_admin .filter_mappers =OOOOO00OO000O0OO0 #line:187
        return OO000O0000OO00000 [O0000OO00OO0O00OO ](request ,model_admin )#line:189
    else :#line:192
        O0O0O0000O0000OOO =model_admin .get_changelist_instance (request )#line:196
        model_admin .has_filters =O0O0O0000O0000OOO .has_filters #line:197
        model_admin .filter_specs =O0O0O0000O0000OOO .filter_specs #line:198
        OO00OO00OO0O0000O =[]#line:199
        if model_admin .has_filters :#line:200
            for OOO00OOOO00O0OOO0 in model_admin .filter_specs :#line:201
                if hasattr (OOO00OOOO00O0OOO0 ,'field_path'):#line:203
                    OO00OO00OO0O0000O .append (OOO00OOOO00O0OOO0 .field_path )#line:204
                elif hasattr (OOO00OOOO00O0OOO0 ,'parameter_name'):#line:205
                    OO00OO00OO0O0000O .append (OOO00OOOO00O0OOO0 .parameter_name )#line:206
                elif hasattr (OOO00OOOO00O0OOO0 ,'lookup_kwarg'):#line:207
                    OO00OO00OO0O0000O .append (OOO00OOOO00O0OOO0 .lookup_kwarg )#line:208
        OO00O0O0O0O000OOO =None #line:211
        if hasattr (model_admin ,'Media'):#line:213
            O0OO00OO0O0O00000 =model_admin .Media #line:214
            OO00O0O0O0O000OOO ={}#line:215
            if hasattr (O0OO00OO0O0O00000 ,'js'):#line:216
                OOOOOOO000OO00O0O =[]#line:217
                O00OO0O0OO0O000O0 =getattr (O0OO00OO0O0O00000 ,'js')#line:219
                for O0O0000000OOO0000 in O00OO0O0OO0O000O0 :#line:221
                    if not O0O0000000OOO0000 .endswith ('import_export/action_formats.js'):#line:222
                        OOOOOOO000OO00O0O .append (O0O0000000OOO0000 )#line:223
                OO00O0O0O0O000OOO ['js']=OOOOOOO000OO00O0O #line:225
            if hasattr (O0OO00OO0O0O00000 ,'css'):#line:226
                OO00O0O0O0O000OOO ['css']=getattr (O0OO00OO0O0O00000 ,'css')#line:227
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':OO00O0O0O0O000OOO ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OO00OO00OO0O0000O ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:246
def delete_data (request ,model_admin ):#line:249
    ""#line:254
    O00OO00O0O0OOOOOO =model_admin .model #line:256
    O00O0OO000O0000OO =O00OO00O0O0OOOOOO .objects .get_queryset ()#line:257
    O0OO00OO00OO00000 =request .POST .get ('ids')#line:258
    O00O0O00OO0OOO000 ={'state':True ,'msg':'删除成功！'}#line:263
    if O0OO00OO00OO00000 :#line:265
        O0OO00OO00OO00000 =O0OO00OO00OO00000 .split (',')#line:266
        O0000OOOO00O0OOO0 ={}#line:267
        O0000OOOO00O0OOO0 [O00OO00O0O0OOOOOO .id .field_name +'__in']=O0OO00OO00OO00000 #line:268
        O00O0OO000O0000OO =O00O0OO000O0000OO .filter (**O0000OOOO00O0OOO0 )#line:269
        try :#line:271
            if hasattr (model_admin ,'delete_queryset'):#line:272
                O0000OOO000OO0000 =getattr (model_admin ,'delete_queryset')(request ,O00O0OO000O0000OO )#line:273
                if O0000OOO000OO0000 :#line:274
                    O00O0OO000O0000OO =O0000OOO000OO0000 #line:275
                    O00O0OO000O0000OO .delete ()#line:276
        except Exception as O0O000O00O00OOO00 :#line:278
            O00O0O00OO0OOO000 ={'state':False ,'msg':O0O000O00O00OOO00 .args [0 ]}#line:282
    return write (O00O0O00OO0OOO000 )#line:283
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
    O000O00OO00OOOO00 ={}#line:303
    O00OO000OO00OO00O =request .POST .get ('current_page')#line:305
    if O00OO000OO00OO00O :#line:306
        O00OO000OO00OO00O =int (O00OO000OO00OO00O )#line:307
    else :#line:308
        O00OO000OO00OO00O =1 #line:309
    OOOO00OOOO0OO0O00 ,OOO0OOO0O0O0OOO0O ,OO0O00OO0O0O0O000 ,OO0O00OO00OOOO0OO ,O000O0O00OO00O0OO =get_model_info (model_admin ,request )#line:311
    OOOO000000OO0OO00 ='-'+model_admin .model .id .field_name #line:313
    if 'order_by'in request .POST :#line:315
        OO0OOO0000O000OOO =request .POST .get ('order_by')#line:316
        if OO0OOO0000O000OOO and OO0OOO0000O000OOO !=''and OO0OOO0000O000OOO !='null':#line:317
            OOOO000000OO0OO00 =OO0OOO0000O000OOO #line:318
    OO00OOOOO00OOOO00 =model_admin .model #line:320
    O0O000O0O0OO0O000 =model_admin .get_queryset (request )#line:323
    if not O0O000O0O0OO0O000 :#line:324
        O0O000O0O0OO0O000 =OO00OOOOO00OOOO00 .objects .get_queryset ()#line:326
    O0O00OOOOOOO00O0O =request .POST .get ('filters')#line:328
    O0OO0O0OO0OO0OO00 ={}#line:331
    OO00O00000OO00000 =request .POST .get ('search')#line:334
    if OO00O00000OO00000 and OO00O00000OO00000 !='':#line:335
        O0OOOOO0O00OO0O00 =Q ()#line:336
        OO00000O000O0OO0O =model_admin .search_fields #line:337
        for O0O0O0O0OOOO0OO0O in OO00000O000O0OO0O :#line:338
            O0OOOOO0O00OO0O00 =O0OOOOO0O00OO0O00 |Q (**{O0O0O0O0OOOO0OO0O +"__icontains":OO00O00000OO00000 })#line:339
        O0O000O0O0OO0O000 =O0O000O0O0OO0O000 .filter (O0OOOOO0O00OO0O00 )#line:340
    if O0O00OOOOOOO00O0O :#line:342
        O0O00OOOOOOO00O0O =json .loads (O0O00OOOOOOO00O0O )#line:343
        for O0O0OO00O00O00O0O in O0O00OOOOOOO00O0O :#line:344
            if O0O0OO00O00O00O0O in model_admin .filter_mappers :#line:346
                OO0OOO0OO00O0OOOO =model_admin .filter_mappers [O0O0OO00O00O00O0O ]#line:348
                OO0OOO0OO00O0OOOO .used_parameters =O0O00OOOOOOO00O0O #line:349
                O0O000O0O0OO0O000 =OO0OOO0OO00O0OOOO .queryset (request ,O0O000O0O0OO0O000 )#line:351
            else :#line:352
                O0O00OO0O000O0000 =O0O00OOOOOOO00O0O .get (O0O0OO00O00O00O0O )#line:358
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',O0O00OO0O000O0000 ):#line:360
                    OOOO0OOO000O0OO00 =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0O00OO0O000O0000 )#line:361
                    if OOOO0OOO000O0OO00 :#line:362
                        OO0O0000000OO0O00 =OOOO0OOO000O0OO00 [0 ]#line:363
                        OOO0O0OO000O00O0O =datetime .datetime .strptime (OO0O0000000OO0O00 ,'%Y-%m-%d %H:%M:%S')#line:364
                        O0O00OO0O000O0000 =OOO0O0OO000O00O0O +datetime .timedelta (hours =8 )#line:365
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0O00OO0O000O0000 ):#line:366
                    O0O00OO0O000O0000 =datetime .datetime .strptime (O0O00OO0O000O0000 ,'%Y-%m-%d %H:%M:%S')#line:368
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',O0O00OO0O000O0000 ):#line:369
                    O0O00OO0O000O0000 =datetime .datetime .strptime (O0O00OO0O000O0000 ,'%Y-%m-%d')#line:371
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',O0O00OO0O000O0000 ):#line:372
                    O0O00OO0O000O0000 =time .strptime (O0O00OO0O000O0000 ,' %H:%M:%S')#line:374
                O0OO0O0OO0OO0OO00 [O0O0OO00O00O00O0O ]=O0O00OO0O000O0000 #line:375
    OOOOOO000O0OO00O0 =O0O000O0O0OO0O000 .filter (**O0OO0O0OO0OO0OO00 ).order_by (OOOO000000OO0OO00 )#line:377
    O00O0OOOO0O0O0O00 =model_admin .list_per_page #line:378
    if 'page_size'in request .POST :#line:379
        OOO00O0O0OO00000O =int (request .POST .get ('page_size'))#line:380
        if OOO00O0O0OO00000O !=0 :#line:381
            O00O0OOOO0O0O0O00 =OOO00O0O0OO00000O #line:382
    OO00O0O0O0O00OOOO =Paginator (OOOOOO000O0OO00O0 ,O00O0OOOO0O0O0O00 )#line:384
    if O00OO000OO00OO00O >OO00O0O0O0O00OOOO .num_pages :#line:385
        O00OO000OO00OO00O =OO00O0O0O0O00OOOO .num_pages #line:386
    OO0OO00OOOO0O0OOO =OO00O0O0O0O00OOOO .page (O00OO000OO00OO00O )#line:387
    O00000000O0OOO00O =OO0OO00OOOO0O0OOO .object_list #line:388
    OO00O000O00OO00O0 =[]#line:392
    O000000OOOOOO0O0O =()#line:393
    if hasattr (model_admin ,'list_display_links'):#line:394
        O000000OOOOOO0O0O =model_admin .list_display_links #line:395
    if not O000000OOOOOO0O0O :#line:397
        O000000OOOOOO0O0O =()#line:399
    for OOO0OO0O0000OOOO0 in O00000000O0OOO00O :#line:401
        OO00OO00O0O0OO000 ={}#line:402
        for OO0OOO0000O000OOO in OOOO00OOOO0OO0O00 :#line:403
            O0O0OO00O00O00O0O =OO0OOO0000O000OOO +'_choices'#line:404
            if O0O0OO00O00O00O0O in O000O0O00OO00O0OO :#line:405
                O00O0O0O0OO00O00O =getattr (OOO0OO0O0000OOOO0 ,OO0OOO0000O000OOO )#line:406
                O0000O00OO00O0OO0 =O000O0O00OO00O0OO [O0O0OO00O00O00O0O ]#line:407
                if O00O0O0O0OO00O00O in O0000O00OO00O0OO0 :#line:408
                    O00O0O0O0OO00O00O =O0000O00OO00O0OO0 .get (O00O0O0O0OO00O00O )#line:409
            elif OO0OOO0000O000OOO in O000O0O00OO00O0OO :#line:410
                O00O0O0O0OO00O00O =getattr (OOO0OO0O0000OOOO0 ,OO0OOO0000O000OOO )#line:411
                O0000O00OO00O0OO0 =O000O0O00OO00O0OO [OO0OOO0000O000OOO ]#line:412
                if O00O0O0O0OO00O00O in O0000O00OO00O0OO0 :#line:413
                    O00O0O0O0OO00O00O =O0000O00OO00O0OO0 .get (O00O0O0O0OO00O00O )#line:414
            else :#line:415
                O00O0O0O0OO00O00O =getattr (OOO0OO0O0000OOOO0 ,OO0OOO0000O000OOO )#line:416
            if OO0O00OO00OOOO0OO :#line:420
                O00O0O0O0OO00O00O =OO0O00OO00OOOO0OO (OOO0OO0O0000OOOO0 ,OO0OOO0000O000OOO ,O00O0O0O0OO00O00O )#line:421
            elif issubclass (O00O0O0O0OO00O00O .__class__ ,Model ):#line:422
                O00O0O0O0OO00O00O =str (O00O0O0O0OO00O00O )#line:423
            if OO0OOO0000O000OOO in O000000OOOOOO0O0O and not OO0O00OO00OOOO0OO :#line:426
                OO0O00O0O00000000 =model_admin .opts #line:427
                O00O00000O000OOOO =reverse ('admin:{}_{}_changelist'.format (OO0O00O0O00000000 .app_label ,OO0O00O0O00000000 .model_name ))#line:428
                _O0000OO0O0O0O00O0 =getattr (OOO0OO0O0000OOOO0 ,model_admin .model .id .field_name )#line:429
                O00O00000O000OOOO =O00O00000O000OOOO +'{}/change'.format (_O0000OO0O0O0O00O0 )#line:430
                O00O0O0O0OO00O00O =format_html ('<a href="{}">{}</a>',O00O00000O000OOOO ,str (O00O0O0O0OO00O00O ))#line:431
            OO00OO00O0O0OO000 [OO0OOO0000O000OOO ]=O00O0O0O0OO00O00O #line:433
        for O0OO0OOOO0O000O00 in OOO0OOO0O0O0OOO0O :#line:435
            try :#line:436
                if O0OO0OOOO0O000O00 =='__str__':#line:437
                    if hasattr (model_admin .model ,'__str__'):#line:438
                        O00O0O0O0OO00O00O =getattr (model_admin .model ,'__str__')(OOO0OO0O0000OOOO0 )#line:439
                    else :#line:440
                        O00O0O0O0OO00O00O =None #line:441
                elif hasattr (model_admin ,O0OO0OOOO0O000O00 ):#line:443
                    O00O0O0O0OO00O00O =getattr (model_admin ,O0OO0OOOO0O000O00 ).__call__ (OOO0OO0O0000OOOO0 )#line:444
                else :#line:445
                    O00O0O0O0OO00O00O =getattr (model_admin .model ,O0OO0OOOO0O000O00 ).__call__ (OOO0OO0O0000OOOO0 )#line:446
                if OO0O00OO00OOOO0OO :#line:447
                    O00O0O0O0OO00O00O =OO0O00OO00OOOO0OO (OOO0OO0O0000OOOO0 ,O0OO0OOOO0O000O00 ,O00O0O0O0OO00O00O )#line:448
                OO00OO00O0O0OO000 [O0OO0OOOO0O000O00 ]=O00O0O0O0OO00O00O #line:449
            except Exception as OO0O0OOO00OOO000O :#line:450
                if O0OO0OOOO0O000O00 .__qualname__ :#line:451
                    raise Exception (OO0O0OOO00OOO000O .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (O0OO0OOOO0O000O00 .__qualname__ ,O0OO0OOOO0O000O00 .__qualname__ ))#line:453
                else :#line:454
                    raise OO0O0OOO00OOO000O #line:455
        OO00OO00O0O0OO000 ['_id']=getattr (OOO0OO0O0000OOOO0 ,model_admin .model .id .field_name )#line:457
        OO00O000O00OO00O0 .append (OO00OO00O0O0OO000 )#line:458
    if O00OO000OO00OO00O <=1 :#line:466
        OOOO0OO0OO00OOOO0 =True #line:467
        if hasattr (model_admin ,'actions_show'):#line:468
            OOOO0OO0OO00OOOO0 =getattr (model_admin ,'actions_show')!=False #line:469
        O000O00OO00OOOO00 ['headers']=OO0O00OO0O0O0O000 #line:470
        O000O00OO00OOOO00 ['exts']={'showId':'id'in OOOO00OOOO0OO0O00 ,'actions_show':OOOO0OO0OO00OOOO0 ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:476
        O000O00OO00OOOO00 ['custom_button']=get_custom_button (request ,model_admin )#line:480
    O000O00OO00OOOO00 ['rows']=OO00O000O00OO00O0 #line:488
    O000O00OO00OOOO00 ['paginator']={'page_size':O00O0OOOO0O0O0O00 ,'count':OO00O0O0O0O00OOOO .count ,'page_count':OO00O0O0O0O00OOOO .num_pages }#line:494
    return write (O000O00OO00OOOO00 )#line:496
def process_active (request ):#line:499
    OOO0O0O00OOO0O0O0 =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:501
    O00O0OOOO000O0000 =request .path #line:502
    O00OOO0OOOOO0O0O0 =request .POST #line:504
    OOO0O00OOOOOOOOO0 =O00OOO0OOOOO0O0O0 .get ('action')#line:505
    if OOO0O00OOOOOOOOO0 :#line:506
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:507
    elif O00O0OOOO000O0000 not in OOO0O0O00OOO0O0O0 :#line:508
        return render (request ,'admin/active.html')#line:509
def process_lic (request ):#line:512
    O0OOO0OO0OOOO00OO =conf .get_device_id ()#line:514
    O0O0OOO00OOO000OO =request .POST .get ('active_code')#line:515
    O0O0OO0O0OO00O0OO =conf .get_server_url ()+'/active'#line:517
    O0O000O000OO00OO0 =requests .post (O0O0OO0O0OO00O0OO ,data ={'device_id':O0OOO0OO0OOOO00OO ,'active_code':O0O0OOO00OOO000OO })#line:521
    if O0O000O000OO00OO0 .status_code ==200 :#line:523
        O0O0O0O00OO0000O0 =O0O000O000OO00OO0 .json ()#line:524
        if O0O0O0O00OO0000O0 .get ('state')is True :#line:525
            O00O00OO0OO0O0OOO =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:527
            O0O00OOOO0OO0OO0O =open (O00O00OO0OO0O0OOO +'/simplepro/simpepro.lic','wb')#line:530
            OO0OOOO0OO00O0OO0 =base64 .b64decode (O0O0O0O00OO0000O0 .get ('license'))#line:533
            OOOO00O0OO00O000O =base64 .b64encode (bytes (O0O0O0O00OO0000O0 .get ('private_key'),encoding ='utf8'))#line:534
            O0O00OOOO0OO0OO0O .write (struct .pack ('h',len (OO0OOOO0OO00O0OO0 )))#line:536
            O0O00OOOO0OO0OO0O .write (struct .pack ('h',len (OOOO00O0OO00O000O )))#line:537
            O0O00OOOO0OO0OO0O .write (OO0OOOO0OO00O0OO0 )#line:538
            O0O00OOOO0OO0OO0O .write (OOOO00O0OO00O000O )#line:539
            O0O00OOOO0OO0OO0O .close ()#line:540
            O0O0OOO0OOO0OO0O0 (True )#line:541
            print ('写入激活文件，位置：{}'.format (O00O00OO0OO0O0OOO +'/simpepro.lic'))#line:543
        return write_obj (O0O0O0O00OO0000O0 )#line:545
    return write ({},'error',False )#line:546
def process_info (request ):#line:549
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:553
