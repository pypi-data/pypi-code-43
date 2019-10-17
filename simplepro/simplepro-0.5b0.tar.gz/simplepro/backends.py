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
        O0O0OOOOO0OOO000O =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:30
        if not os .path .exists (O0O0OOOOO0OOO000O +'/simplepro/simpepro.lic'):#line:31
            return False #line:32
        global cache_d #line:33
        if cache_d :#line:34
            return cache_d #line:35
        OO0O00OOO0O0OO0OO =open (O0O0OOOOO0OOO000O +'/simplepro/simpepro.lic','rb')#line:36
        OOO0OO000000O0OOO =OO0O00OOO0O0OO0OO .read ()#line:37
        OOO0OOO0OOO0O0O0O ,=struct .unpack ('h',OOO0OO000000O0OOO [0 :2 ])#line:38
        O00OOO0O0O0OOO00O ,=struct .unpack ('h',OOO0OO000000O0OOO [2 :4 ])#line:39
        OO000O000OOOOO000 =OOO0OO000000O0OOO [4 :OOO0OOO0OOO0O0O0O +4 ]#line:40
        OO000O000OO00O0OO =base64 .b64decode (OOO0OO000000O0OOO [OOO0OOO0OOO0O0O0O +4 :])#line:42
        O0000OO0O0000000O =rsa .PrivateKey .load_pkcs1 (OO000O000OO00O0OO )#line:44
        O0OO00O0O0000OO0O =rsa .decrypt (OO000O000OOOOO000 ,O0000OO0O0000000O ).decode ()#line:45
        O0000000O0OOOOOO0 =json .loads (O0OO00O0O0000OO0O )#line:46
        cache_d =O0000000O0OOOOOO0 #line:47
    except Exception as OO00OO0000O0O00O0 :#line:48
        pass #line:49
    return O0000000O0OOOOOO0 #line:50
def OO0O0OO0OOO0OO0O0 (request ):#line:53
    try :#line:54
        OO0O0OO0000OO00O0 =O0O0OOO0OOO0OO0O0 ()#line:55
        OOO00OO0O00O000O0 =OO0O0OO0000OO00O0 .get ('end_date').split (' ')[0 ]#line:57
        O0OOOOO000OOO0000 =datetime .datetime .strptime (OOO00OO0O00O000O0 ,'%Y-%m-%d')#line:58
        OOOOO00OO0O000O0O =datetime .datetime .now ()#line:59
        if OOOOO00OO0O000O0O >O0OOOOO000OOO0000 :#line:60
            request .msg ='激活码已经过期，请重新购买！'#line:61
            return False #line:62
        O00O0O0O000O0O0O0 =OO0O0OO0000OO00O0 .get ('device_id')#line:63
        if str (conf .get_device_id ())!=str (O00O0O0O000O0O0O0 ):#line:64
            request .msg ='激活码和设备不匹配，请重新激活！'#line:65
            return False #line:66
        return True #line:67
    except Exception as OOO0O0OO0O00OO0OO :#line:68
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
            class OO00OOO00O000O00O :#line:91
                js =('admin/group/js/group.js',)#line:92
            view_func .model_admin .Media =OO00OOO00O000O00O #line:94
            view_func .model_admin .list_display =('id','name')#line:95
            view_func .model_admin .list_per_page =10 #line:96
        O0OOO000OO000OOO0 =request .path #line:97
        OOOOO00O0OOOOO000 =view_func .model_admin .opts #line:99
        O0OOO0OO0000O00O0 ='admin:{}_{}_changelist'.format (OOOOO00O0OOOOO000 .app_label ,OOOOO00O0OOOOO000 .model_name )#line:100
        if reverse (O0OOO0OO0000O00O0 )==O0OOO000OO000OOO0 :#line:102
            URL_CACHE [request .path ]=view_func .model_admin #line:104
            return process_list (request ,view_func .model_admin )#line:105
