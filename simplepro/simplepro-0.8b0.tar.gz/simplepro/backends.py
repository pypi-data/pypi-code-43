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
from simplepro import conf #line:16
from simplepro .utils import LazyEncoder ,has_permission ,write ,get_model_info ,search_placeholder ,get_custom_button ,get_menus ,write_obj #line:18
URL_CACHE ={}#line:20
import base64 #line:22
cache_d =None #line:24
def O0O0OOO0OOO0OO0O0 (OOO0OOOOOO00OOO0O =False ):#line:27
    try :#line:28
        O000O00OO0O0OO0O0 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:30
        if not os .path .exists (O000O00OO0O0OO0O0 +'/simplepro/simpepro.lic'):#line:31
            return False #line:32
        global cache_d #line:33
        if OOO0OOOOOO00OOO0O :#line:34
            cache_d =None #line:35
        if cache_d :#line:37
            return cache_d #line:38
        O0OO0OO0OOO000000 =open (O000O00OO0O0OO0O0 +'/simplepro/simpepro.lic','rb')#line:39
        O0000OO00000O000O =O0OO0OO0OOO000000 .read ()#line:40
        OOO0O0OO00OOOOOO0 ,=struct .unpack ('h',O0000OO00000O000O [0 :2 ])#line:41
        O000OO0OOOOOOO00O ,=struct .unpack ('h',O0000OO00000O000O [2 :4 ])#line:42
        O0OOOOO00O00O0O0O =O0000OO00000O000O [4 :OOO0O0OO00OOOOOO0 +4 ]#line:43
        O00000O0OO0O000O0 =base64 .b64decode (O0000OO00000O000O [OOO0O0OO00OOOOOO0 +4 :])#line:45
        O000OOO0OOO0OO000 =rsa .PrivateKey .load_pkcs1 (O00000O0OO0O000O0 )#line:47
        OO0OOO0OO0O0O0O0O =rsa .decrypt (O0OOOOO00O00O0O0O ,O000OOO0OOO0OO000 ).decode ()#line:48
        OO0O0O0O0OOOOO00O =json .loads (OO0OOO0OO0O0O0O0O )#line:49
        cache_d =OO0O0O0O0OOOOO00O #line:50
    except Exception as OO0OOOOOOOO00OO00 :#line:51
        pass #line:52
    return OO0O0O0O0OOOOO00O #line:53
def OO0O0OO0OOO0OO0O0 (request ):#line:56
    try :#line:57
        OO0000OO00O0OO0OO =O0O0OOO0OOO0OO0O0 ()#line:58
        O0OOOOO0O00O00OO0 =OO0000OO00O0OO0OO .get ('end_date').split (' ')[0 ]#line:60
        O000O000O00OO0OO0 =datetime .datetime .strptime (O0OOOOO0O00O00OO0 ,'%Y-%m-%d')#line:61
        O00O00000O000O000 =datetime .datetime .now ()#line:62
        if O00O00000O000O000 >O000O000O00OO0OO0 :#line:63
            request .msg ='激活码已经过期，请重新购买！'#line:64
            return False #line:65
        O0O0OOO00O0O0O00O =OO0000OO00O0OO0OO .get ('device_id')#line:66
        if str (conf .get_device_id ())!=str (O0O0OOO00O0O0O00O ):#line:67
            request .msg ='激活码和设备不匹配，请重新激活！'#line:68
            return False #line:69
        return True #line:70
    except Exception as OOO0O0O0O0OOO0O00 :#line:71
        pass #line:73
    return False #line:74
def pre_process (request ,view_func ):#line:77
    if not OO0O0OO0OOO0OO0O0 (request ):#line:78
        return process_active (request )#line:79
    if '_popup'in request .GET or not request .user .is_authenticated :#line:82
        pass #line:83
    elif hasattr (view_func ,'admin_site'):#line:84
        if request .user and not request .user .is_superuser :#line:86
            request .menus =get_menus (request ,view_func .admin_site )#line:87
    elif 'model_admin'in view_func .__dict__ :#line:88
        request .model_admin =view_func .model_admin #line:91
        if isinstance (view_func .model_admin ,GroupAdmin ):#line:93
            class O00000OO0000O00OO :#line:94
                js =('admin/group/js/group.js',)#line:95
            view_func .model_admin .Media =O00000OO0000O00OO #line:97
            view_func .model_admin .list_display =('id','name')#line:98
            view_func .model_admin .list_per_page =10 #line:99
        O0O0O0000O0OOOOO0 =request .path #line:100
        O00OO0OOOOOOO0O0O =view_func .model_admin .opts #line:102
        OO0OO0O00O0OOO00O ='admin:{}_{}_changelist'.format (O00OO0OOOOOOO0O0O .app_label ,O00OO0OOOOOOO0O0O .model_name )#line:103
        if reverse (OO0OO0O00O0OOO00O )==O0O0O0000O0OOOOO0 :#line:105
            URL_CACHE [request .path ]=view_func .model_admin #line:107
            return process_list (request ,view_func .model_admin )#line:108
