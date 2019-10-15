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
        OO00000OO00OO0O00 =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:30
        if not os .path .exists (OO00000OO00OO0O00 +'/simplepro/simpepro.lic'):#line:31
            return False #line:32
        global cache_d #line:33
        if cache_d :#line:34
            return cache_d #line:35
        O0OOO0O00OO0OO0O0 =open (OO00000OO00OO0O00 +'/simplepro/simpepro.lic','rb')#line:36
        OO000OO000OOO0O0O =O0OOO0O00OO0OO0O0 .read ()#line:37
        OOO00OO0O0000O000 ,=struct .unpack ('h',OO000OO000OOO0O0O [0 :2 ])#line:38
        O0O00O000OO0O0000 ,=struct .unpack ('h',OO000OO000OOO0O0O [2 :4 ])#line:39
        O00O00OOOO000O000 =OO000OO000OOO0O0O [4 :OOO00OO0O0000O000 +4 ]#line:40
        O0O00O0O0O00OOOO0 =base64 .b64decode (OO000OO000OOO0O0O [OOO00OO0O0000O000 +4 :])#line:42
        OOO0OOO0O0000OOOO =rsa .PrivateKey .load_pkcs1 (O0O00O0O0O00OOOO0 )#line:44
        OOOOO0O0O0O00O0O0 =rsa .decrypt (O00O00OOOO000O000 ,OOO0OOO0O0000OOOO ).decode ()#line:45
        OO0OOO000O0O0O000 =json .loads (OOOOO0O0O0O00O0O0 )#line:46
        cache_d =OO0OOO000O0O0O000 #line:47
    except Exception as OOO000OO0000OO00O :#line:48
        pass #line:49
    return OO0OOO000O0O0O000 #line:50
def OO0O0OO0OOO0OO0O0 (request ):#line:53
    try :#line:54
        O0OOOO00OOO00OO00 =O0O0OOO0OOO0OO0O0 ()#line:55
        OO0OO00OO0000O000 =O0OOOO00OOO00OO00 .get ('end_date').split (' ')[0 ]#line:57
        O0000O000OO000000 =datetime .datetime .strptime (OO0OO00OO0000O000 ,'%Y-%m-%d')#line:58
        OO000OOO000O0O000 =datetime .datetime .now ()#line:59
        if OO000OOO000O0O000 >O0000O000OO000000 :#line:60
            request .msg ='激活码已经过期，请重新购买！'#line:61
            return False #line:62
        O0O0O000O0O000O0O =O0OOOO00OOO00OO00 .get ('device_id')#line:63
        if str (conf .get_device_id ())!=str (O0O0O000O0O000O0O ):#line:64
            request .msg ='激活码和设备不匹配，请重新激活！'#line:65
            return False #line:66
        return True #line:67
    except Exception as OOOO00000OOO000O0 :#line:68
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
            class O0OOO0OO0O0O0OO00 :#line:91
                js =('admin/group/js/group.js',)#line:92
            view_func .model_admin .Media =O0OOO0OO0O0O0OO00 #line:94
            view_func .model_admin .list_display =('id','name')#line:95
            view_func .model_admin .list_per_page =10 #line:96
        O0000O0OOO00O00OO =request .path #line:97
        O000OO0O00OO0000O =view_func .model_admin .opts #line:99
        OO0OO0O0O0OO00O0O ='admin:{}_{}_changelist'.format (O000OO0O00OO0000O .app_label ,O000OO0O00OO0000O .model_name )#line:100
        if reverse (OO0OO0O0O0OO00O0O )==O0000O0OOO00O00OO :#line:102
            URL_CACHE [request .path ]=view_func .model_admin #line:104
            return process_list (request ,view_func .model_admin )#line:105
