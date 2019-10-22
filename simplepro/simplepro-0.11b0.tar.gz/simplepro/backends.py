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
def O0O0OOO0OOO0OO0O0 (O00OO00OO00OO0O00 =False ):#line:28
    try :#line:29
        O0000O00O0O00OO00 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:31
        if not os .path .exists (O0000O00O0O00OO00 +'/simplepro/simpepro.lic'):#line:32
            return False #line:33
        global cache_d #line:34
        if O00OO00OO00OO0O00 :#line:35
            cache_d =None #line:36
        if cache_d :#line:38
            return cache_d #line:39
        O0OOOOO000OOOO0OO =open (O0000O00O0O00OO00 +'/simplepro/simpepro.lic','rb')#line:40
        O0OOO00OO0OO000O0 =O0OOOOO000OOOO0OO .read ()#line:41
        O0O00OO0OO0OO00OO ,=struct .unpack ('h',O0OOO00OO0OO000O0 [0 :2 ])#line:42
        O0O00000O0O000O0O ,=struct .unpack ('h',O0OOO00OO0OO000O0 [2 :4 ])#line:43
        OO0000O0OO0O0OOO0 =O0OOO00OO0OO000O0 [4 :O0O00OO0OO0OO00OO +4 ]#line:44
        O000O0O00O0OO00OO =base64 .b64decode (O0OOO00OO0OO000O0 [O0O00OO0OO0OO00OO +4 :])#line:46
        OO0000OO0OOOO0000 =rsa .PrivateKey .load_pkcs1 (O000O0O00O0OO00OO )#line:48
        O0OO000OOOO0OO000 =rsa .decrypt (OO0000O0OO0O0OOO0 ,OO0000OO0OOOO0000 ).decode ()#line:49
        O0O0O0O0O0O00O00O =json .loads (O0OO000OOOO0OO000 )#line:50
        cache_d =O0O0O0O0O0O00O00O #line:51
    except Exception as OO0OO000O0O0OO000 :#line:52
        pass #line:53
    return O0O0O0O0O0O00O00O #line:54
def OO0O0OO0OOO0OO0O0 (request ):#line:57
    try :#line:58
        O0O00000OO00OOO00 =O0O0OOO0OOO0OO0O0 ()#line:59
        O000OOO0O0OOOOO0O =O0O00000OO00OOO00 .get ('end_date').split (' ')[0 ]#line:61
        OOO00O0O0O000O0OO =datetime .datetime .strptime (O000OOO0O0OOOOO0O ,'%Y-%m-%d')#line:62
        OO0O00000O0000000 =datetime .datetime .now ()#line:63
        if OO0O00000O0000000 >OOO00O0O0O000O0OO :#line:64
            request .msg ='激活码已经过期，请重新购买！'#line:65
            return False #line:66
        O0O00OO000OO000OO =O0O00000OO00OOO00 .get ('device_id')#line:67
        if str (conf .get_device_id ())!=str (O0O00OO000OO000OO ):#line:68
            request .msg ='激活码和设备不匹配，请重新激活！'#line:69
            return False #line:70
        return True #line:71
    except Exception as O00O000O0OOOOO0O0 :#line:72
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
            class O00OOOOO00O0O0O0O :#line:95
                js =('admin/group/js/group.js',)#line:96
            view_func .model_admin .Media =O00OOOOO00O0O0O0O #line:98
            view_func .model_admin .list_display =('id','name')#line:99
            view_func .model_admin .list_per_page =10 #line:100
        OO0O00O00000OOOOO =request .path #line:101
        OO00O0OOO00O000OO =view_func .model_admin .opts #line:103
        OOO0OOO0OO0000OO0 ='admin:{}_{}_changelist'.format (OO00O0OOO00O000OO .app_label ,OO00O0OOO00O000OO .model_name )#line:104
        if reverse (OOO0OOO0OO0000OO0 )==OO0O00O00000OOOOO :#line:106
            URL_CACHE [request .path ]=view_func .model_admin #line:108
            return process_list (request ,view_func .model_admin )#line:109
