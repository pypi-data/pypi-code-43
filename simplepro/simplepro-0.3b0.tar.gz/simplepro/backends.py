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
def O0O0OOO0OOO0OO0O0 ():#line:27
    try :#line:28
        O0OO0O000O0O0O0O0 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:30
        if not os .path .exists (O0OO0O000O0O0O0O0 +'/simplepro/simpepro.lic'):#line:31
            return False #line:32
        global cache_d #line:33
        if cache_d :#line:34
            return cache_d #line:35
        O0O0OOO0OOO0O0OO0 =open (O0OO0O000O0O0O0O0 +'/simplepro/simpepro.lic','rb')#line:36
        OOO00O0OOOO0O0O00 =O0O0OOO0OOO0O0OO0 .read ()#line:37
        O000O00OOOOO0OOO0 ,=struct .unpack ('h',OOO00O0OOOO0O0O00 [0 :2 ])#line:38
        O0OOOO0OO0OOOO0OO ,=struct .unpack ('h',OOO00O0OOOO0O0O00 [2 :4 ])#line:39
        OO00OOOO000000OO0 =OOO00O0OOOO0O0O00 [4 :O000O00OOOOO0OOO0 +4 ]#line:40
        O0OOOO000OO0OOOOO =base64 .b64decode (OOO00O0OOOO0O0O00 [O000O00OOOOO0OOO0 +4 :])#line:42
        OO00000O00OO0O00O =rsa .PrivateKey .load_pkcs1 (O0OOOO000OO0OOOOO )#line:44
        OO00O00OOOO0O0O0O =rsa .decrypt (OO00OOOO000000OO0 ,OO00000O00OO0O00O ).decode ()#line:45
        O00O0000OOOOO0O0O =json .loads (OO00O00OOOO0O0O0O )#line:46
        cache_d =O00O0000OOOOO0O0O #line:47
    except Exception as O0O000000OO0O0O00 :#line:48
        pass #line:49
    return O00O0000OOOOO0O0O #line:50
def OO0O0OO0OOO0OO0O0 (request ):#line:53
    try :#line:54
        O0OO00OOO0OO00O00 =O0O0OOO0OOO0OO0O0 ()#line:55
        O000OO0O000O0O00O =O0OO00OOO0OO00O00 .get ('end_date').split (' ')[0 ]#line:57
        O0OOO000OO00O0O00 =datetime .datetime .strptime (O000OO0O000O0O00O ,'%Y-%m-%d')#line:58
        OO0O00O0OO00O0O00 =datetime .datetime .now ()#line:59
        if OO0O00O0OO00O0O00 >O0OOO000OO00O0O00 :#line:60
            request .msg ='激活码已经过期，请重新购买！'#line:61
            return False #line:62
        O0OO00O000000OO00 =O0OO00OOO0OO00O00 .get ('device_id')#line:63
        if str (conf .get_device_id ())!=str (O0OO00O000000OO00 ):#line:64
            request .msg ='激活码和设备不匹配，请重新激活！'#line:65
            return False #line:66
        return True #line:67
    except Exception as OOOOOO0000000O000 :#line:68
        pass #line:70
    return False #line:71
def pre_process (request ,view_func ):#line:74
    if not OO0O0OO0OOO0OO0O0 (request ):#line:75
        return process_active (request )#line:76
    if '_popup'in request .GET or not request .user .is_authenticated :#line:79
        pass #line:80
    elif hasattr (view_func ,'admin_site'):#line:81
        if request .user and not request .user .is_superuser :#line:83
            request .menus =get_menus (request ,view_func .admin_site )#line:84
    elif 'model_admin'in view_func .__dict__ :#line:85
        request .model_admin =view_func .model_admin #line:88
        if isinstance (view_func .model_admin ,GroupAdmin ):#line:90
            class O0000O0OOO0000O00 :#line:91
                js =('admin/group/js/group.js',)#line:92
            view_func .model_admin .Media =O0000O0OOO0000O00 #line:94
            view_func .model_admin .list_display =('id','name')#line:95
            view_func .model_admin .list_per_page =10 #line:96
        O0O0O0O0OO000O000 =request .path #line:97
        O00O00OO00OOO000O =view_func .model_admin .opts #line:99
        O0OOO000O000OO0OO ='admin:{}_{}_changelist'.format (O00O00OO00OOO000O .app_label ,O00O00OO00OOO000O .model_name )#line:100
        if reverse (O0OOO000O000OO0OO )==O0O0O0O0OO000O000 :#line:102
            URL_CACHE [request .path ]=view_func .model_admin #line:104
            return process_list (request ,view_func .model_admin )#line:105