def custom_action (request ,model_admin ):#line:108
    ""#line:109
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:112
    OO00OO00O000OOO00 ={'state':True ,'msg':'操作成功！',}#line:117
    try :#line:118
        OO0000O0O0000O00O =request .POST #line:119
        O00OOO0000O00O00O =OO0000O0O0000O00O .get ('all')#line:121
        OO0000OOOO0O0OOOO =OO0000O0O0000O00O .get ('ids')#line:122
        O00O0O0000OO0000O =OO0000O0O0000O00O .get ('key')#line:123
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:129
        OO00000O00O00O0OO =model_admin .model #line:130
        OO00O00O0O0O00OO0 =OO00000O00O00O0OO .objects .get_queryset ()#line:131
        if O00OOO0000O00O00O =='0':#line:134
            OOOO00OO00O0O000O ={}#line:135
            OOOO00OO00O0O000O [OO00000O00O00O0OO .id .field_name +'__in']=OO0000OOOO0O0OOOO .split (',')#line:136
            OO00O00O0O0O00OO0 =OO00O00O0O0O00OO0 .filter (**OOOO00OO00O0O000O )#line:138
        O0OO00O0OOOOOO0O0 =getattr (model_admin ,O00O0O0000OO0000O )#line:140
        O0O00OOOO00000000 =O0OO00O0OOOOOO0O0 (request ,OO00O00O0O0O00OO0 )#line:141
        if O0O00OOOO00000000 and isinstance (O0O00OOOO00000000 ,dict ):#line:144
            OO00OO00O000OOO00 =O0O00OOOO00000000 #line:145
    except Exception as OO0OOO00O000O0000 :#line:147
        OO00OO00O000OOO00 ={'state':False ,'msg':OO0OOO00O000O0000 .args [0 ]}#line:151
    return HttpResponse (json .dumps (OO00OO00O000OOO00 ,cls =LazyEncoder ),content_type ='application/json')#line:153