def custom_action (request ,model_admin ):#line:112
    ""#line:113
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:116
    OOO0OO00O00OO000O ={'state':True ,'msg':'操作成功！',}#line:121
    try :#line:122
        O0OOOO0O0000O0OOO =request .POST #line:123
        O0OOOO0OOO0O00O0O =O0OOOO0O0000O0OOO .get ('all')#line:125
        O0O0000OOO000OOOO =O0OOOO0O0000O0OOO .get ('ids')#line:126
        O00O0O0O0OO000OOO =O0OOOO0O0000O0OOO .get ('key')#line:127
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:133
        O000O0O0OO0000OOO =model_admin .model #line:134
        OO0OOOO00OOOO0O00 =O000O0O0OO0000OOO .objects .get_queryset ()#line:135
        if O0OOOO0OOO0O00O0O =='0':#line:138
            O0000O00O0OO0O0O0 ={}#line:139
            O0000O00O0OO0O0O0 [O000O0O0OO0000OOO .id .field_name +'__in']=O0O0000OOO000OOOO .split (',')#line:140
            OO0OOOO00OOOO0O00 =OO0OOOO00OOOO0O00 .filter (**O0000O00O0OO0O0O0 )#line:142
        O0OO000000OOO0O00 =getattr (model_admin ,O00O0O0O0OO000OOO )#line:144
        O00000O0OOO0O0OOO =O0OO000000OOO0O00 (request ,OO0OOOO00OOOO0O00 )#line:145
        if O00000O0OOO0O0OOO and isinstance (O00000O0OOO0O0OOO ,dict ):#line:148
            OOO0OO00O00OO000O =O00000O0OOO0O0OOO #line:149
    except Exception as OOOO000O0OO0O0O00 :#line:151
        OOO0OO00O00OO000O ={'state':False ,'msg':OOOO000O0OO0O0O00 .args [0 ]}#line:155
    return HttpResponse (json .dumps (OOO0OO00O00OO000O ,cls =LazyEncoder ),content_type ='application/json')#line:157