def custom_action (request ,model_admin ):#line:111
    ""#line:112
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:115
    O0OOO000O00OO00OO ={'state':True ,'msg':'操作成功！',}#line:120
    try :#line:121
        OO0O0O000OOOO0O00 =request .POST #line:122
        O0O0O00000O0000OO =OO0O0O000OOOO0O00 .get ('all')#line:124
        OO00OO000OO000O0O =OO0O0O000OOOO0O00 .get ('ids')#line:125
        OO0O00OOOO00O0O0O =OO0O0O000OOOO0O00 .get ('key')#line:126
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:132
        O00OO00OOOOO0O00O =model_admin .model #line:133
        O000000O000O00000 =O00OO00OOOOO0O00O .objects .get_queryset ()#line:134
        if O0O0O00000O0000OO =='0':#line:137
            OO00O0OO000O00OOO ={}#line:138
            OO00O0OO000O00OOO [O00OO00OOOOO0O00O .id .field_name +'__in']=OO00OO000OO000O0O .split (',')#line:139
            O000000O000O00000 =O000000O000O00000 .filter (**OO00O0OO000O00OOO )#line:141
        O0000O00O0OO00OO0 =getattr (model_admin ,OO0O00OOOO00O0O0O )#line:143
        OO0O00000000OOOOO =O0000O00O0OO00OO0 (request ,O000000O000O00000 )#line:144
        if OO0O00000000OOOOO and isinstance (OO0O00000000OOOOO ,dict ):#line:147
            O0OOO000O00OO00OO =OO0O00000000OOOOO #line:148
    except Exception as O000000OOO0000OOO :#line:150
        O0OOO000O00OO00OO ={'state':False ,'msg':O000000OOO0000OOO .args [0 ]}#line:154
    return HttpResponse (json .dumps (O0OOO000O00OO00OO ,cls =LazyEncoder ),content_type ='application/json')#line:156