def process_list (request ,model_admin ):#line:156
    O00OOO0O0O00OO0O0 =request .POST .get ('action')#line:157
    OO00OO00OOO0OOOOO ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:164
    if O00OOO0O0O00OO0O0 and O00OOO0O0O00OO0O0 not in OO00OO00OOO0OOOOO :#line:166
        pass #line:167
    elif O00OOO0O0O00OO0O0 :#line:168
        O00OOOO0OOOOO0000 ={}#line:170
        OOOO0O0OOO00O0OO0 =model_admin .get_changelist_instance (request )#line:171
        if OOOO0O0OOO00O0OO0 .has_filters :#line:172
            for O00OOO0O0O0O0O0OO in OOOO0O0OOO00O0OO0 .filter_specs :#line:173
                O00OO000O00OOOO00 =None #line:174
                if hasattr (O00OOO0O0O0O0O0OO ,'field_path'):#line:175
                    O00OO000O00OOOO00 =O00OOO0O0O0O0O0OO .field_path #line:176
                elif hasattr (O00OOO0O0O0O0O0OO ,'parameter_name'):#line:177
                    O00OO000O00OOOO00 =O00OOO0O0O0O0O0OO .parameter_name #line:178
                elif hasattr (O00OOO0O0O0O0O0OO ,'lookup_kwarg'):#line:179
                    O00OO000O00OOOO00 =O00OOO0O0O0O0O0OO .lookup_kwarg #line:180
                if O00OO000O00OOOO00 :#line:181
                    O00OOOO0OOOOO0000 [O00OO000O00OOOO00 ]=O00OOO0O0O0O0O0OO #line:182
        model_admin .filter_mappers =O00OOOO0OOOOO0000 #line:183
        return OO00OO00OOO0OOOOO [O00OOO0O0O00OO0O0 ](request ,model_admin )#line:185
    else :#line:188
        OOOO0O0OOO00O0OO0 =model_admin .get_changelist_instance (request )#line:192
        model_admin .has_filters =OOOO0O0OOO00O0OO0 .has_filters #line:193
        model_admin .filter_specs =OOOO0O0OOO00O0OO0 .filter_specs #line:194
        OOOO0O0000000OOO0 =[]#line:195
        if model_admin .has_filters :#line:196
            for O00OOO0O0O0O0O0OO in model_admin .filter_specs :#line:197
                if hasattr (O00OOO0O0O0O0O0OO ,'field_path'):#line:199
                    OOOO0O0000000OOO0 .append (O00OOO0O0O0O0O0OO .field_path )#line:200
                elif hasattr (O00OOO0O0O0O0O0OO ,'parameter_name'):#line:201
                    OOOO0O0000000OOO0 .append (O00OOO0O0O0O0O0OO .parameter_name )#line:202
                elif hasattr (O00OOO0O0O0O0O0OO ,'lookup_kwarg'):#line:203
                    OOOO0O0000000OOO0 .append (O00OOO0O0O0O0O0OO .lookup_kwarg )#line:204
        O000O000O000O00O0 =None #line:207
        if hasattr (model_admin ,'Media'):#line:209
            O0000OO0O00000OO0 =model_admin .Media #line:210
            O000O000O000O00O0 ={}#line:211
            if hasattr (O0000OO0O00000OO0 ,'js'):#line:212
                OO000OO00O0OO0OO0 =[]#line:213
                OOOO0O0OOOO00OOOO =getattr (O0000OO0O00000OO0 ,'js')#line:215
                for O0O0O0OOO00OOOOOO in OOOO0O0OOOO00OOOO :#line:217
                    if not O0O0O0OOO00OOOOOO .endswith ('import_export/action_formats.js'):#line:218
                        OO000OO00O0OO0OO0 .append (O0O0O0OOO00OOOOOO )#line:219
                O000O000O000O00O0 ['js']=OO000OO00O0OO0OO0 #line:221
            if hasattr (O0000OO0O00000OO0 ,'css'):#line:222
                O000O000O000O00O0 ['css']=getattr (O0000OO0O00000OO0 ,'css')#line:223
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':O000O000O000O00O0 ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OOOO0O0000000OOO0 ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:242
def delete_data (request ,model_admin ):#line:245
    ""#line:250
    O0O00OOO0O0O00O0O =model_admin .model #line:252
    OOOOO00O0OO0OO0OO =O0O00OOO0O0O00O0O .objects .get_queryset ()#line:253
    O0O0OO000OO0O00OO =request .POST .get ('ids')#line:254
    O0OO00OO0000OO0OO ={'state':True ,'msg':'删除成功！'}#line:259
    if O0O0OO000OO0O00OO :#line:261
        O0O0OO000OO0O00OO =O0O0OO000OO0O00OO .split (',')#line:262
        OO0O0O0O00OO0OO00 ={}#line:263
        OO0O0O0O00OO0OO00 [O0O00OOO0O0O00O0O .id .field_name +'__in']=O0O0OO000OO0O00OO #line:264
        OOOOO00O0OO0OO0OO =OOOOO00O0OO0OO0OO .filter (**OO0O0O0O00OO0OO00 )#line:265
        try :#line:267
            if hasattr (model_admin ,'delete_queryset'):#line:268
                OO000O0OO000O0O00 =getattr (model_admin ,'delete_queryset')(request ,OOOOO00O0OO0OO0OO )#line:269
                if OO000O0OO000O0O00 :#line:270
                    OOOOO00O0OO0OO0OO =OO000O0OO000O0O00 #line:271
                    OOOOO00O0OO0OO0OO .delete ()#line:272
        except Exception as O000O0O0O0O0O0OOO :#line:274
            O0OO00OO0000OO0OO ={'state':False ,'msg':O000O0O0O0O0O0OOO .args [0 ]}#line:278
    return write (O0OO00OO0000OO0OO )#line:279
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
    OOOO0O000O0OOO0OO ={}#line:299
    OOOO0OOOOO00000O0 =request .POST .get ('current_page')#line:301
    if OOOO0OOOOO00000O0 :#line:302
        OOOO0OOOOO00000O0 =int (OOOO0OOOOO00000O0 )#line:303
    else :#line:304
        OOOO0OOOOO00000O0 =1 #line:305
    O0O0000O0OOOO0OO0 ,O00OOOO00OOO00OO0 ,OO000O0O0O000OOOO ,OO000OOO00000O0O0 ,OO0000OOOO0000OOO =get_model_info (model_admin ,request )#line:307
    OO0OO000O0O00O00O ='-'+model_admin .model .id .field_name #line:309
    if 'order_by'in request .POST :#line:311
        O0OOOOOOOO0OO0OO0 =request .POST .get ('order_by')#line:312
        if O0OOOOOOOO0OO0OO0 and O0OOOOOOOO0OO0OO0 !=''and O0OOOOOOOO0OO0OO0 !='null':#line:313
            OO0OO000O0O00O00O =O0OOOOOOOO0OO0OO0 #line:314
    O000O000OO000O0O0 =model_admin .model #line:316
    OO00OO0OOO0O0OOO0 =model_admin .get_queryset (request )#line:319
    if not OO00OO0OOO0O0OOO0 :#line:320
        OO00OO0OOO0O0OOO0 =O000O000OO000O0O0 .objects .get_queryset ()#line:322
    O00OOOOOOO0O0OO0O =request .POST .get ('filters')#line:324
    OOOO00O0O00OO00O0 ={}#line:327
    OOO0O0O0O000OOO0O =request .POST .get ('search')#line:330
    if OOO0O0O0O000OOO0O and OOO0O0O0O000OOO0O !='':#line:331
        O00000O00OOOO00OO =Q ()#line:332
        OOOOO000O0OO00O0O =model_admin .search_fields #line:333
        for O0O0O0OO000O0OOOO in OOOOO000O0OO00O0O :#line:334
            O00000O00OOOO00OO =O00000O00OOOO00OO |Q (**{O0O0O0OO000O0OOOO +"__icontains":OOO0O0O0O000OOO0O })#line:335
        OO00OO0OOO0O0OOO0 =OO00OO0OOO0O0OOO0 .filter (O00000O00OOOO00OO )#line:336
    if O00OOOOOOO0O0OO0O :#line:338
        O00OOOOOOO0O0OO0O =json .loads (O00OOOOOOO0O0OO0O )#line:339
        for OOOO0O000000OO00O in O00OOOOOOO0O0OO0O :#line:340
            if OOOO0O000000OO00O in model_admin .filter_mappers :#line:342
                O0000O000OOO0O000 =model_admin .filter_mappers [OOOO0O000000OO00O ]#line:344
                O0000O000OOO0O000 .used_parameters =O00OOOOOOO0O0OO0O #line:345
                OO00OO0OOO0O0OOO0 =O0000O000OOO0O000 .queryset (request ,OO00OO0OOO0O0OOO0 )#line:347
            else :#line:348
                O0OO0000000O0O00O =O00OOOOOOO0O0OO0O .get (OOOO0O000000OO00O )#line:354
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',O0OO0000000O0O00O ):#line:356
                    OOOOO00OOOO00OOO0 =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0OO0000000O0O00O )#line:357
                    if OOOOO00OOOO00OOO0 :#line:358
                        OOOOO0OOO0O000OOO =OOOOO00OOOO00OOO0 [0 ]#line:359
                        O0000OOO00OO0O00O =datetime .datetime .strptime (OOOOO0OOO0O000OOO ,'%Y-%m-%d %H:%M:%S')#line:360
                        O0OO0000000O0O00O =O0000OOO00OO0O00O +datetime .timedelta (hours =8 )#line:361
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O0OO0000000O0O00O ):#line:362
                    O0OO0000000O0O00O =datetime .datetime .strptime (O0OO0000000O0O00O ,'%Y-%m-%d %H:%M:%S')#line:364
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',O0OO0000000O0O00O ):#line:365
                    O0OO0000000O0O00O =datetime .datetime .strptime (O0OO0000000O0O00O ,'%Y-%m-%d')#line:367
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',O0OO0000000O0O00O ):#line:368
                    O0OO0000000O0O00O =time .strptime (O0OO0000000O0O00O ,' %H:%M:%S')#line:370
                OOOO00O0O00OO00O0 [OOOO0O000000OO00O ]=O0OO0000000O0O00O #line:371
    O0O000OO00O00O000 =OO00OO0OOO0O0OOO0 .filter (**OOOO00O0O00OO00O0 ).order_by (OO0OO000O0O00O00O )#line:373
    OO0O0O00OO0OO0000 =model_admin .list_per_page #line:374
    if 'page_size'in request .POST :#line:375
        OO0O0OO00O0O0O000 =int (request .POST .get ('page_size'))#line:376
        if OO0O0OO00O0O0O000 !=0 :#line:377
            OO0O0O00OO0OO0000 =OO0O0OO00O0O0O000 #line:378
    O0OO000O000OO0OO0 =Paginator (O0O000OO00O00O000 ,OO0O0O00OO0OO0000 )#line:380
    if OOOO0OOOOO00000O0 >O0OO000O000OO0OO0 .num_pages :#line:381
        OOOO0OOOOO00000O0 =O0OO000O000OO0OO0 .num_pages #line:382
    O0O00O00OOO0OOOOO =O0OO000O000OO0OO0 .page (OOOO0OOOOO00000O0 )#line:383
    O0O00O0O000OO000O =O0O00O00OOO0OOOOO .object_list #line:384
    O0OO00000OOO000OO =[]#line:388
    for O0OOOOO0OOO000O00 in O0O00O0O000OO000O :#line:389
        O0000000O0OO00O0O ={}#line:390
        for O0OOOOOOOO0OO0OO0 in O0O0000O0OOOO0OO0 :#line:391
            OOOO0O000000OO00O =O0OOOOOOOO0OO0OO0 +'_choices'#line:392
            if OOOO0O000000OO00O in OO0000OOOO0000OOO :#line:393
                OO0O0O000OOOO0O0O =getattr (O0OOOOO0OOO000O00 ,O0OOOOOOOO0OO0OO0 )#line:394
                O00O00O00O0OO00OO =OO0000OOOO0000OOO [OOOO0O000000OO00O ]#line:395
                if OO0O0O000OOOO0O0O in O00O00O00O0OO00OO :#line:396
                    OO0O0O000OOOO0O0O =O00O00O00O0OO00OO .get (OO0O0O000OOOO0O0O )#line:397
            elif O0OOOOOOOO0OO0OO0 in OO0000OOOO0000OOO :#line:398
                OO0O0O000OOOO0O0O =getattr (O0OOOOO0OOO000O00 ,O0OOOOOOOO0OO0OO0 )#line:399
                O00O00O00O0OO00OO =OO0000OOOO0000OOO [O0OOOOOOOO0OO0OO0 ]#line:400
                if OO0O0O000OOOO0O0O in O00O00O00O0OO00OO :#line:401
                    OO0O0O000OOOO0O0O =O00O00O00O0OO00OO .get (OO0O0O000OOOO0O0O )#line:402
            else :#line:403
                OO0O0O000OOOO0O0O =getattr (O0OOOOO0OOO000O00 ,O0OOOOOOOO0OO0OO0 )#line:404
            if OO000OOO00000O0O0 :#line:408
                OO0O0O000OOOO0O0O =OO000OOO00000O0O0 (O0OOOOO0OOO000O00 ,O0OOOOOOOO0OO0OO0 ,OO0O0O000OOOO0O0O )#line:409
            if issubclass (OO0O0O000OOOO0O0O .__class__ ,Model ):#line:410
                OO0O0O000OOOO0O0O =str (OO0O0O000OOOO0O0O )#line:411
            O0000000O0OO00O0O [O0OOOOOOOO0OO0OO0 ]=OO0O0O000OOOO0O0O #line:412
        for OOO0O0000OO0000OO in O00OOOO00OOO00OO0 :#line:414
            try :#line:415
                OO0O0O000OOOO0O0O =getattr (model_admin .model ,OOO0O0000OO0000OO ).__call__ (O0OOOOO0OOO000O00 )#line:416
                if OO000OOO00000O0O0 :#line:417
                    OO0O0O000OOOO0O0O =OO000OOO00000O0O0 (O0OOOOO0OOO000O00 ,OOO0O0000OO0000OO ,OO0O0O000OOOO0O0O )#line:418
                O0000000O0OO00O0O [OOO0O0000OO0000OO ]=OO0O0O000OOOO0O0O #line:419
            except Exception as OOO0000O0OO0OO000 :#line:420
                raise Exception (OOO0000O0OO0OO000 .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (OOO0O0000OO0000OO .__qualname__ ,OOO0O0000OO0000OO .__qualname__ ))#line:422
        O0000000O0OO00O0O ['_id']=getattr (O0OOOOO0OOO000O00 ,model_admin .model .id .field_name )#line:424
        O0OO00000OOO000OO .append (O0000000O0OO00O0O )#line:425
    if OOOO0OOOOO00000O0 <=1 :#line:433
        O0OO0O0OOOOO0OO0O =True #line:434
        if hasattr (model_admin ,'actions_show'):#line:435
            O0OO0O0OOOOO0OO0O =getattr (model_admin ,'actions_show')!=False #line:436
        OOOO0O000O0OOO0OO ['headers']=OO000O0O0O000OOOO #line:437
        OOOO0O000O0OOO0OO ['exts']={'showId':'id'in O0O0000O0OOOO0OO0 ,'actions_show':O0OO0O0OOOOO0OO0O ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:443
        OOOO0O000O0OOO0OO ['custom_button']=get_custom_button (request ,model_admin )#line:447
    OOOO0O000O0OOO0OO ['rows']=O0OO00000OOO000OO #line:455
    OOOO0O000O0OOO0OO ['paginator']={'page_size':OO0O0O00OO0OO0000 ,'count':O0OO000O000OO0OO0 .count ,'page_count':O0OO000O000OO0OO0 .num_pages }#line:461
    return write (OOOO0O000O0OOO0OO )#line:463
def process_active (request ):#line:466
    OO00O0O0O00OO00OO =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:468
    O0OOO0OOO0O00O00O =request .path #line:469
    O0OO0O0OOO0O00O00 =request .POST #line:471
    OO0O00OO00O000O0O =O0OO0O0OOO0O00O00 .get ('action')#line:472
    if OO0O00OO00O000O0O :#line:473
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:474
    elif O0OOO0OOO0O00O00O not in OO00O0O0O00OO00OO :#line:475
        return render (request ,'admin/active.html')#line:476
def process_lic (request ):#line:479
    OO00000O0OOOO000O =conf .get_device_id ()#line:481
    O0OO0O00OO00O0000 =request .POST .get ('active_code')#line:482
    OOOO000OO0000000O =conf .get_server_url ()+'/active'#line:484
    O00OO000OO0000OO0 =requests .post (OOOO000OO0000000O ,data ={'device_id':OO00000O0OOOO000O ,'active_code':O0OO0O00OO00O0000 })#line:488
    if O00OO000OO0000OO0 .status_code ==200 :#line:490
        O0000OOOOO00OOOO0 =O00OO000OO0000OO0 .json ()#line:491
        if O0000OOOOO00OOOO0 .get ('state')is True :#line:492
            OOOOOOOOO0OO00OOO =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:494
            O0OOO0000OO0O00OO =open (OOOOOOOOO0OO00OOO +'/simplepro/simpepro.lic','wb')#line:497
            OO00OOOO00OOOOO00 =base64 .b64decode (O0000OOOOO00OOOO0 .get ('license'))#line:500
            OOOOOO0OOOOOO00OO =base64 .b64encode (bytes (O0000OOOOO00OOOO0 .get ('private_key'),encoding ='utf8'))#line:501
            O0OOO0000OO0O00OO .write (struct .pack ('h',len (OO00OOOO00OOOOO00 )))#line:503
            O0OOO0000OO0O00OO .write (struct .pack ('h',len (OOOOOO0OOOOOO00OO )))#line:504
            O0OOO0000OO0O00OO .write (OO00OOOO00OOOOO00 )#line:505
            O0OOO0000OO0O00OO .write (OOOOOO0OOOOOO00OO )#line:506
            O0OOO0000OO0O00OO .close ()#line:507
            print ('写入激活文件，位置：{}'.format (OOOOOOOOO0OO00OOO +'/simpepro.lic'))#line:508
        return write_obj (O0000OOOOO00OOOO0 )#line:510
    return write ({},'error',False )#line:511
def process_info (request ):#line:514
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:518
