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
        O000000000000OOOO =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:30
        if not os .path .exists (O000000000000OOOO +'/simplepro/simpepro.lic'):#line:31
            return False #line:32
        global cache_d #line:33
        if cache_d :#line:34
            return cache_d #line:35
        O000O0OO0OO00OOO0 =open (O000000000000OOOO +'/simplepro/simpepro.lic','rb')#line:36
        OO00O0OOOOO0OO00O =O000O0OO0OO00OOO0 .read ()#line:37
        O00OO0000000OOOOO ,=struct .unpack ('h',OO00O0OOOOO0OO00O [0 :2 ])#line:38
        O00000O000000O0OO ,=struct .unpack ('h',OO00O0OOOOO0OO00O [2 :4 ])#line:39
        O0O0OO0O0O0O00OOO =OO00O0OOOOO0OO00O [4 :O00OO0000000OOOOO +4 ]#line:40
        OO0O0O0000000O000 =base64 .b64decode (OO00O0OOOOO0OO00O [O00OO0000000OOOOO +4 :])#line:42
        OO00O0O0O00OO0OOO =rsa .PrivateKey .load_pkcs1 (OO0O0O0000000O000 )#line:44
        OO0O0OO0OOOO0OO00 =rsa .decrypt (O0O0OO0O0O0O00OOO ,OO00O0O0O00OO0OOO ).decode ()#line:45
        OOOOOOO00OOO0000O =json .loads (OO0O0OO0OOOO0OO00 )#line:46
        cache_d =OOOOOOO00OOO0000O #line:47
    except Exception as O0O0OOO00O0O0OOO0 :#line:48
        pass #line:49
    return OOOOOOO00OOO0000O #line:50
def OO0O0OO0OOO0OO0O0 (request ):#line:53
    try :#line:54
        O000O0O0OO0O0OOOO =O0O0OOO0OOO0OO0O0 ()#line:55
        O0O0O0O0O0OOOOO0O =O000O0O0OO0O0OOOO .get ('end_date').split (' ')[0 ]#line:57
        OO0OOOO00OO0OO0OO =datetime .datetime .strptime (O0O0O0O0O0OOOOO0O ,'%Y-%m-%d')#line:58
        O000O0OOO0O0O00O0 =datetime .datetime .now ()#line:59
        if O000O0OOO0O0O00O0 >OO0OOOO00OO0OO0OO :#line:60
            request .msg ='激活码已经过期，请重新购买！'#line:61
            return False #line:62
        OO000O0O00OO0OO00 =O000O0O0OO0O0OOOO .get ('device_id')#line:63
        if str (conf .get_device_id ())!=str (OO000O0O00OO0OO00 ):#line:64
            request .msg ='激活码和设备不匹配，请重新激活！'#line:65
            return False #line:66
        return True #line:67
    except Exception as OO000O000O0OOO0OO :#line:68
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
            class OOO000000OOOOOOOO :#line:91
                js =('admin/group/js/group.js',)#line:92
            view_func .model_admin .Media =OOO000000OOOOOOOO #line:94
            view_func .model_admin .list_display =('id','name')#line:95
            view_func .model_admin .list_per_page =10 #line:96
        O000OOOO000000O0O =request .path #line:97
        O00OO0O0O0O0OO000 =view_func .model_admin .opts #line:99
        O000OO00O0OO0O0OO ='admin:{}_{}_changelist'.format (O00OO0O0O0O0OO000 .app_label ,O00OO0O0O0O0OO000 .model_name )#line:100
        if reverse (O000OO00O0OO0O0OO )==O000OOOO000000O0O :#line:102
            URL_CACHE [request .path ]=view_func .model_admin #line:104
            return process_list (request ,view_func .model_admin )#line:105