def custom_action (request ,model_admin ):#line:108
    ""#line:109
    """
        默认，执行成功就会返回成功，失败就失败，如果用户自己有返回数据，就用用户返回的
    """#line:112
    O0000OO00000O00O0 ={'state':True ,'msg':'操作成功！',}#line:117
    try :#line:118
        O0OO00O0O000O0O0O =request .POST #line:119
        O00000O0O0O0000OO =O0OO00O0O000O0O0O .get ('all')#line:121
        OOO0OO00O000O00O0 =O0OO00O0O000O0O0O .get ('ids')#line:122
        OO00O000000O00OO0 =O0OO00O0O000O0O0O .get ('key')#line:123
        """
        action: "custom_action"
        all: 0
        ids: "102,100"
        key: "make_copy"""#line:129
        OO00O0OO0O0000OO0 =model_admin .model #line:130
        O000O0000O0000O00 =OO00O0OO0O0000OO0 .objects .get_queryset ()#line:131
        if O00000O0O0O0000OO =='0':#line:134
            OOOO00OOO00O000OO ={}#line:135
            OOOO00OOO00O000OO [OO00O0OO0O0000OO0 .id .field_name +'__in']=OOO0OO00O000O00O0 .split (',')#line:136
            O000O0000O0000O00 =O000O0000O0000O00 .filter (**OOOO00OOO00O000OO )#line:138
        O000OOO00000OOO00 =getattr (model_admin ,OO00O000000O00OO0 )#line:140
        O00O0OOOO0000OOO0 =O000OOO00000OOO00 (request ,O000O0000O0000O00 )#line:141
        if O00O0OOOO0000OOO0 and isinstance (O00O0OOOO0000OOO0 ,dict ):#line:144
            O0000OO00000O00O0 =O00O0OOOO0000OOO0 #line:145
    except Exception as OO0000OO0OO000OOO :#line:147
        O0000OO00000O00O0 ={'state':False ,'msg':OO0000OO0OO000OOO .args [0 ]}#line:151
    return HttpResponse (json .dumps (O0000OO00000O00O0 ,cls =LazyEncoder ),content_type ='application/json')#line:153
def process_list (request ,model_admin ):#line:156
    OO0OOOOO0O0O00O00 =request .POST .get ('action')#line:157
    O0O0O0OO00OO00O0O ={'list':list_data ,'delete':delete_data ,'custom_action':custom_action }#line:164
    if OO0OOOOO0O0O00O00 and OO0OOOOO0O0O00O00 not in O0O0O0OO00OO00O0O :#line:166
        pass #line:167
    elif OO0OOOOO0O0O00O00 :#line:168
        O0OO0O00000OO0O00 ={}#line:170
        OO0O0O0O0000O0O00 =model_admin .get_changelist_instance (request )#line:171
        if OO0O0O0O0000O0O00 .has_filters :#line:172
            for O0OO0000OOO0O00O0 in OO0O0O0O0000O0O00 .filter_specs :#line:173
                O00O000O0000O00OO =None #line:174
                if hasattr (O0OO0000OOO0O00O0 ,'field_path'):#line:175
                    O00O000O0000O00OO =O0OO0000OOO0O00O0 .field_path #line:176
                elif hasattr (O0OO0000OOO0O00O0 ,'parameter_name'):#line:177
                    O00O000O0000O00OO =O0OO0000OOO0O00O0 .parameter_name #line:178
                elif hasattr (O0OO0000OOO0O00O0 ,'lookup_kwarg'):#line:179
                    O00O000O0000O00OO =O0OO0000OOO0O00O0 .lookup_kwarg #line:180
                if O00O000O0000O00OO :#line:181
                    O0OO0O00000OO0O00 [O00O000O0000O00OO ]=O0OO0000OOO0O00O0 #line:182
        model_admin .filter_mappers =O0OO0O00000OO0O00 #line:183
        return O0O0O0OO00OO00O0O [OO0OOOOO0O0O00O00 ](request ,model_admin )#line:185
    else :#line:188
        OO0O0O0O0000O0O00 =model_admin .get_changelist_instance (request )#line:192
        model_admin .has_filters =OO0O0O0O0000O0O00 .has_filters #line:193
        model_admin .filter_specs =OO0O0O0O0000O0O00 .filter_specs #line:194
        O00OOO0O0O0O0OOOO =[]#line:195
        if model_admin .has_filters :#line:196
            for O0OO0000OOO0O00O0 in model_admin .filter_specs :#line:197
                if hasattr (O0OO0000OOO0O00O0 ,'field_path'):#line:199
                    O00OOO0O0O0O0OOOO .append (O0OO0000OOO0O00O0 .field_path )#line:200
                elif hasattr (O0OO0000OOO0O00O0 ,'parameter_name'):#line:201
                    O00OOO0O0O0O0OOOO .append (O0OO0000OOO0O00O0 .parameter_name )#line:202
                elif hasattr (O0OO0000OOO0O00O0 ,'lookup_kwarg'):#line:203
                    O00OOO0O0O0O0OOOO .append (O0OO0000OOO0O00O0 .lookup_kwarg )#line:204
        OOOO0O0O00OO000O0 =None #line:207
        if hasattr (model_admin ,'Media'):#line:209
            OOO00O0000O00OO00 =model_admin .Media #line:210
            OOOO0O0O00OO000O0 ={}#line:211
            if hasattr (OOO00O0000O00OO00 ,'js'):#line:212
                O0OOO00OOO000O00O =[]#line:213
                O0OOO0O00OOOOOOOO =getattr (OOO00O0000O00OO00 ,'js')#line:215
                for O0O000OOOO0OOOO00 in O0OOO0O00OOOOOOOO :#line:217
                    if not O0O000OOOO0OOOO00 .endswith ('import_export/action_formats.js'):#line:218
                        O0OOO00OOO000O00O .append (O0O000OOOO0OOOO00 )#line:219
                OOOO0O0O00OO000O0 ['js']=O0OOO00OOO000O00O #line:221
            if hasattr (OOO00O0000O00OO00 ,'css'):#line:222
                OOOO0O0O00OO000O0 ['css']=getattr (OOO00O0000O00OO00 ,'css')#line:223
        return render (request ,'admin/results/list.html',{'request':request ,'cl':model_admin ,'opts':model_admin .opts ,'media':OOOO0O0O00OO000O0 ,'title':model_admin .model ._meta .verbose_name_plural ,'model':model_admin .model ,'searchModels':json .dumps (O00OOO0O0O0O0OOOO ,cls =LazyEncoder ),'has_delete_permission':has_permission (request ,model_admin ,'delete'),'has_add_permission':has_permission (request ,model_admin ,'add'),'has_change_permission':has_permission (request ,model_admin ,'change'),})#line:242