def process_list (request ,model_admin ):#line:160
    O00O0O0OOOOO00OO0 =request .POST .get ('action')#line:161
    O00OO0OO00O0O0O00 ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:168
    if O00O0O0OOOOO00OO0 and O00O0O0OOOOO00OO0 not in O00OO0OO00O0O0O00 :#line:170
        pass #line:171
    elif O00O0O0OOOOO00OO0 :#line:172
        OOO000OO00OO00OOO ={}#line:174
        OOO00OO0OOOO0OO00 =model_admin .get_changelist_instance (request )#line:175
        if OOO00OO0OOOO0OO00 .has_filters :#line:176
            for OOO0OO0OOO00000O0 in OOO00OO0OOOO0OO00 .filter_specs :#line:177
                OO0O0OOO0O0000O0O =None #line:178
                if hasattr (OOO0OO0OOO00000O0 ,'field_path'):#line:179
                    OO0O0OOO0O0000O0O =OOO0OO0OOO00000O0 .field_path #line:180
                elif hasattr (OOO0OO0OOO00000O0 ,'parameter_name'):#line:181
                    OO0O0OOO0O0000O0O =OOO0OO0OOO00000O0 .parameter_name #line:182
                elif hasattr (OOO0OO0OOO00000O0 ,'lookup_kwarg'):#line:183
                    OO0O0OOO0O0000O0O =OOO0OO0OOO00000O0 .lookup_kwarg #line:184
                if OO0O0OOO0O0000O0O :#line:185
                    OOO000OO00OO00OOO [OO0O0OOO0O0000O0O ]=OOO0OO0OOO00000O0 #line:186
        model_admin .filter_mappers =OOO000OO00OO00OOO #line:187
        return O00OO0OO00O0O0O00 [O00O0O0OOOOO00OO0 ](request ,model_admin )#line:189
    else :#line:192
        OOO00OO0OOOO0OO00 =model_admin .get_changelist_instance (request )#line:196
        model_admin .has_filters =OOO00OO0OOOO0OO00 .has_filters #line:197
        model_admin .filter_specs =OOO00OO0OOOO0OO00 .filter_specs #line:198
        O0O0O000O00O0OO00 =[]#line:199
        if model_admin .has_filters :#line:200
            for OOO0OO0OOO00000O0 in model_admin .filter_specs :#line:201
                if hasattr (OOO0OO0OOO00000O0 ,'field_path'):#line:203
                    O0O0O000O00O0OO00 .append (OOO0OO0OOO00000O0 .field_path )#line:204
                elif hasattr (OOO0OO0OOO00000O0 ,'parameter_name'):#line:205
                    O0O0O000O00O0OO00 .append (OOO0OO0OOO00000O0 .parameter_name )#line:206
                elif hasattr (OOO0OO0OOO00000O0 ,'lookup_kwarg'):#line:207
                    O0O0O000O00O0OO00 .append (OOO0OO0OOO00000O0 .lookup_kwarg )#line:208
        OO0O0O0O0O0O0000O =None #line:211
        if hasattr (model_admin ,'Media'):#line:213
            OO0OO0OOOO00O0000 =model_admin .Media #line:214
            OO0O0O0O0O0O0000O ={}#line:215
            if hasattr (OO0OO0OOOO00O0000 ,'js'):#line:216
                O0OO0OO0OO0OOO000 =[]#line:217
                OOOOO0OOOO0000OOO =getattr (OO0OO0OOOO00O0000 ,'js')#line:219
                for OOOOO0O00OOO00OOO in OOOOO0OOOO0000OOO :#line:221
                    if not OOOOO0O00OOO00OOO .endswith ('import_export/action_formats.js'):#line:222
                        O0OO0OO0OO0OOO000 .append (OOOOO0O00OOO00OOO )#line:223
                OO0O0O0O0O0O0000O ['js']=O0OO0OO0OO0OOO000 #line:225
            if hasattr (OO0OO0OOOO00O0000 ,'css'):#line:226
                OO0O0O0O0O0O0000O ['css']=getattr (OO0OO0OOOO00O0000 ,'css')#line:227
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':OO0O0O0O0O0O0000O ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (O0O0O000O00O0OO00 ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:246
def delete_data (request ,model_admin ):#line:249
    ""#line:254
    O0000O00O0OO0OOOO =model_admin .model #line:256
    OOO0O000O00O000OO =O0000O00O0OO0OOOO .objects .get_queryset ()#line:257
    OOOO000OO00OOO0O0 =request .POST .get ('ids')#line:258
    OO0000OO00OOO0O0O ={'state':True ,'msg':'删除成功！'}#line:263
    if OOOO000OO00OOO0O0 :#line:265
        OOOO000OO00OOO0O0 =OOOO000OO00OOO0O0 .split (',')#line:266
        OO0OO0000O0O0OO0O ={}#line:267
        OO0OO0000O0O0OO0O [O0000O00O0OO0OOOO .id .field_name +'__in']=OOOO000OO00OOO0O0 #line:268
        OOO0O000O00O000OO =OOO0O000O00O000OO .filter (**OO0OO0000O0O0OO0O )#line:269
        try :#line:271
            if hasattr (model_admin ,'delete_queryset'):#line:272
                OOO000OOO000OOOO0 =getattr (model_admin ,'delete_queryset')(request ,OOO0O000O00O000OO )#line:273
                if OOO000OOO000OOOO0 :#line:274
                    OOO0O000O00O000OO =OOO000OOO000OOOO0 #line:275
                    OOO0O000O00O000OO .delete ()#line:276
        except Exception as O000OOOOO0OO00OOO :#line:278
            OO0000OO00OOO0O0O ={'state':False ,'msg':O000OOOOO0OO00OOO .args [0 ]}#line:282
    return write (OO0000OO00OOO0O0O )#line:283
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
    O00OO00O0OOO0OOOO ={}#line:303
    OOO00000O0OO0O0O0 =request .POST .get ('current_page')#line:305
    if OOO00000O0OO0O0O0 :#line:306
        OOO00000O0OO0O0O0 =int (OOO00000O0OO0O0O0 )#line:307
    else :#line:308
        OOO00000O0OO0O0O0 =1 #line:309
    OO0000000OOOO0O0O ,O0000O0OOOOOOOOO0 ,O0OO000OOO00O000O ,OOOOO0OO00O00000O ,OOOO0O0OOOOOO0O00 =get_model_info (model_admin ,request )#line:311
    OOO00OO000O0000OO ='-'+model_admin .model .id .field_name #line:313
    if 'order_by'in request .POST :#line:315
        OO000O00OOOO0OO00 =request .POST .get ('order_by')#line:316
        if OO000O00OOOO0OO00 and OO000O00OOOO0OO00 !=''and OO000O00OOOO0OO00 !='null':#line:317
            OOO00OO000O0000OO =OO000O00OOOO0OO00 #line:318
    OO0OO0O0O00O000OO =model_admin .model #line:320
    O000000O0O0O0O000 =model_admin .get_queryset (request )#line:323
    if not O000000O0O0O0O000 :#line:324
        O000000O0O0O0O000 =OO0OO0O0O00O000OO .objects .get_queryset ()#line:326
    OOO0OO00OO00O0OO0 =request .POST .get ('filters')#line:328
    OOOO00OO00OO0OO0O ={}#line:331
    O000OO0O000OO000O =request .POST .get ('search')#line:334
    if O000OO0O000OO000O and O000OO0O000OO000O !='':#line:335
        OO00OOO0O00OO0OOO =Q ()#line:336
        O0OO0O0O00000O000 =model_admin .search_fields #line:337
        for O0O0000OOO000O0OO in O0OO0O0O00000O000 :#line:338
            OO00OOO0O00OO0OOO =OO00OOO0O00OO0OOO |Q (**{O0O0000OOO000O0OO +"__icontains":O000OO0O000OO000O })#line:339
        O000000O0O0O0O000 =O000000O0O0O0O000 .filter (OO00OOO0O00OO0OOO )#line:340
    if OOO0OO00OO00O0OO0 :#line:342
        OOO0OO00OO00O0OO0 =json .loads (OOO0OO00OO00O0OO0 )#line:343
        for OO000O00O0OOO0OOO in OOO0OO00OO00O0OO0 :#line:344
            if OO000O00O0OOO0OOO in model_admin .filter_mappers :#line:346
                O00O0O000O0OOOO0O =model_admin .filter_mappers [OO000O00O0OOO0OOO ]#line:348
                O00O0O000O0OOOO0O .used_parameters =OOO0OO00OO00O0OO0 #line:349
                O000000O0O0O0O000 =O00O0O000O0OOOO0O .queryset (request ,O000000O0O0O0O000 )#line:351
            else :#line:352
                O0OOOOOOOOOOO00O0 =OOO0OO00OO00O0OO0 .get (OO000O00O0OOO0OOO )#line:358
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',O0OOOOOOOOOOO00O0 ):#line:360
                    O000O000OOOO00OO0 =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0OOOOOOOOOOO00O0 )#line:361
                    if O000O000OOOO00OO0 :#line:362
                        O0OOOOO0OO00000O0 =O000O000OOOO00OO0 [0 ]#line:363
                        O00OOO0O000O00000 =datetime .datetime .strptime (O0OOOOO0OO00000O0 ,'%Y-%m-%d %H:%M:%S')#line:364
                        O0OOOOOOOOOOO00O0 =O00OOO0O000O00000 +datetime .timedelta (hours =8 )#line:365
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0OOOOOOOOOOO00O0 ):#line:366
                    O0OOOOOOOOOOO00O0 =datetime .datetime .strptime (O0OOOOOOOOOOO00O0 ,'%Y-%m-%d %H:%M:%S')#line:368
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',O0OOOOOOOOOOO00O0 ):#line:369
                    O0OOOOOOOOOOO00O0 =datetime .datetime .strptime (O0OOOOOOOOOOO00O0 ,'%Y-%m-%d')#line:371
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',O0OOOOOOOOOOO00O0 ):#line:372
                    O0OOOOOOOOOOO00O0 =time .strptime (O0OOOOOOOOOOO00O0 ,' %H:%M:%S')#line:374
                OOOO00OO00OO0OO0O [OO000O00O0OOO0OOO ]=O0OOOOOOOOOOO00O0 #line:375
    O000000O0OO0OOOOO =O000000O0O0O0O000 .filter (**OOOO00OO00OO0OO0O ).order_by (OOO00OO000O0000OO )#line:377
    O0O0O00OO00OO00OO =model_admin .list_per_page #line:378
    if 'page_size'in request .POST :#line:379
        O00000O0O0OO00000 =int (request .POST .get ('page_size'))#line:380
        if O00000O0O0OO00000 !=0 :#line:381
            O0O0O00OO00OO00OO =O00000O0O0OO00000 #line:382
    OO0OOO00OOO0O0O0O =Paginator (O000000O0OO0OOOOO ,O0O0O00OO00OO00OO )#line:384
    if OOO00000O0OO0O0O0 >OO0OOO00OOO0O0O0O .num_pages :#line:385
        OOO00000O0OO0O0O0 =OO0OOO00OOO0O0O0O .num_pages #line:386
    OOO0O00OO00000000 =OO0OOO00OOO0O0O0O .page (OOO00000O0OO0O0O0 )#line:387
    OO00OOO0000O0O0O0 =OOO0O00OO00000000 .object_list #line:388
    O0OOO0OO000000O0O =[]#line:392
    OO0O00O00O00O0OOO =()#line:393
    if hasattr (model_admin ,'list_display_links'):#line:394
        OO0O00O00O00O0OOO =model_admin .list_display_links #line:395
    if not OO0O00O00O00O0OOO :#line:397
        OO0O00O00O00O0OOO =()#line:399
    for OOOO0000O00O0OOO0 in OO00OOO0000O0O0O0 :#line:401
        O0O0O0O0O000O0O0O ={}#line:402
        for OO000O00OOOO0OO00 in OO0000000OOOO0O0O :#line:403
            OO000O00O0OOO0OOO =OO000O00OOOO0OO00 +'_choices'#line:404
            if OO000O00O0OOO0OOO in OOOO0O0OOOOOO0O00 :#line:405
                O0OO00OOO0O00OO00 =getattr (OOOO0000O00O0OOO0 ,OO000O00OOOO0OO00 )#line:406
                O0O000O0OO0OOO00O =OOOO0O0OOOOOO0O00 [OO000O00O0OOO0OOO ]#line:407
                if O0OO00OOO0O00OO00 in O0O000O0OO0OOO00O :#line:408
                    O0OO00OOO0O00OO00 =O0O000O0OO0OOO00O .get (O0OO00OOO0O00OO00 )#line:409
            elif OO000O00OOOO0OO00 in OOOO0O0OOOOOO0O00 :#line:410
                O0OO00OOO0O00OO00 =getattr (OOOO0000O00O0OOO0 ,OO000O00OOOO0OO00 )#line:411
                O0O000O0OO0OOO00O =OOOO0O0OOOOOO0O00 [OO000O00OOOO0OO00 ]#line:412
                if O0OO00OOO0O00OO00 in O0O000O0OO0OOO00O :#line:413
                    O0OO00OOO0O00OO00 =O0O000O0OO0OOO00O .get (O0OO00OOO0O00OO00 )#line:414
            else :#line:415
                O0OO00OOO0O00OO00 =getattr (OOOO0000O00O0OOO0 ,OO000O00OOOO0OO00 )#line:416
            if OOOOO0OO00O00000O :#line:420
                O0OO00OOO0O00OO00 =OOOOO0OO00O00000O (OOOO0000O00O0OOO0 ,OO000O00OOOO0OO00 ,O0OO00OOO0O00OO00 )#line:421
            elif issubclass (O0OO00OOO0O00OO00 .__class__ ,Model ):#line:422
                O0OO00OOO0O00OO00 =str (O0OO00OOO0O00OO00 )#line:423
            if OO000O00OOOO0OO00 in OO0O00O00O00O0OOO and not OOOOO0OO00O00000O :#line:426
                OOOO0OO0OO00O000O =model_admin .opts #line:427
                O00O0O00O000O0000 =reverse ('admin:{}_{}_changelist'.format (OOOO0OO0OO00O000O .app_label ,OOOO0OO0OO00O000O .model_name ))#line:428
                _OO00O0000O0000OOO =getattr (OOOO0000O00O0OOO0 ,model_admin .model .id .field_name )#line:429
                O00O0O00O000O0000 =O00O0O00O000O0000 +'{}/change'.format (_OO00O0000O0000OOO )#line:430
                O0OO00OOO0O00OO00 =format_html ('<a href="{}">{}</a>',O00O0O00O000O0000 ,str (O0OO00OOO0O00OO00 ))#line:431
            O0O0O0O0O000O0O0O [OO000O00OOOO0OO00 ]=O0OO00OOO0O00OO00 #line:433
        for O00OO0000O0O0OO00 in O0000O0OOOOOOOOO0 :#line:435
            try :#line:436
                if O00OO0000O0O0OO00 =='__str__':#line:437
                    if hasattr (model_admin .model ,'__str__'):#line:438
                        O0OO00OOO0O00OO00 =getattr (model_admin .model ,'__str__')(OOOO0000O00O0OOO0 )#line:439
                    else :#line:440
                        O0OO00OOO0O00OO00 =None #line:441
                elif hasattr (model_admin ,O00OO0000O0O0OO00 ):#line:443
                    O0OO00OOO0O00OO00 =getattr (model_admin ,O00OO0000O0O0OO00 ).__call__ (OOOO0000O00O0OOO0 )#line:444
                else :#line:445
                    O0OO00OOO0O00OO00 =getattr (model_admin .model ,O00OO0000O0O0OO00 ).__call__ (OOOO0000O00O0OOO0 )#line:446
                if OOOOO0OO00O00000O :#line:447
                    O0OO00OOO0O00OO00 =OOOOO0OO00O00000O (OOOO0000O00O0OOO0 ,O00OO0000O0O0OO00 ,O0OO00OOO0O00OO00 )#line:448
                O0O0O0O0O000O0O0O [O00OO0000O0O0OO00 ]=O0OO00OOO0O00OO00 #line:449
            except Exception as OO0O0O000OOO0O00O :#line:450
                raise Exception (OO0O0O000OOO0O00O .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (O00OO0000O0O0OO00 .__qualname__ ,O00OO0000O0O0OO00 .__qualname__ ))#line:452
        O0O0O0O0O000O0O0O ['_id']=getattr (OOOO0000O00O0OOO0 ,model_admin .model .id .field_name )#line:454
        O0OOO0OO000000O0O .append (O0O0O0O0O000O0O0O )#line:455
    if OOO00000O0OO0O0O0 <=1 :#line:463
        O00OOOOOOO00O00O0 =True #line:464
        if hasattr (model_admin ,'actions_show'):#line:465
            O00OOOOOOO00O00O0 =getattr (model_admin ,'actions_show')!=False #line:466
        O00OO00O0OOO0OOOO ['headers']=O0OO000OOO00O000O #line:467
        O00OO00O0OOO0OOOO ['exts']={'showId':'id'in OO0000000OOOO0O0O ,'actions_show':O00OOOOOOO00O00O0 ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:473
        O00OO00O0OOO0OOOO ['custom_button']=get_custom_button (request ,model_admin )#line:477
    O00OO00O0OOO0OOOO ['rows']=O0OOO0OO000000O0O #line:485
    O00OO00O0OOO0OOOO ['paginator']={'page_size':O0O0O00OO00OO00OO ,'count':OO0OOO00OOO0O0O0O .count ,'page_count':OO0OOO00OOO0O0O0O .num_pages }#line:491
    return write (O00OO00O0OOO0OOOO )#line:493
def process_active (request ):#line:496
    O0OO0OO0OOOO0OOOO =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:498
    O0O0O00O000OO000O =request .path #line:499
    OOOOOOOOO0OO00O0O =request .POST #line:501
    O000O0O00O0OO000O =OOOOOOOOO0OO00O0O .get ('action')#line:502
    if O000O0O00O0OO000O :#line:503
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:504
    elif O0O0O00O000OO000O not in O0OO0OO0OOOO0OOOO :#line:505
        return render (request ,'admin/active.html')#line:506
def process_lic (request ):#line:509
    OO0O000O0O0O0OOOO =conf .get_device_id ()#line:511
    O000O0OO0OO00O0OO =request .POST .get ('active_code')#line:512
    O00O0O0O00OOO0O0O =conf .get_server_url ()+'/active'#line:514
    O0O0O000O00OO0OO0 =requests .post (O00O0O0O00OOO0O0O ,data ={'device_id':OO0O000O0O0O0OOOO ,'active_code':O000O0OO0OO00O0OO })#line:518
    if O0O0O000O00OO0OO0 .status_code ==200 :#line:520
        OOOO000OO0000OO00 =O0O0O000O00OO0OO0 .json ()#line:521
        if OOOO000OO0000OO00 .get ('state')is True :#line:522
            OOO0OOOOO0OOOOO0O =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:524
            O0000OO000OOO0OOO =open (OOO0OOOOO0OOOOO0O +'/simplepro/simpepro.lic','wb')#line:527
            O00000O00O0O00000 =base64 .b64decode (OOOO000OO0000OO00 .get ('license'))#line:530
            OOO0000OO0O0OOOO0 =base64 .b64encode (bytes (OOOO000OO0000OO00 .get ('private_key'),encoding ='utf8'))#line:531
            O0000OO000OOO0OOO .write (struct .pack ('h',len (O00000O00O0O00000 )))#line:533
            O0000OO000OOO0OOO .write (struct .pack ('h',len (OOO0000OO0O0OOOO0 )))#line:534
            O0000OO000OOO0OOO .write (O00000O00O0O00000 )#line:535
            O0000OO000OOO0OOO .write (OOO0000OO0O0OOOO0 )#line:536
            O0000OO000OOO0OOO .close ()#line:537
            O0O0OOO0OOO0OO0O0 (True )#line:538
            print ('写入激活文件，位置：{}'.format (OOO0OOOOO0OOOOO0O +'/simpepro.lic'))#line:540
        return write_obj (OOOO000OO0000OO00 )#line:542
    return write ({},'error',False )#line:543
def process_info (request ):#line:546
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:550