def custom_action (request ,model_admin ):#line:108
    ""#line:109
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:112
    OO00O000OOOO00O00 ={'state':True ,'msg':'操作成功！',}#line:117
    try :#line:118
        OO00OOO0OO0OO0000 =request .POST #line:119
        OO000OO0OO0OOO0OO =OO00OOO0OO0OO0000 .get ('all')#line:121
        OO0O0000OOO00O0OO =OO00OOO0OO0OO0000 .get ('ids')#line:122
        OOO00OOOOO00OO00O =OO00OOO0OO0OO0000 .get ('key')#line:123
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:129
        O00OOO0O000OO000O =model_admin .model #line:130
        O000O00000OOO00OO =O00OOO0O000OO000O .objects .get_queryset ()#line:131
        if OO000OO0OO0OOO0OO =='0':#line:134
            O00O0000O0OOO0000 ={}#line:135
            O00O0000O0OOO0000 [O00OOO0O000OO000O .id .field_name +'__in']=OO0O0000OOO00O0OO .split (',')#line:136
            O000O00000OOO00OO =O000O00000OOO00OO .filter (**O00O0000O0OOO0000 )#line:138
        OO000OOOO0OOOO000 =getattr (model_admin ,OOO00OOOOO00OO00O )#line:140
        O000O0O00O00000OO =OO000OOOO0OOOO000 (request ,O000O00000OOO00OO )#line:141
        if O000O0O00O00000OO and isinstance (O000O0O00O00000OO ,dict ):#line:144
            OO00O000OOOO00O00 =O000O0O00O00000OO #line:145
    except Exception as O00O00O0O0OOO0000 :#line:147
        OO00O000OOOO00O00 ={'state':False ,'msg':O00O00O0O0OOO0000 .args [0 ]}#line:151
    return HttpResponse (json .dumps (OO00O000OOOO00O00 ,cls =LazyEncoder ),content_type ='application/json')#line:153