def custom_action (request ,model_admin ):#line:108
    ""#line:109
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:112
    OO00000OO0O0O0OO0 ={'state':True ,'msg':'操作成功！',}#line:117
    try :#line:118
        OOOO0O00OO0OO0O0O =request .POST #line:119
        O0O0O0O000OOOOO00 =OOOO0O00OO0OO0O0O .get ('all')#line:121
        OO00OOOOOOO0O00OO =OOOO0O00OO0OO0O0O .get ('ids')#line:122
        O0O0OOO0000O00O00 =OOOO0O00OO0OO0O0O .get ('key')#line:123
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:129
        O000O0O00O0000O00 =model_admin .model #line:130
        OOO00OO000O00OO0O =O000O0O00O0000O00 .objects .get_queryset ()#line:131
        if O0O0O0O000OOOOO00 =='0':#line:134
            OO00O0O0OO00000OO ={}#line:135
            OO00O0O0OO00000OO [O000O0O00O0000O00 .id .field_name +'__in']=OO00OOOOOOO0O00OO .split (',')#line:136
            OOO00OO000O00OO0O =OOO00OO000O00OO0O .filter (**OO00O0O0OO00000OO )#line:138
        O00O0O000OOO000OO =getattr (model_admin ,O0O0OOO0000O00O00 )#line:140
        OO0OO0O0OO000OOOO =O00O0O000OOO000OO (request ,OOO00OO000O00OO0O )#line:141
        if OO0OO0O0OO000OOOO and isinstance (OO0OO0O0OO000OOOO ,dict ):#line:144
            OO00000OO0O0O0OO0 =OO0OO0O0OO000OOOO #line:145
    except Exception as OO0OO00OOOO0000O0 :#line:147
        OO00000OO0O0O0OO0 ={'state':False ,'msg':OO0OO00OOOO0000O0 .args [0 ]}#line:151
    return HttpResponse (json .dumps (OO00000OO0O0O0OO0 ,cls =LazyEncoder ),content_type ='application/json')#line:153