def process_list (request ,model_admin ):#line:159
    O00000O00O0OOOO0O =request .POST .get ('action')#line:160
    OOOOO00000O0OO0OO ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:167
    if O00000O00O0OOOO0O and O00000O00O0OOOO0O not in OOOOO00000O0OO0OO :#line:169
        pass #line:170
    elif O00000O00O0OOOO0O :#line:171
        OOOOO000O0OO00O0O ={}#line:173
        OOO0OOOOOOOO00OO0 =model_admin .get_changelist_instance (request )#line:174
        if OOO0OOOOOOOO00OO0 .has_filters :#line:175
            for OOO000O00O0000OO0 in OOO0OOOOOOOO00OO0 .filter_specs :#line:176
                OOOO0OO0OO0O000OO =None #line:177
                if hasattr (OOO000O00O0000OO0 ,'field_path'):#line:178
                    OOOO0OO0OO0O000OO =OOO000O00O0000OO0 .field_path #line:179
                elif hasattr (OOO000O00O0000OO0 ,'parameter_name'):#line:180
                    OOOO0OO0OO0O000OO =OOO000O00O0000OO0 .parameter_name #line:181
                elif hasattr (OOO000O00O0000OO0 ,'lookup_kwarg'):#line:182
                    OOOO0OO0OO0O000OO =OOO000O00O0000OO0 .lookup_kwarg #line:183
                if OOOO0OO0OO0O000OO :#line:184
                    OOOOO000O0OO00O0O [OOOO0OO0OO0O000OO ]=OOO000O00O0000OO0 #line:185
        model_admin .filter_mappers =OOOOO000O0OO00O0O #line:186
        return OOOOO00000O0OO0OO [O00000O00O0OOOO0O ](request ,model_admin )#line:188
    else :#line:191
        OOO0OOOOOOOO00OO0 =model_admin .get_changelist_instance (request )#line:195
        model_admin .has_filters =OOO0OOOOOOOO00OO0 .has_filters #line:196
        model_admin .filter_specs =OOO0OOOOOOOO00OO0 .filter_specs #line:197
        OO0O00OO0O000O000 =[]#line:198
        if model_admin .has_filters :#line:199
            for OOO000O00O0000OO0 in model_admin .filter_specs :#line:200
                if hasattr (OOO000O00O0000OO0 ,'field_path'):#line:202
                    OO0O00OO0O000O000 .append (OOO000O00O0000OO0 .field_path )#line:203
                elif hasattr (OOO000O00O0000OO0 ,'parameter_name'):#line:204
                    OO0O00OO0O000O000 .append (OOO000O00O0000OO0 .parameter_name )#line:205
                elif hasattr (OOO000O00O0000OO0 ,'lookup_kwarg'):#line:206
                    OO0O00OO0O000O000 .append (OOO000O00O0000OO0 .lookup_kwarg )#line:207
        O0OOOOOOO0000OO00 =None #line:210
        if hasattr (model_admin ,'Media'):#line:212
            O0O0O0O0OOO00O000 =model_admin .Media #line:213
            O0OOOOOOO0000OO00 ={}#line:214
            if hasattr (O0O0O0O0OOO00O000 ,'js'):#line:215
                OOOOO00000OO000OO =[]#line:216
                O0OOOOOOOOO00O0OO =getattr (O0O0O0O0OOO00O000 ,'js')#line:218
                for O0OOOO0O00O00O0O0 in O0OOOOOOOOO00O0OO :#line:220
                    if not O0OOOO0O00O00O0O0 .endswith ('import_export/action_formats.js'):#line:221
                        OOOOO00000OO000OO .append (O0OOOO0O00O00O0O0 )#line:222
                O0OOOOOOO0000OO00 ['js']=OOOOO00000OO000OO #line:224
            if hasattr (O0O0O0O0OOO00O000 ,'css'):#line:225
                O0OOOOOOO0000OO00 ['css']=getattr (O0O0O0O0OOO00O000 ,'css')#line:226
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':O0OOOOOOO0000OO00 ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OO0O00OO0O000O000 ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:245
def delete_data (request ,model_admin ):#line:248
    ""#line:253
    O000OO000OO0OO000 =model_admin .model #line:255
    O0O0000OO00O00OOO =O000OO000OO0OO000 .objects .get_queryset ()#line:256
    O0000OO0OO00OO0OO =request .POST .get ('ids')#line:257
    O0O0O0000OO0O0OOO ={'state':True ,'msg':'删除成功！'}#line:262
    if O0000OO0OO00OO0OO :#line:264
        O0000OO0OO00OO0OO =O0000OO0OO00OO0OO .split (',')#line:265
        O0O0OO000OOO0OO0O ={}#line:266
        O0O0OO000OOO0OO0O [O000OO000OO0OO000 .id .field_name +'__in']=O0000OO0OO00OO0OO #line:267
        O0O0000OO00O00OOO =O0O0000OO00O00OOO .filter (**O0O0OO000OOO0OO0O )#line:268
        try :#line:270
            if hasattr (model_admin ,'delete_queryset'):#line:271
                OO0OOOOO0OO00O0O0 =getattr (model_admin ,'delete_queryset')(request ,O0O0000OO00O00OOO )#line:272
                if OO0OOOOO0OO00O0O0 :#line:273
                    O0O0000OO00O00OOO =OO0OOOOO0OO00O0O0 #line:274
                    O0O0000OO00O00OOO .delete ()#line:275
        except Exception as OO00OO0OO00OO0OO0 :#line:277
            O0O0O0000OO0O0OOO ={'state':False ,'msg':OO00OO0OO00OO0OO0 .args [0 ]}#line:281
    return write (O0O0O0000OO0O0OOO )#line:282