def process_list (request ,model_admin ):#line:156
    OO0000OOOOOOO0O0O =request .POST .get ('action')#line:157
    OO000O0OO000OO0O0 ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:164
    if OO0000OOOOOOO0O0O and OO0000OOOOOOO0O0O not in OO000O0OO000OO0O0 :#line:166
        pass #line:167
    elif OO0000OOOOOOO0O0O :#line:168
        OOOOO0OOO0O00OO0O ={}#line:170
        OOO00O000000O0OOO =model_admin .get_changelist_instance (request )#line:171
        if OOO00O000000O0OOO .has_filters :#line:172
            for O0OO0O000OO00OO0O in OOO00O000000O0OOO .filter_specs :#line:173
                O0OOOOOO0O00O00O0 =None #line:174
                if hasattr (O0OO0O000OO00OO0O ,'field_path'):#line:175
                    O0OOOOOO0O00O00O0 =O0OO0O000OO00OO0O .field_path #line:176
                elif hasattr (O0OO0O000OO00OO0O ,'parameter_name'):#line:177
                    O0OOOOOO0O00O00O0 =O0OO0O000OO00OO0O .parameter_name #line:178
                elif hasattr (O0OO0O000OO00OO0O ,'lookup_kwarg'):#line:179
                    O0OOOOOO0O00O00O0 =O0OO0O000OO00OO0O .lookup_kwarg #line:180
                if O0OOOOOO0O00O00O0 :#line:181
                    OOOOO0OOO0O00OO0O [O0OOOOOO0O00O00O0 ]=O0OO0O000OO00OO0O #line:182
        model_admin .filter_mappers =OOOOO0OOO0O00OO0O #line:183
        return OO000O0OO000OO0O0 [OO0000OOOOOOO0O0O ](request ,model_admin )#line:185
    else :#line:188
        OOO00O000000O0OOO =model_admin .get_changelist_instance (request )#line:192
        model_admin .has_filters =OOO00O000000O0OOO .has_filters #line:193
        model_admin .filter_specs =OOO00O000000O0OOO .filter_specs #line:194
        OO0OOO0OO0000OOO0 =[]#line:195
        if model_admin .has_filters :#line:196
            for O0OO0O000OO00OO0O in model_admin .filter_specs :#line:197
                if hasattr (O0OO0O000OO00OO0O ,'field_path'):#line:199
                    OO0OOO0OO0000OOO0 .append (O0OO0O000OO00OO0O .field_path )#line:200
                elif hasattr (O0OO0O000OO00OO0O ,'parameter_name'):#line:201
                    OO0OOO0OO0000OOO0 .append (O0OO0O000OO00OO0O .parameter_name )#line:202
                elif hasattr (O0OO0O000OO00OO0O ,'lookup_kwarg'):#line:203
                    OO0OOO0OO0000OOO0 .append (O0OO0O000OO00OO0O .lookup_kwarg )#line:204
        OO0O00000OOOOOOOO =None #line:207
        if hasattr (model_admin ,'Media'):#line:209
            OOO000O0OOO0OO0O0 =model_admin .Media #line:210
            OO0O00000OOOOOOOO ={}#line:211
            if hasattr (OOO000O0OOO0OO0O0 ,'js'):#line:212
                O00O0OOOO00OOO000 =[]#line:213
                O0O0O00000000O00O =getattr (OOO000O0OOO0OO0O0 ,'js')#line:215
                for O0OOO000000OO0OOO in O0O0O00000000O00O :#line:217
                    if not O0OOO000000OO0OOO .endswith ('import_export/action_formats.js'):#line:218
                        O00O0OOOO00OOO000 .append (O0OOO000000OO0OOO )#line:219
                OO0O00000OOOOOOOO ['js']=O00O0OOOO00OOO000 #line:221
            if hasattr (OOO000O0OOO0OO0O0 ,'css'):#line:222
                OO0O00000OOOOOOOO ['css']=getattr (OOO000O0OOO0OO0O0 ,'css')#line:223
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':OO0O00000OOOOOOOO ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (OO0OOO0OO0000OOO0 ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:242
def delete_data (request ,model_admin ):#line:245
    ""#line:250
    O0OOOO0O00OOO000O =model_admin .model #line:252
    OO000000OO0000O0O =O0OOOO0O00OOO000O .objects .get_queryset ()#line:253
    O0O0OO0OOOO0000O0 =request .POST .get ('ids')#line:254
    O0O00OO0OO00000OO ={'state':True ,'msg':'删除成功！'}#line:259
    if O0O0OO0OOOO0000O0 :#line:261
        O0O0OO0OOOO0000O0 =O0O0OO0OOOO0000O0 .split (',')#line:262
        OOO0OO000O0OOO00O ={}#line:263
        OOO0OO000O0OOO00O [O0OOOO0O00OOO000O .id .field_name +'__in']=O0O0OO0OOOO0000O0 #line:264
        OO000000OO0000O0O =OO000000OO0000O0O .filter (**OOO0OO000O0OOO00O )#line:265
        try :#line:267
            if hasattr (model_admin ,'delete_queryset'):#line:268
                OO0OO0000OO0O0O0O =getattr (model_admin ,'delete_queryset')(request ,OO000000OO0000O0O )#line:269
                if OO0OO0000OO0O0O0O :#line:270
                    OO000000OO0000O0O =OO0OO0000OO0O0O0O #line:271
                    OO000000OO0000O0O .delete ()#line:272
        except Exception as OOO0000OO0O00OOOO :#line:274
            O0O00OO0OO00000OO ={'state':False ,'msg':OOO0000OO0O00OOOO .args [0 ]}#line:278
    return write (O0O00OO0OO00000OO )#line:279
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
    OOO00O0O0O000O00O ={}#line:299
    O00O0OO0000000O0O =request .POST .get ('current_page')#line:301
    if O00O0OO0000000O0O :#line:302
        O00O0OO0000000O0O =int (O00O0OO0000000O0O )#line:303
    else :#line:304
        O00O0OO0000000O0O =1 #line:305
    O0OO00O000OOO00O0 ,O00O0OOO00O0O0O0O ,OO0OO000O000O0O00 ,OOO0OO00OO00O0O0O ,O0OO00O00OOO00OO0 =get_model_info (model_admin ,request )#line:307
    OO000O00OOO00O00O ='-'+model_admin .model .id .field_name #line:309
    if 'order_by'in request .POST :#line:311
        OO00OO0O00O000OOO =request .POST .get ('order_by')#line:312
        if OO00OO0O00O000OOO and OO00OO0O00O000OOO !=''and OO00OO0O00O000OOO !='null':#line:313
            OO000O00OOO00O00O =OO00OO0O00O000OOO #line:314
    OO0000OOOOO000OOO =model_admin .model #line:316
    O00000OO0O0OOOO0O =model_admin .get_queryset (request )#line:319
    if not O00000OO0O0OOOO0O :#line:320
        O00000OO0O0OOOO0O =OO0000OOOOO000OOO .objects .get_queryset ()#line:322
    O00OO00OO0O0O0OOO =request .POST .get ('filters')#line:324
    OOOO0OOOOO0OO00OO ={}#line:327
    O0000OOO0OO0O00O0 =request .POST .get ('search')#line:330
    if O0000OOO0OO0O00O0 and O0000OOO0OO0O00O0 !='':#line:331
        OOOOOOO0000O00O00 =Q ()#line:332
        OO0O0000OOOOOOOO0 =model_admin .search_fields #line:333
        for OO0O000OOOOOO00OO in OO0O0000OOOOOOOO0 :#line:334
            OOOOOOO0000O00O00 =OOOOOOO0000O00O00 |Q (**{OO0O000OOOOOO00OO +"__icontains":O0000OOO0OO0O00O0 })#line:335
        O00000OO0O0OOOO0O =O00000OO0O0OOOO0O .filter (OOOOOOO0000O00O00 )#line:336
    if O00OO00OO0O0O0OOO :#line:338
        O00OO00OO0O0O0OOO =json .loads (O00OO00OO0O0O0OOO )#line:339
        for OOOO0O0O0000000OO in O00OO00OO0O0O0OOO :#line:340
            if OOOO0O0O0000000OO in model_admin .filter_mappers :#line:342
                O00O0O000000OO00O =model_admin .filter_mappers [OOOO0O0O0000000OO ]#line:344
                O00O0O000000OO00O .used_parameters =O00OO00OO0O0O0OOO #line:345
                O00000OO0O0OOOO0O =O00O0O000000OO00O .queryset (request ,O00000OO0O0OOOO0O )#line:347
            else :#line:348
                O000O0O0O0000OO0O =O00OO00OO0O0O0OOO .get (OOOO0O0O0000000OO )#line:354
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',O000O0O0O0000OO0O ):#line:356
                    O0O00O0OOO0O00OOO =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O000O0O0O0000OO0O )#line:357
                    if O0O00O0OOO0O00OOO :#line:358
                        O0OOOO0O00OO0O0OO =O0O00O0OOO0O00OOO [0 ]#line:359
                        OO00OO00000OOOO0O =datetime .datetime .strptime (O0OOOO0O00OO0O0OO ,'%Y-%m-%d %H:%M:%S')#line:360
                        O000O0O0O0000OO0O =OO00OO00000OOOO0O +datetime .timedelta (hours =8 )#line:361
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O000O0O0O0000OO0O ):#line:362
                    O000O0O0O0000OO0O =datetime .datetime .strptime (O000O0O0O0000OO0O ,'%Y-%m-%d %H:%M:%S')#line:364
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',O000O0O0O0000OO0O ):#line:365
                    O000O0O0O0000OO0O =datetime .datetime .strptime (O000O0O0O0000OO0O ,'%Y-%m-%d')#line:367
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',O000O0O0O0000OO0O ):#line:368
                    O000O0O0O0000OO0O =time .strptime (O000O0O0O0000OO0O ,' %H:%M:%S')#line:370
                OOOO0OOOOO0OO00OO [OOOO0O0O0000000OO ]=O000O0O0O0000OO0O #line:371
    O0O000OO00OO0OO0O =O00000OO0O0OOOO0O .filter (**OOOO0OOOOO0OO00OO ).order_by (OO000O00OOO00O00O )#line:373
    OOOOO0O00O0OO0OOO =model_admin .list_per_page #line:374
    if 'page_size'in request .POST :#line:375
        O00000OO0000OO00O =int (request .POST .get ('page_size'))#line:376
        if O00000OO0000OO00O !=0 :#line:377
            OOOOO0O00O0OO0OOO =O00000OO0000OO00O #line:378
    O0000OOOOO0OO0000 =Paginator (O0O000OO00OO0OO0O ,OOOOO0O00O0OO0OOO )#line:380
    if O00O0OO0000000O0O >O0000OOOOO0OO0000 .num_pages :#line:381
        O00O0OO0000000O0O =O0000OOOOO0OO0000 .num_pages #line:382
    O00O0OOO000O0O000 =O0000OOOOO0OO0000 .page (O00O0OO0000000O0O )#line:383
    OOO0OOOOOOO000OO0 =O00O0OOO000O0O000 .object_list #line:384
    OO00O0OO0OO000OOO =[]#line:388
    for OO00O0O0O0OO000OO in OOO0OOOOOOO000OO0 :#line:389
        O0OOO0000O00O0OOO ={}#line:390
        for OO00OO0O00O000OOO in O0OO00O000OOO00O0 :#line:391
            OOOO0O0O0000000OO =OO00OO0O00O000OOO +'_choices'#line:392
            if OOOO0O0O0000000OO in O0OO00O00OOO00OO0 :#line:393
                O0O0O0000OOO00O0O =getattr (OO00O0O0O0OO000OO ,OO00OO0O00O000OOO )#line:394
                O0O0OO0O0OO00O000 =O0OO00O00OOO00OO0 [OOOO0O0O0000000OO ]#line:395
                if O0O0O0000OOO00O0O in O0O0OO0O0OO00O000 :#line:396
                    O0O0O0000OOO00O0O =O0O0OO0O0OO00O000 .get (O0O0O0000OOO00O0O )#line:397
            elif OO00OO0O00O000OOO in O0OO00O00OOO00OO0 :#line:398
                O0O0O0000OOO00O0O =getattr (OO00O0O0O0OO000OO ,OO00OO0O00O000OOO )#line:399
                O0O0OO0O0OO00O000 =O0OO00O00OOO00OO0 [OO00OO0O00O000OOO ]#line:400
                if O0O0O0000OOO00O0O in O0O0OO0O0OO00O000 :#line:401
                    O0O0O0000OOO00O0O =O0O0OO0O0OO00O000 .get (O0O0O0000OOO00O0O )#line:402
            else :#line:403
                O0O0O0000OOO00O0O =getattr (OO00O0O0O0OO000OO ,OO00OO0O00O000OOO )#line:404
            if OOO0OO00OO00O0O0O :#line:408
                O0O0O0000OOO00O0O =OOO0OO00OO00O0O0O (OO00O0O0O0OO000OO ,OO00OO0O00O000OOO ,O0O0O0000OOO00O0O )#line:409
            if issubclass (O0O0O0000OOO00O0O .__class__ ,Model ):#line:410
                O0O0O0000OOO00O0O =str (O0O0O0000OOO00O0O )#line:411
            O0OOO0000O00O0OOO [OO00OO0O00O000OOO ]=O0O0O0000OOO00O0O #line:412
        for OOOOO000OOOO0O00O in O00O0OOO00O0O0O0O :#line:414
            try :#line:415
                if hasattr (model_admin ,OOOOO000OOOO0O00O ):#line:416
                    O0O0O0000OOO00O0O =getattr (model_admin ,OOOOO000OOOO0O00O ).__call__ (OO00O0O0O0OO000OO )#line:417
                else :#line:418
                    O0O0O0000OOO00O0O =getattr (model_admin .model ,OOOOO000OOOO0O00O ).__call__ (OO00O0O0O0OO000OO )#line:419
                if OOO0OO00OO00O0O0O :#line:420
                    O0O0O0000OOO00O0O =OOO0OO00OO00O0O0O (OO00O0O0O0OO000OO ,OOOOO000OOOO0O00O ,O0O0O0000OOO00O0O )#line:421
                O0OOO0000O00O0OOO [OOOOO000OOOO0O00O ]=O0O0O0000OOO00O0O #line:422
            except Exception as O0000000OOOO0OO00 :#line:423
                raise Exception (O0000000OOOO0OO00 .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (OOOOO000OOOO0O00O .__qualname__ ,OOOOO000OOOO0O00O .__qualname__ ))#line:425
        O0OOO0000O00O0OOO ['_id']=getattr (OO00O0O0O0OO000OO ,model_admin .model .id .field_name )#line:427
        OO00O0OO0OO000OOO .append (O0OOO0000O00O0OOO )#line:428
    if O00O0OO0000000O0O <=1 :#line:436
        OO0OO0OOO0OOOO00O =True #line:437
        if hasattr (model_admin ,'actions_show'):#line:438
            OO0OO0OOO0OOOO00O =getattr (model_admin ,'actions_show')!=False #line:439
        OOO00O0O0O000O00O ['headers']=OO0OO000O000O0O00 #line:440
        OOO00O0O0O000O00O ['exts']={'showId':'id'in O0OO00O000OOO00O0 ,'actions_show':OO0OO0OOO0OOOO00O ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:446
        OOO00O0O0O000O00O ['custom_button']=get_custom_button (request ,model_admin )#line:450
    OOO00O0O0O000O00O ['rows']=OO00O0OO0OO000OOO #line:458
    OOO00O0O0O000O00O ['paginator']={'page_size':OOOOO0O00O0OO0OOO ,'count':O0000OOOOO0OO0000 .count ,'page_count':O0000OOOOO0OO0000 .num_pages }#line:464
    return write (OOO00O0O0O000O00O )#line:466
def process_active (request ):#line:469
    OO0OOO0O00OO0O00O =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:471
    O0OO0000O0O0O0000 =request .path #line:472
    OOO000OO00OOO0O00 =request .POST #line:474
    OOOOO0O0OOOOOO0O0 =OOO000OO00OOO0O00 .get ('action')#line:475
    if OOOOO0O0OOOOOO0O0 :#line:476
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:477
    elif O0OO0000O0O0O0000 not in OO0OOO0O00OO0O00O :#line:478
        return render (request ,'admin/active.html')#line:479
def process_lic (request ):#line:482
    O0O00OO00O00OO0OO =conf .get_device_id ()#line:484
    O0OO0O0000OOO0O00 =request .POST .get ('active_code')#line:485
    OO00OO0O000O0OOO0 =conf .get_server_url ()+'/active'#line:487
    O00OOOOO000O00OO0 =requests .post (OO00OO0O000O0OOO0 ,data ={'device_id':O0O00OO00O00OO0OO ,'active_code':O0OO0O0000OOO0O00 })#line:491
    if O00OOOOO000O00OO0 .status_code ==200 :#line:493
        O0000OOO0OOO0OO0O =O00OOOOO000O00OO0 .json ()#line:494
        if O0000OOO0OOO0OO0O .get ('state')is True :#line:495
            O0OO0O00OOO0O0O0O =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:497
            OO0O0OO00OO000OOO =open (O0OO0O00OOO0O0O0O +'/simplepro/simpepro.lic','wb')#line:500
            O0OO0O0OOOO000000 =base64 .b64decode (O0000OOO0OOO0OO0O .get ('license'))#line:503
            O0O00O00OOOO000OO =base64 .b64encode (bytes (O0000OOO0OOO0OO0O .get ('private_key'),encoding ='utf8'))#line:504
            OO0O0OO00OO000OOO .write (struct .pack ('h',len (O0OO0O0OOOO000000 )))#line:506
            OO0O0OO00OO000OOO .write (struct .pack ('h',len (O0O00O00OOOO000OO )))#line:507
            OO0O0OO00OO000OOO .write (O0OO0O0OOOO000000 )#line:508
            OO0O0OO00OO000OOO .write (O0O00O00OOOO000OO )#line:509
            OO0O0OO00OO000OOO .close ()#line:510
            print ('写入激活文件，位置：{}'.format (O0OO0O00OOO0O0O0O +'/simpepro.lic'))#line:511
        return write_obj (O0000OOO0OOO0OO0O )#line:513
    return write ({},'error',False )#line:514
def process_info (request ):#line:517
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:521