def process_list (request ,model_admin ):#line:156
    OOO00O000O0OO0O0O =request .POST .get ('action')#line:157
    O00OOO00OOOOOOO00 ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:164
    if OOO00O000O0OO0O0O and OOO00O000O0OO0O0O not in O00OOO00OOOOOOO00 :#line:166
        pass #line:167
    elif OOO00O000O0OO0O0O :#line:168
        OO0O0000OO00OO000 ={}#line:170
        OOOOO00000OOOOOOO =model_admin .get_changelist_instance (request )#line:171
        if OOOOO00000OOOOOOO .has_filters :#line:172
            for O00O0OO0O000O0000 in OOOOO00000OOOOOOO .filter_specs :#line:173
                OOOO00O0OO0OO0O00 =None #line:174
                if hasattr (O00O0OO0O000O0000 ,'field_path'):#line:175
                    OOOO00O0OO0OO0O00 =O00O0OO0O000O0000 .field_path #line:176
                elif hasattr (O00O0OO0O000O0000 ,'parameter_name'):#line:177
                    OOOO00O0OO0OO0O00 =O00O0OO0O000O0000 .parameter_name #line:178
                elif hasattr (O00O0OO0O000O0000 ,'lookup_kwarg'):#line:179
                    OOOO00O0OO0OO0O00 =O00O0OO0O000O0000 .lookup_kwarg #line:180
                if OOOO00O0OO0OO0O00 :#line:181
                    OO0O0000OO00OO000 [OOOO00O0OO0OO0O00 ]=O00O0OO0O000O0000 #line:182
        model_admin .filter_mappers =OO0O0000OO00OO000 #line:183
        return O00OOO00OOOOOOO00 [OOO00O000O0OO0O0O ](request ,model_admin )#line:185
    else :#line:188
        OOOOO00000OOOOOOO =model_admin .get_changelist_instance (request )#line:192
        model_admin .has_filters =OOOOO00000OOOOOOO .has_filters #line:193
        model_admin .filter_specs =OOOOO00000OOOOOOO .filter_specs #line:194
        OOOO0OOOO0OO0O0O0 =[]#line:195
        if model_admin .has_filters :#line:196
            for O00O0OO0O000O0000 in model_admin .filter_specs :#line:197
                if hasattr (O00O0OO0O000O0000 ,'field_path'):#line:199
                    OOOO0OOOO0OO0O0O0 .append (O00O0OO0O000O0000 .field_path )#line:200
                elif hasattr (O00O0OO0O000O0000 ,'parameter_name'):#line:201
                    OOOO0OOOO0OO0O0O0 .append (O00O0OO0O000O0000 .parameter_name )#line:202
                elif hasattr (O00O0OO0O000O0000 ,'lookup_kwarg'):#line:203
                    OOOO0OOOO0OO0O0O0 .append (O00O0OO0O000O0000 .lookup_kwarg )#line:204
        O0OO0000O0O00OO0O =None #line:207
        if hasattr (model_admin ,'Media'):#line:209
            O0O00OO0O0O000000 =model_admin .Media #line:210
            O0OO0000O0O00OO0O ={}#line:211
            if hasattr (O0O00OO0O0O000000 ,'js'):#line:212
                O0OO0OOOO00O00O00 =[]#line:213
                OO000O0O00000000O =getattr (O0O00OO0O0O000000 ,'js')#line:215
                for OO00OO00OOOO0O000 in OO000O0O00000000O :#line:217
                    if not OO00OO00OOOO0O000 .endswith ('import_export/action_formats.js'):#line:218
                        O0OO0OOOO00O00O00 .append (OO00OO00OOOO0O000 )#line:219
                O0OO0000O0O00OO0O ['js']=O0OO0OOOO00O00O00 #line:221
            if hasattr (O0O00OO0O0O000000 ,'css'):#line:222
                O0OO0000O0O00OO0O ['css']=getattr (O0O00OO0O0O000000 ,'css')#line:223
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':O0OO0000O0O00OO0O ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OOOO0OOOO0OO0O0O0 ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:242
def delete_data (request ,model_admin ):#line:245
    ""#line:250
    OO0OOO00OOOO0000O =model_admin .model #line:252
    O0O00OO0OO0OO0O0O =OO0OOO00OOOO0000O .objects .get_queryset ()#line:253
    OOO0O00OO00OOO0O0 =request .POST .get ('ids')#line:254
    OO000O00O00OOOOOO ={'state':True ,'msg':'删除成功！'}#line:259
    if OOO0O00OO00OOO0O0 :#line:261
        OOO0O00OO00OOO0O0 =OOO0O00OO00OOO0O0 .split (',')#line:262
        O000O0OOO0OO00O00 ={}#line:263
        O000O0OOO0OO00O00 [OO0OOO00OOOO0000O .id .field_name +'__in']=OOO0O00OO00OOO0O0 #line:264
        O0O00OO0OO0OO0O0O =O0O00OO0OO0OO0O0O .filter (**O000O0OOO0OO00O00 )#line:265
        try :#line:267
            if hasattr (model_admin ,'delete_queryset'):#line:268
                OO00OO000O00OO0O0 =getattr (model_admin ,'delete_queryset')(request ,O0O00OO0OO0OO0O0O )#line:269
                if OO00OO000O00OO0O0 :#line:270
                    O0O00OO0OO0OO0O0O =OO00OO000O00OO0O0 #line:271
                    O0O00OO0OO0OO0O0O .delete ()#line:272
        except Exception as O00OOO0O0O00000OO :#line:274
            OO000O00O00OOOOOO ={'state':False ,'msg':O00OOO0O0O00000OO .args [0 ]}#line:278
    return write (OO000O00O00OOOOOO )#line:279