def delete_data (request ,model_admin ):#line:245
    ""#line:250
    OOOOO00OOO0O00OO0 =model_admin .model #line:252
    O0O0OO0000000O000 =OOOOO00OOO0O00OO0 .objects .get_queryset ()#line:253
    OO0OO0OO0OO0O00OO =request .POST .get ('ids')#line:254
    OOO0000O0000OOO0O ={'state':True ,'msg':'删除成功！'}#line:259
    if OO0OO0OO0OO0O00OO :#line:261
        OO0OO0OO0OO0O00OO =OO0OO0OO0OO0O00OO .split (',')#line:262
        O00OOOO00OOO000O0 ={}#line:263
        O00OOOO00OOO000O0 [OOOOO00OOO0O00OO0 .id .field_name +'__in']=OO0OO0OO0OO0O00OO #line:264
        O0O0OO0000000O000 =O0O0OO0000000O000 .filter (**O00OOOO00OOO000O0 )#line:265
        try :#line:267
            if hasattr (model_admin ,'delete_queryset'):#line:268
                OO0OOOO00000O0O00 =getattr (model_admin ,'delete_queryset')(request ,O0O0OO0000000O000 )#line:269
                if OO0OOOO00000O0O00 :#line:270
                    O0O0OO0000000O000 =OO0OOOO00000O0O00 #line:271
                    O0O0OO0000000O000 .delete ()#line:272
        except Exception as O0OOO000O00O0O0O0 :#line:274
            OOO0000O0000OOO0O ={'state':False ,'msg':O0OOO000O00O0O0O0 .args [0 ]}#line:278
    return write (OOO0000O0000OOO0O )#line:279
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
    O0O0000O000OO00O0 ={}#line:299
    O00000O0O000OOO00 =request .POST .get ('current_page')#line:301
    if O00000O0O000OOO00 :#line:302
        O00000O0O000OOO00 =int (O00000O0O000OOO00 )#line:303
    else :#line:304
        O00000O0O000OOO00 =1 #line:305
    OO0O0000O0O000O00 ,OO0O0O0000OOO00OO ,OO00000O0OO000000 ,OO0000O0O00OOOOOO ,O0OOO0OO00000OO00 =get_model_info (model_admin ,request )#line:307
    O0OOO00OOO0OO0OOO ='-'+model_admin .model .id .field_name #line:309
    if 'order_by'in request .POST :#line:311
        OOOO00O000O000O00 =request .POST .get ('order_by')#line:312
        if OOOO00O000O000O00 and OOOO00O000O000O00 !=''and OOOO00O000O000O00 !='null':#line:313
            O0OOO00OOO0OO0OOO =OOOO00O000O000O00 #line:314
    OOOO0O0OO0OO00O0O =model_admin .model #line:316
    OOOO0OO0O00OOOO0O =model_admin .get_queryset (request )#line:319
    if not OOOO0OO0O00OOOO0O :#line:320
        OOOO0OO0O00OOOO0O =OOOO0O0OO0OO00O0O .objects .get_queryset ()#line:322
    OOO0OOO00O0O0O0O0 =request .POST .get ('filters')#line:324
    OO0O00OO00O00OOOO ={}#line:327
    O0OOOOO00OOO0OOOO =request .POST .get ('search')#line:330
    if O0OOOOO00OOO0OOOO and O0OOOOO00OOO0OOOO !='':#line:331
        OOOOO00OOOOOO0O0O =Q ()#line:332
        OO0O0OO00OOO0000O =model_admin .search_fields #line:333
        for O0OO0OOO000OOOOO0 in OO0O0OO00OOO0000O :#line:334
            OOOOO00OOOOOO0O0O =OOOOO00OOOOOO0O0O |Q (**{O0OO0OOO000OOOOO0 +"__icontains":O0OOOOO00OOO0OOOO })#line:335
        OOOO0OO0O00OOOO0O =OOOO0OO0O00OOOO0O .filter (OOOOO00OOOOOO0O0O )#line:336
    if OOO0OOO00O0O0O0O0 :#line:338
        OOO0OOO00O0O0O0O0 =json .loads (OOO0OOO00O0O0O0O0 )#line:339
        for OOOOOO00000OO0O00 in OOO0OOO00O0O0O0O0 :#line:340
            if OOOOOO00000OO0O00 in model_admin .filter_mappers :#line:342
                O00O0OOOOO0OO00OO =model_admin .filter_mappers [OOOOOO00000OO0O00 ]#line:344
                O00O0OOOOO0OO00OO .used_parameters =OOO0OOO00O0O0O0O0 #line:345
                OOOO0OO0O00OOOO0O =O00O0OOOOO0OO00OO .queryset (request ,OOOO0OO0O00OOOO0O )#line:347
            else :#line:348
                O000O000OOOOOO0O0 =OOO0OOO00O0O0O0O0 .get (OOOOOO00000OO0O00 )#line:354
                if re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}\s\d{2}\:\d{2}',O000O000OOOOOO0O0 ):#line:356
                    O00O0O000O0OOOO0O =re .match (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O000O000OOOOOO0O0 )#line:357
                    if O00O0O000O0OOOO0O :#line:358
                        O0OOOOOO0OOOOOOO0 =O00O0O000O0OOOO0O [0 ]#line:359
                        O00O0O0OO0O00OOOO =datetime .datetime .strptime (O0OOOOOO0OOOOOOO0 ,'%Y-%m-%d %H:%M:%S')#line:360
                        O000O000OOOOOO0O0 =O00O0O0OO0O00OOOO +datetime .timedelta (hours =8 )#line:361
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}\s\d{2}\:\d{2}\:\d{2}',O000O000OOOOOO0O0 ):#line:362
                    O000O000OOOOOO0O0 =datetime .datetime .strptime (O000O000OOOOOO0O0 ,'%Y-%m-%d %H:%M:%S')#line:364
                elif re .fullmatch (r'\d{4}\-\d{2}-\d{2}',O000O000OOOOOO0O0 ):#line:365
                    O000O000OOOOOO0O0 =datetime .datetime .strptime (O000O000OOOOOO0O0 ,'%Y-%m-%d')#line:367
                elif re .fullmatch (r'\d{3}\-\d{2}-\d{2}',O000O000OOOOOO0O0 ):#line:368
                    O000O000OOOOOO0O0 =time .strptime (O000O000OOOOOO0O0 ,' %H:%M:%S')#line:370
                OO0O00OO00O00OOOO [OOOOOO00000OO0O00 ]=O000O000OOOOOO0O0 #line:371
    OOOO000OO0OOO00O0 =OOOO0OO0O00OOOO0O .filter (**OO0O00OO00O00OOOO ).order_by (O0OOO00OOO0OO0OOO )#line:373
    OOO0O0OO0000O0OO0 =model_admin .list_per_page #line:374
    if 'page_size'in request .POST :#line:375
        OOO00OOOOOOO00000 =int (request .POST .get ('page_size'))#line:376
        if OOO00OOOOOOO00000 !=0 :#line:377
            OOO0O0OO0000O0OO0 =OOO00OOOOOOO00000 #line:378
    OOOOOO00O00000OO0 =Paginator (OOOO000OO0OOO00O0 ,OOO0O0OO0000O0OO0 )#line:380
    if O00000O0O000OOO00 >OOOOOO00O00000OO0 .num_pages :#line:381
        O00000O0O000OOO00 =OOOOOO00O00000OO0 .num_pages #line:382
    OOOOO0000O00O0000 =OOOOOO00O00000OO0 .page (O00000O0O000OOO00 )#line:383
    OOO0OO0O000000OOO =OOOOO0000O00O0000 .object_list #line:384
    O0OO0000O0O000000 =[]#line:388
    for OO0O000OO0OOOOOOO in OOO0OO0O000000OOO :#line:389
        OOO000O0O00O0O00O ={}#line:390
        for OOOO00O000O000O00 in OO0O0000O0O000O00 :#line:391
            OOOOOO00000OO0O00 =OOOO00O000O000O00 +'_choices'#line:392
            if OOOOOO00000OO0O00 in O0OOO0OO00000OO00 :#line:393
                OO0OOOO0000O0O000 =getattr (OO0O000OO0OOOOOOO ,OOOO00O000O000O00 )#line:394
                OOO000OOO0000O0O0 =O0OOO0OO00000OO00 [OOOOOO00000OO0O00 ]#line:395
                if OO0OOOO0000O0O000 in OOO000OOO0000O0O0 :#line:396
                    OO0OOOO0000O0O000 =OOO000OOO0000O0O0 .get (OO0OOOO0000O0O000 )#line:397
            elif OOOO00O000O000O00 in O0OOO0OO00000OO00 :#line:398
                OO0OOOO0000O0O000 =getattr (OO0O000OO0OOOOOOO ,OOOO00O000O000O00 )#line:399
                OOO000OOO0000O0O0 =O0OOO0OO00000OO00 [OOOO00O000O000O00 ]#line:400
                if OO0OOOO0000O0O000 in OOO000OOO0000O0O0 :#line:401
                    OO0OOOO0000O0O000 =OOO000OOO0000O0O0 .get (OO0OOOO0000O0O000 )#line:402
            else :#line:403
                OO0OOOO0000O0O000 =getattr (OO0O000OO0OOOOOOO ,OOOO00O000O000O00 )#line:404
            if OO0000O0O00OOOOOO :#line:408
                OO0OOOO0000O0O000 =OO0000O0O00OOOOOO (OO0O000OO0OOOOOOO ,OOOO00O000O000O00 ,OO0OOOO0000O0O000 )#line:409
            if issubclass (OO0OOOO0000O0O000 .__class__ ,Model ):#line:410
                OO0OOOO0000O0O000 =str (OO0OOOO0000O0O000 )#line:411
            OOO000O0O00O0O00O [OOOO00O000O000O00 ]=OO0OOOO0000O0O000 #line:412
        for O0O0O0O0000O00OOO in OO0O0O0000OOO00OO :#line:414
            try :#line:415
                if hasattr (model_admin ,O0O0O0O0000O00OOO ):#line:416
                    OO0OOOO0000O0O000 =getattr (model_admin ,O0O0O0O0000O00OOO ).__call__ (OO0O000OO0OOOOOOO )#line:417
                else :#line:418
                    OO0OOOO0000O0O000 =getattr (model_admin .model ,O0O0O0O0000O00OOO ).__call__ (OO0O000OO0OOOOOOO )#line:419
                if OO0000O0O00OOOOOO :#line:420
                    OO0OOOO0000O0O000 =OO0000O0O00OOOOOO (OO0O000OO0OOOOOOO ,O0O0O0O0000O00OOO ,OO0OOOO0000O0O000 )#line:421
                OOO000O0O00O0O00O [O0O0O0O0000O00OOO ]=OO0OOOO0000O0O000 #line:422
            except Exception as OO00OOO000000OOO0 :#line:423
                raise Exception (OO00OOO000000OOO0 .args [0 ]+'\n call {} error. 调用自定义方法出错，请检查模型中的{}方法'.format (O0O0O0O0000O00OOO .__qualname__ ,O0O0O0O0000O00OOO .__qualname__ ))#line:425
        OOO000O0O00O0O00O ['_id']=getattr (OO0O000OO0OOOOOOO ,model_admin .model .id .field_name )#line:427
        O0OO0000O0O000000 .append (OOO000O0O00O0O00O )#line:428
    if O00000O0O000OOO00 <=1 :#line:436
        O00OO00OO0O00O0O0 =True #line:437
        if hasattr (model_admin ,'actions_show'):#line:438
            O00OO00OO0O00O0O0 =getattr (model_admin ,'actions_show')!=False #line:439
        O0O0000O000OO00O0 ['headers']=OO00000O0OO000000 #line:440
        O0O0000O000OO00O0 ['exts']={'showId':'id'in OO0O0000O0O000O00 ,'actions_show':O00OO00OO0O00O0O0 ,'showSearch':len (model_admin .search_fields )>0 ,'search_placeholder':search_placeholder (model_admin )}#line:446
        O0O0000O000OO00O0 ['custom_button']=get_custom_button (request ,model_admin )#line:450
    O0O0000O000OO00O0 ['rows']=O0OO0000O0O000000 #line:458
    O0O0000O000OO00O0 ['paginator']={'page_size':OOO0O0OO0000O0OO0 ,'count':OOOOOO00O00000OO0 .count ,'page_count':OOOOOO00O00000OO0 .num_pages }#line:464
    return write (O0O0000O000OO00O0 )#line:466