def list_data (request ,model_admin ):#line:285
    ""#line:291
    """
        admin 中字段设置
        fields_options={
            'id':{
                'fixed':'left',
                'width':'100px',
                'algin':'center'
            }
        }
    """#line:301
    OOOO00O0OOO0OO00O ={}#line:302
    OOOOO000O00000O0O =request .POST .get ('current_page')#line:304
    if OOOOO000O00000O0O :#line:305
        OOOOO000O00000O0O =int (OOOOO000O00000O0O )#line:306
    else :#line:307
        OOOOO000O00000O0O =1 #line:308
    O0O0O00O0OOOO0000 ,O0O0OO00O0O00O0O0 ,O0000O0O0O0000OO0 ,O000OO00O0O0O00OO ,OOO0OOOO0O00O00O0 =get_model_info (model_admin ,request )#line:310
    OO00O00OO000OOOOO ='-'+model_admin .model .id .field_name #line:312
    if 'order_by'in request .POST :#line:314
        O0O000OOOOO0OOOO0 =request .POST .get ('order_by')#line:315
        if O0O000OOOOO0OOOO0 and O0O000OOOOO0OOOO0 !=''and O0O000OOOOO0OOOO0 !='null':#line:316
            OO00O00OO000OOOOO =O0O000OOOOO0OOOO0 #line:317
    OO0000000OO0OOO00 =model_admin .model #line:319
    O0O00OO00O00000OO =model_admin .get_queryset (request )#line:322
    if not O0O00OO00O00000OO :#line:323
        O0O00OO00O00000OO =OO0000000OO0OOO00 .objects .get_queryset ()#line:325
    O00OOOO0O0OOOOO00 =request .POST .get ('filters')#line:327
    OOO000OO0O0000O00 ={}#line:330
    O000OOOOO000OO0OO =request .POST .get ('search')#line:333
    if O000OOOOO000OO0OO and O000OOOOO000OO0OO !='':#line:334
        OO0O00O0OO0O0000O =Q ()#line:335
        O00OO0OO00O00OO0O =model_admin .search_fields #line:336
        for OOO0000OO0O00O000 in O00OO0OO00O00OO0O :#line:337
            OO0O00O0OO0O0000O =OO0O00O0OO0O0000O |Q (**{OOO0000OO0O00O000 +"__icontains":O000OOOOO000OO0OO })#line:338
        O0O00OO00O00000OO =O0O00OO00O00000OO .filter (OO0O00O0OO0O0000O )#line:339
    if O00OOOO0O0OOOOO00 :#line:341
        O00OOOO0O0OOOOO00 =json .loads (O00OOOO0O0OOOOO00 )#line:342
        for OO000OOOO0O0OOO0O in O00OOOO0O0OOOOO00 :#line:343
            if OO000OOOO0O0OOO0O in model_admin .filter_mappers :#line:345
                OO0O0OOOOOOO0O000 =model_admin .filter_mappers [OO000OOOO0O0OOO0O ]#line:347
                OO0O0OOOOOOO0O000 .used_parameters =O00OOOO0O0OOOOO00 #line:348
                O0O00OO00O00000OO =OO0O0OOOOOOO0O000 .queryset (request ,O0O00OO00O00000OO )#line:350
            else :#line:351
                OO0O0OO0O00O0OOO0 =O00OOOO0O0OOOOO00 .get (OO000OOOO0O0OOO0O )#line:357
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',OO0O0OO0O00O0OOO0 ):#line:359
                    OO00O000000OOO00O =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OO0O0OO0O00O0OOO0 )#line:360
                    if OO00O000000OOO00O :#line:361
                        O0OO0000OO000OO0O =OO00O000000OOO00O [0 ]#line:362
                        O00OO0OO00OOO0000 =datetime .datetime .strptime (O0OO0000OO000OO0O ,'%Y-%m-%d %H:%M:%S')#line:363
                        OO0O0OO0O00O0OOO0 =O00OO0OO00OOO0000 +datetime .timedelta (hours =8 )#line:364
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OO0O0OO0O00O0OOO0 ):#line:365
                    OO0O0OO0O00O0OOO0 =datetime .datetime .strptime (OO0O0OO0O00O0OOO0 ,'%Y-%m-%d %H:%M:%S')#line:367
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',OO0O0OO0O00O0OOO0 ):#line:368
                    OO0O0OO0O00O0OOO0 =datetime .datetime .strptime (OO0O0OO0O00O0OOO0 ,'%Y-%m-%d')#line:370
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',OO0O0OO0O00O0OOO0 ):#line:371
                    OO0O0OO0O00O0OOO0 =time .strptime (OO0O0OO0O00O0OOO0 ,' %H:%M:%S')#line:373
                OOO000OO0O0000O00 [OO000OOOO0O0OOO0O ]=OO0O0OO0O00O0OOO0 #line:374
    OOO00O00O0O0O000O =O0O00OO00O00000OO .filter (**OOO000OO0O0000O00 ).order_by (OO00O00OO000OOOOO )#line:376
    O00O0OOO0OO0OOOOO =model_admin .list_per_page #line:377
    if 'page_size'in request .POST :#line:378
        OOO0O0O0O0O0OOOO0 =int (request .POST .get ('page_size'))#line:379
        if OOO0O0O0O0O0OOOO0 !=0 :#line:380
            O00O0OOO0OO0OOOOO =OOO0O0O0O0O0OOOO0 #line:381
    O0O0OOOOO00OOO00O =Paginator (OOO00O00O0O0O000O ,O00O0OOO0OO0OOOOO )#line:383
    if OOOOO000O00000O0O >O0O0OOOOO00OOO00O .num_pages :#line:384
        OOOOO000O00000O0O =O0O0OOOOO00OOO00O .num_pages #line:385
    O000O0O0000OO0OOO =O0O0OOOOO00OOO00O .page (OOOOO000O00000O0O )#line:386
    OOO0O0O0O0O000OO0 =O000O0O0000OO0OOO .object_list #line:387
    OO0OO0OO0000OOO0O =[]#line:391
    for O0OO00O00OOO000OO in OOO0O0O0O0O000OO0 :#line:392
        O0000OOOO0O000O00 ={}#line:393
        for O0O000OOOOO0OOOO0 in O0O0O00O0OOOO0000 :#line:394
            OO000OOOO0O0OOO0O =O0O000OOOOO0OOOO0 +'_choices'#line:395
            if OO000OOOO0O0OOO0O in OOO0OOOO0O00O00O0 :#line:396
                OO000000O0O0O000O =getattr (O0OO00O00OOO000OO ,O0O000OOOOO0OOOO0 )#line:397
                OOO0OOOO00O000O0O =OOO0OOOO0O00O00O0 [OO000OOOO0O0OOO0O ]#line:398
                if OO000000O0O0O000O in OOO0OOOO00O000O0O :#line:399
                    OO000000O0O0O000O =OOO0OOOO00O000O0O .get (OO000000O0O0O000O )#line:400
            elif O0O000OOOOO0OOOO0 in OOO0OOOO0O00O00O0 :#line:401
                OO000000O0O0O000O =getattr (O0OO00O00OOO000OO ,O0O000OOOOO0OOOO0 )#line:402
                OOO0OOOO00O000O0O =OOO0OOOO0O00O00O0 [O0O000OOOOO0OOOO0 ]#line:403
                if OO000000O0O0O000O in OOO0OOOO00O000O0O :#line:404
                    OO000000O0O0O000O =OOO0OOOO00O000O0O .get (OO000000O0O0O000O )#line:405
            else :#line:406
                OO000000O0O0O000O =getattr (O0OO00O00OOO000OO ,O0O000OOOOO0OOOO0 )#line:407
            if O000OO00O0O0O00OO :#line:411
                OO000000O0O0O000O =O000OO00O0O0O00OO (O0OO00O00OOO000OO ,O0O000OOOOO0OOOO0 ,OO000000O0O0O000O )#line:412
            if issubclass (OO000000O0O0O000O .__class__ ,Model ):#line:413
                OO000000O0O0O000O =str (OO000000O0O0O000O )#line:414
            O0000OOOO0O000O00 [O0O000OOOOO0OOOO0 ]=OO000000O0O0O000O #line:415
        for OOOO0OOO00000OOO0 in O0O0OO00O0O00O0O0 :#line:417
            try :#line:418
                if hasattr (model_admin ,OOOO0OOO00000OOO0 ):#line:419
                    OO000000O0O0O000O =getattr (model_admin ,OOOO0OOO00000OOO0 ).__call__ (O0OO00O00OOO000OO )#line:420
                else :#line:421
                    OO000000O0O0O000O =getattr (model_admin .model ,OOOO0OOO00000OOO0 ).__call__ (O0OO00O00OOO000OO )#line:422
                if O000OO00O0O0O00OO :#line:423
                    OO000000O0O0O000O =O000OO00O0O0O00OO (O0OO00O00OOO000OO ,OOOO0OOO00000OOO0 ,OO000000O0O0O000O )#line:424
                O0000OOOO0O000O00 [OOOO0OOO00000OOO0 ]=OO000000O0O0O000O #line:425
            except Exception as OO0OO000O0O000O00 :#line:426
                raise Exception (OO0OO000O0O000O00 .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (OOOO0OOO00000OOO0 .__qualname__ ,OOOO0OOO00000OOO0 .__qualname__ ))#line:428
        O0000OOOO0O000O00 ['_id']=getattr (O0OO00O00OOO000OO ,model_admin .model .id .field_name )#line:430
        OO0OO0OO0000OOO0O .append (O0000OOOO0O000O00 )#line:431
    if OOOOO000O00000O0O <=1 :#line:439
        OOOO000O00O0O00OO =True #line:440
        if hasattr (model_admin ,'actions_show'):#line:441
            OOOO000O00O0O00OO =getattr (model_admin ,'actions_show')!=False #line:442
        OOOO00O0OOO0OO00O ['headers']=O0000O0O0O0000OO0 #line:443
        OOOO00O0OOO0OO00O ['exts']={'showId':'id'in O0O0O00O0OOOO0000 ,'actions_show':OOOO000O00O0O00OO ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:449
        OOOO00O0OOO0OO00O ['custom_button']=get_custom_button (request ,model_admin )#line:453
    OOOO00O0OOO0OO00O ['rows']=OO0OO0OO0000OOO0O #line:461
    OOOO00O0OOO0OO00O ['paginator']={'page_size':O00O0OOO0OO0OOOOO ,'count':O0O0OOOOO00OOO00O .count ,'page_count':O0O0OOOOO00OOO00O .num_pages }#line:467
    return write (OOOO00O0OOO0OO00O )#line:469
def process_active (request ):#line:472
    O0OO0OOO0O0OOOO00 =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:474
    O0O00O000OO0O0000 =request .path #line:475
    O0OO00OO00O00O000 =request .POST #line:477
    O0O0O0O00OO0O0000 =O0OO00OO00O00O000 .get ('action')#line:478
    if O0O0O0O00OO0O0000 :#line:479
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:480
    elif O0O00O000OO0O0000 not in O0OO0OOO0O0OOOO00 :#line:481
        return render (request ,'admin/active.html')#line:482
def process_lic (request ):#line:485
    O0000O00O0OO0O0O0 =conf .get_device_id ()#line:487
    O000O0000OOO00O00 =request .POST .get ('active_code')#line:488
    O0O0000000O00O00O =conf .get_server_url ()+'/active'#line:490
    OO0OO000OOOOOO000 =requests .post (O0O0000000O00O00O ,data ={'device_id':O0000O00O0OO0O0O0 ,'active_code':O000O0000OOO00O00 })#line:494
    if OO0OO000OOOOOO000 .status_code ==200 :#line:496
        O0O0OO00OO000O000 =OO0OO000OOOOOO000 .json ()#line:497
        if O0O0OO00OO000O000 .get ('state')is True :#line:498
            O0OO0OO0O00OOOOO0 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:500
            OO0O0OO0OO0O00OO0 =open (O0OO0OO0O00OOOOO0 +'/simplepro/simpepro.lic','wb')#line:503
            O0OOOO0OO0OOOOOO0 =base64 .b64decode (O0O0OO00OO000O000 .get ('license'))#line:506
            OO00000OO0000O0OO =base64 .b64encode (bytes (O0O0OO00OO000O000 .get ('private_key'),encoding ='utf8'))#line:507
            OO0O0OO0OO0O00OO0 .write (struct .pack ('h',len (O0OOOO0OO0OOOOOO0 )))#line:509
            OO0O0OO0OO0O00OO0 .write (struct .pack ('h',len (OO00000OO0000O0OO )))#line:510
            OO0O0OO0OO0O00OO0 .write (O0OOOO0OO0OOOOOO0 )#line:511
            OO0O0OO0OO0O00OO0 .write (OO00000OO0000O0OO )#line:512
            OO0O0OO0OO0O00OO0 .close ()#line:513
            O0O0OOO0OOO0OO0O0 (True )#line:514
            print ('写入激活文件，位置：{}'.format (O0OO0OO0O00OOOOO0 +'/simpepro.lic'))#line:516
        return write_obj (O0O0OO00OO000O000 )#line:518
    return write ({},'error',False )#line:519
def process_info (request ):#line:522
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:526