def list_data (request ,model_admin ):#line:282
    ""#line:288
    """
        admin 中字段设置
        fields_options={
            'id':{
                'fixed':'left',
                'width':'100px',
                'algin':'center'
            }
        }
    """#line:298
    OOOOO0O00000O0OO0 ={}#line:299
    OOOOOO0OO00O0O00O =request .POST .get ('current_page')#line:301
    if OOOOOO0OO00O0O00O :#line:302
        OOOOOO0OO00O0O00O =int (OOOOOO0OO00O0O00O )#line:303
    else :#line:304
        OOOOOO0OO00O0O00O =1 #line:305
    OO0O0O0OOO00OOOO0 ,OOOO0OO0OO0000OOO ,O0O00O0OO00000OO0 ,OO00O000OO0O0000O ,OO00OOOOOOOO0OO00 =get_model_info (model_admin ,request )#line:307
    O0OOOO000O0OOO00O ='-'+model_admin .model .id .field_name #line:309
    if 'order_by'in request .POST :#line:311
        O0000OO0O0000O000 =request .POST .get ('order_by')#line:312
        if O0000OO0O0000O000 and O0000OO0O0000O000 !=''and O0000OO0O0000O000 !='null':#line:313
            O0OOOO000O0OOO00O =O0000OO0O0000O000 #line:314
    O0O0OOO00OOOO0O00 =model_admin .model #line:316
    OOOO0OO00O0OO00OO =model_admin .get_queryset (request )#line:319
    if not OOOO0OO00O0OO00OO :#line:320
        OOOO0OO00O0OO00OO =O0O0OOO00OOOO0O00 .objects .get_queryset ()#line:322
    O000OOO000OOOO000 =request .POST .get ('filters')#line:324
    O0O000000O0OOO00O ={}#line:327
    O00OO0O0O0OO00000 =request .POST .get ('search')#line:330
    if O00OO0O0O0OO00000 and O00OO0O0O0OO00000 !='':#line:331
        O0OOOOO000OOO0OOO =Q ()#line:332
        O00000000000OOO00 =model_admin .search_fields #line:333
        for O00OO00OO00000OO0 in O00000000000OOO00 :#line:334
            O0OOOOO000OOO0OOO =O0OOOOO000OOO0OOO |Q (**{O00OO00OO00000OO0 +"__icontains":O00OO0O0O0OO00000 })#line:335
        OOOO0OO00O0OO00OO =OOOO0OO00O0OO00OO .filter (O0OOOOO000OOO0OOO )#line:336
    if O000OOO000OOOO000 :#line:338
        O000OOO000OOOO000 =json .loads (O000OOO000OOOO000 )#line:339
        for OOO00O000OOOOOO0O in O000OOO000OOOO000 :#line:340
            if OOO00O000OOOOOO0O in model_admin .filter_mappers :#line:342
                O0O0O0OOO0OO000O0 =model_admin .filter_mappers [OOO00O000OOOOOO0O ]#line:344
                O0O0O0OOO0OO000O0 .used_parameters =O000OOO000OOOO000 #line:345
                OOOO0OO00O0OO00OO =O0O0O0OOO0OO000O0 .queryset (request ,OOOO0OO00O0OO00OO )#line:347
            else :#line:348
                OOOO0OOOO000O00OO =O000OOO000OOOO000 .get (OOO00O000OOOOOO0O )#line:354
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',OOOO0OOOO000O00OO ):#line:356
                    OOOO0OOO0O00000OO =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OOOO0OOOO000O00OO )#line:357
                    if OOOO0OOO0O00000OO :#line:358
                        OO0O0OO0OO0OO0OO0 =OOOO0OOO0O00000OO [0 ]#line:359
                        OO0OOOO0O00OO00OO =datetime .datetime .strptime (OO0O0OO0OO0OO0OO0 ,'%Y-%m-%d %H:%M:%S')#line:360
                        OOOO0OOOO000O00OO =OO0OOOO0O00OO00OO +datetime .timedelta (hours =8 )#line:361
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',OOOO0OOOO000O00OO ):#line:362
                    OOOO0OOOO000O00OO =datetime .datetime .strptime (OOOO0OOOO000O00OO ,'%Y-%m-%d %H:%M:%S')#line:364
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',OOOO0OOOO000O00OO ):#line:365
                    OOOO0OOOO000O00OO =datetime .datetime .strptime (OOOO0OOOO000O00OO ,'%Y-%m-%d')#line:367
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',OOOO0OOOO000O00OO ):#line:368
                    OOOO0OOOO000O00OO =time .strptime (OOOO0OOOO000O00OO ,' %H:%M:%S')#line:370
                O0O000000O0OOO00O [OOO00O000OOOOOO0O ]=OOOO0OOOO000O00OO #line:371
    OOOO0000OO0O00OOO =OOOO0OO00O0OO00OO .filter (**O0O000000O0OOO00O ).order_by (O0OOOO000O0OOO00O )#line:373
    OOOOO00OOO0OO0O00 =model_admin .list_per_page #line:374
    if 'page_size'in request .POST :#line:375
        O0O0O0O00000O0000 =int (request .POST .get ('page_size'))#line:376
        if O0O0O0O00000O0000 !=0 :#line:377
            OOOOO00OOO0OO0O00 =O0O0O0O00000O0000 #line:378
    O0O0O0OOO000O00OO =Paginator (OOOO0000OO0O00OOO ,OOOOO00OOO0OO0O00 )#line:380
    if OOOOOO0OO00O0O00O >O0O0O0OOO000O00OO .num_pages :#line:381
        OOOOOO0OO00O0O00O =O0O0O0OOO000O00OO .num_pages #line:382
    OOOO000O000000O0O =O0O0O0OOO000O00OO .page (OOOOOO0OO00O0O00O )#line:383
    O00OO00000OO0O0O0 =OOOO000O000000O0O .object_list #line:384
    O000000O00000OO00 =[]#line:388
    for O0OOO00OO00O00O0O in O00OO00000OO0O0O0 :#line:389
        OOOOO0OOO000000O0 ={}#line:390
        for O0000OO0O0000O000 in OO0O0O0OOO00OOOO0 :#line:391
            OOO00O000OOOOOO0O =O0000OO0O0000O000 +'_choices'#line:392
            if OOO00O000OOOOOO0O in OO00OOOOOOOO0OO00 :#line:393
                O0O0O0O000O000O00 =getattr (O0OOO00OO00O00O0O ,O0000OO0O0000O000 )#line:394
                O0O00000OOO0O0OO0 =OO00OOOOOOOO0OO00 [OOO00O000OOOOOO0O ]#line:395
                if O0O0O0O000O000O00 in O0O00000OOO0O0OO0 :#line:396
                    O0O0O0O000O000O00 =O0O00000OOO0O0OO0 .get (O0O0O0O000O000O00 )#line:397
            elif O0000OO0O0000O000 in OO00OOOOOOOO0OO00 :#line:398
                O0O0O0O000O000O00 =getattr (O0OOO00OO00O00O0O ,O0000OO0O0000O000 )#line:399
                O0O00000OOO0O0OO0 =OO00OOOOOOOO0OO00 [O0000OO0O0000O000 ]#line:400
                if O0O0O0O000O000O00 in O0O00000OOO0O0OO0 :#line:401
                    O0O0O0O000O000O00 =O0O00000OOO0O0OO0 .get (O0O0O0O000O000O00 )#line:402
            else :#line:403
                O0O0O0O000O000O00 =getattr (O0OOO00OO00O00O0O ,O0000OO0O0000O000 )#line:404
            if OO00O000OO0O0000O :#line:408
                O0O0O0O000O000O00 =OO00O000OO0O0000O (O0OOO00OO00O00O0O ,O0000OO0O0000O000 ,O0O0O0O000O000O00 )#line:409
            if issubclass (O0O0O0O000O000O00 .__class__ ,Model ):#line:410
                O0O0O0O000O000O00 =str (O0O0O0O000O000O00 )#line:411
            OOOOO0OOO000000O0 [O0000OO0O0000O000 ]=O0O0O0O000O000O00 #line:412
        for OOO00OOOOO00O0OOO in OOOO0OO0OO0000OOO :#line:414
            try :#line:415
                if hasattr (model_admin ,OOO00OOOOO00O0OOO ):#line:416
                    O0O0O0O000O000O00 =getattr (model_admin ,OOO00OOOOO00O0OOO ).__call__ (O0OOO00OO00O00O0O )#line:417
                else :#line:418
                    O0O0O0O000O000O00 =getattr (model_admin .model ,OOO00OOOOO00O0OOO ).__call__ (O0OOO00OO00O00O0O )#line:419
                if OO00O000OO0O0000O :#line:420
                    O0O0O0O000O000O00 =OO00O000OO0O0000O (O0OOO00OO00O00O0O ,OOO00OOOOO00O0OOO ,O0O0O0O000O000O00 )#line:421
                OOOOO0OOO000000O0 [OOO00OOOOO00O0OOO ]=O0O0O0O000O000O00 #line:422
            except Exception as O00OO0OO0OOO000O0 :#line:423
                raise Exception (O00OO0OO0OOO000O0 .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (OOO00OOOOO00O0OOO .__qualname__ ,OOO00OOOOO00O0OOO .__qualname__ ))#line:425
        OOOOO0OOO000000O0 ['_id']=getattr (O0OOO00OO00O00O0O ,model_admin .model .id .field_name )#line:427
        O000000O00000OO00 .append (OOOOO0OOO000000O0 )#line:428
    if OOOOOO0OO00O0O00O <=1 :#line:436
        OO0000O00OO0O0OO0 =True #line:437
        if hasattr (model_admin ,'actions_show'):#line:438
            OO0000O00OO0O0OO0 =getattr (model_admin ,'actions_show')!=False #line:439
        OOOOO0O00000O0OO0 ['headers']=O0O00O0OO00000OO0 #line:440
        OOOOO0O00000O0OO0 ['exts']={'showId':'id'in OO0O0O0OOO00OOOO0 ,'actions_show':OO0000O00OO0O0OO0 ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:446
        OOOOO0O00000O0OO0 ['custom_button']=get_custom_button (request ,model_admin )#line:450
    OOOOO0O00000O0OO0 ['rows']=O000000O00000OO00 #line:458
    OOOOO0O00000O0OO0 ['paginator']={'page_size':OOOOO00OOO0OO0O00 ,'count':O0O0O0OOO000O00OO .count ,'page_count':O0O0O0OOO000O00OO .num_pages }#line:464
    return write (OOOOO0O00000O0OO0 )#line:466
def process_active (request ):#line:469
    O00000OOOO000000O =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:471
    O0OO0OOOOO0OO0000 =request .path #line:472
    OOO0O0O00OO0OOO00 =request .POST #line:474
    OOO000OOO0O0O0OOO =OOO0O0O00OO0OOO00 .get ('action')#line:475
    if OOO000OOO0O0O0OOO :#line:476
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:477
    elif O0OO0OOOOO0OO0000 not in O00000OOOO000000O :#line:478
        return render (request ,'admin/active.html')#line:479
def process_lic (request ):#line:482
    O0O0OO0OOO0OO000O =conf .get_device_id ()#line:484
    OO0O0O0OOOO000O0O =request .POST .get ('active_code')#line:485
    OO000OOOO0O000000 =conf .get_server_url ()+'/active'#line:487
    OO0000OO00O0O000O =requests .post (OO000OOOO0O000000 ,data ={'device_id':O0O0OO0OOO0OO000O ,'active_code':OO0O0O0OOOO000O0O })#line:491
    if OO0000OO00O0O000O .status_code ==200 :#line:493
        OOOOO00OOO0000OOO =OO0000OO00O0O000O .json ()#line:494
        if OOOOO00OOO0000OOO .get ('state')is True :#line:495
            OOO0OO00000OOOOO0 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:497
            O00O0O000OO0OOO0O =open (OOO0OO00000OOOOO0 +'/simplepro/simpepro.lic','wb')#line:500
            OO00OOO0000OO0OO0 =base64 .b64decode (OOOOO00OOO0000OOO .get ('license'))#line:503
            OOOOOOO0O0O0OOO00 =base64 .b64encode (bytes (OOOOO00OOO0000OOO .get ('private_key'),encoding ='utf8'))#line:504
            O00O0O000OO0OOO0O .write (struct .pack ('h',len (OO00OOO0000OO0OO0 )))#line:506
            O00O0O000OO0OOO0O .write (struct .pack ('h',len (OOOOOOO0O0O0OOO00 )))#line:507
            O00O0O000OO0OOO0O .write (OO00OOO0000OO0OO0 )#line:508
            O00O0O000OO0OOO0O .write (OOOOOOO0O0O0OOO00 )#line:509
            O00O0O000OO0OOO0O .close ()#line:510
            print ('写入激活文件，位置：{}'.format (OOO0OO00000OOOOO0 +'/simpepro.lic'))#line:511
        return write_obj (OOOOO00OOO0000OOO )#line:513
    return write ({},'error',False )#line:514
def process_info (request ):#line:517
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:521