def process_active (request ):#line:469
    O0O0O0OOO0OOOOO0O =[reverse ('admin:index'),reverse ('admin:login'),reverse ('admin:logout')]#line:471
    OOOOO0O0OOO00OO0O =request .path #line:472
    O000OO0OO000O00OO =request .POST #line:474
    OOO0O000OOO0O000O =O000OO0OO000O00OO .get ('action')#line:475
    if OOO0O000OOO0O000O :#line:476
        return write (None ,'Simple Pro未激活，请联系客服人员进行激活！',False )#line:477
    elif OOOOO0O0OOO00OO0O not in O0O0O0OOO0OOOOO0O :#line:478
        return render (request ,'admin/active.html')#line:479
def process_lic (request ):#line:482
    O0O0OOO00000O000O =conf .get_device_id ()#line:484
    O00O0OOO00O000O0O =request .POST .get ('active_code')#line:485
    OOO000OOOO00OOOO0 =conf .get_server_url ()+'/active'#line:487
    OOOOO00OOOOO000OO =requests .post (OOO000OOOO00OOOO0 ,data ={'device_id':O0O0OOO00000O000O ,'active_code':O00O0OOO00O000O0O })#line:491
    if OOOOO00OOOOO000OO .status_code ==200 :#line:493
        O000OOO0OOOO0O000 =OOOOO00OOOOO000OO .json ()#line:494
        if O000OOO0OOOO0O000 .get ('state')is True :#line:495
            OOOOOOO00O0O0000O =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))#line:497
            OOOOO000OOOOOO0O0 =open (OOOOOOO00O0O0000O +'/simplepro/simpepro.lic','wb')#line:500
            O0O0OO000OO0O000O =base64 .b64decode (O000OOO0OOOO0O000 .get ('license'))#line:503
            OOO00OO00O0O0O000 =base64 .b64encode (bytes (O000OOO0OOOO0O000 .get ('private_key'),encoding ='utf8'))#line:504
            OOOOO000OOOOOO0O0 .write (struct .pack ('h',len (O0O0OO000OO0O000O )))#line:506
            OOOOO000OOOOOO0O0 .write (struct .pack ('h',len (OOO00OO00O0O0O000 )))#line:507
            OOOOO000OOOOOO0O0 .write (O0O0OO000OO0O000O )#line:508
            OOOOO000OOOOOO0O0 .write (OOO00OO00O0O0O000 )#line:509
            OOOOO000OOOOOO0O0 .close ()#line:510
            print ('写入激活文件，位置：{}'.format (OOOOOOO00O0O0000O +'/simpepro.lic'))#line:511
        return write_obj (O000OOO0OOOO0O000 )#line:513
    return write ({},'error',False )#line:514
def process_info (request ):#line:517
    return render (request ,'admin/active.html',{'page_size':OO0O0OO0OOO0OO0O0 (request ),'data':O0O0OOO0OOO0OO0O0 ()})#line:521
