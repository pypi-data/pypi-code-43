import json #line:1
from django .core .serializers .json import DjangoJSONEncoder #line:3
from django .db .models import ForeignKey #line:4
from django .http import HttpResponse #line:5
from django .utils .encoding import force_text #line:6
from django .utils .functional import Promise #line:7
import datetime #line:9
class LazyEncoder (DjangoJSONEncoder ):#line:12
    ""#line:15
    def default (self ,obj ):#line:17
        if isinstance (obj ,datetime .datetime ):#line:18
            return obj .strftime ("%Y-%m-%d %H:%M:%S")#line:19
        elif isinstance (obj ,datetime .date ):#line:20
            return obj .strftime ("%Y-%m-%d")#line:21
        elif isinstance (obj ,Promise ):#line:22
            return force_text (obj )#line:23
        return str (obj )#line:24
def get_model_fields (model ,O00OO00OO0O0O00O0 =None ):#line:28
    ""#line:34
    OO00O0O0O000O0000 =[]#line:35
    O000OOO0O000O000O =model ._meta .fields #line:36
    for O0OO000OOOO0OOO0O in O000OOO0O000O000O :#line:37
        OOOOO0OOOO0OOOOO0 =O0OO000OOOO0OOO0O .name #line:38
        if hasattr (O0OO000OOOO0OOO0O ,'verbose_name'):#line:39
            OOOOO0OOOO0OOOOO0 =getattr (O0OO000OOOO0OOO0O ,'verbose_name')#line:40
        if isinstance (OOOOO0OOOO0OOOOO0 ,Promise ):#line:42
            OOOOO0OOOO0OOOOO0 =str (OOOOO0OOOO0OOOOO0 )#line:43
        if O00OO00OO0O0O00O0 :#line:45
            OO00O0O0O000O0000 .append (('{}__{}'.format (O00OO00OO0O0O00O0 ,O0OO000OOOO0OOO0O .name ),OOOOO0OOOO0OOOOO0 ))#line:46
        else :#line:47
            OO00O0O0O000O0000 .append ((O0OO000OOOO0OOO0O .name ,OOOOO0OOOO0OOOOO0 ))#line:48
    return OO00O0O0O000O0000 #line:50
def find_field (fields ,name ):#line:53
    for O0OOO0000O0O0000O in fields :#line:54
        if name ==O0OOO0000O0O0000O [0 ]:#line:55
            return O0OOO0000O0O0000O [1 ]#line:56
    return False #line:57
MODEL_CACHE ={}#line:61
def get_model_info (model_admin ,request ):#line:64
    O00OOOOOOOOO00000 =str (model_admin )#line:68
    if O00OOOOOOOOO00000 in MODEL_CACHE :#line:69
        OOO0OOOOO0O0O0000 =MODEL_CACHE .get (O00OOOOOOOOO00000 )#line:70
        return OOO0OOOOO0O0O0000 .get ('values_fields'),OOO0OOOOO0O0O0000 .get ('fun_fields'),OOO0OOOOO0O0O0000 .get ('headers'),OOO0OOOOO0O0O0000 .get ('formatter'),OOO0OOOOO0O0O0000 .get ('choices')#line:72
    O0O0O0O00000O0O00 =get_model_fields (model_admin .model )#line:73
    O0OO0O0OOOOO0O000 =model_admin .get_list_display (request )#line:75
    O0OO0O0OOOOOOOOO0 =[]#line:76
    O0OOOOO00OO0O00OO =[]#line:77
    OOOOO000O0000OO0O =[]#line:78
    OOOO0O0OOO0000000 ={}#line:81
    if hasattr (model_admin ,'fields_options'):#line:82
        OOOO0O0OOO0000000 =getattr (model_admin ,'fields_options')#line:83
    for O0000OOO0OO0O0OO0 in O0OO0O0OOOOO0O000 :#line:85
        OOOOO0O0OO000O0OO =find_field (O0O0O0O00000O0O00 ,O0000OOO0OO0O0OO0 )#line:86
        if OOOOO0O0OO000O0OO :#line:87
            O0OOOOO00OO0O00OO .append (O0000OOO0OO0O0OO0 )#line:88
            OO0O0OOOOOO0OOOO0 ={'name':O0000OOO0OO0O0OO0 ,'label':OOOOO0O0OO000O0OO }#line:92
            if O0000OOO0OO0O0OO0 in OOOO0O0OOO0000000 :#line:93
                OO0O0OOOOOO0OOOO0 =dict (OO0O0OOOOOO0OOOO0 ,**OOOO0O0OOO0000000 .get (O0000OOO0OO0O0OO0 ))#line:94
            if 'sortable'not in OO0O0OOOOOO0OOOO0 :#line:96
                OO0O0OOOOOO0OOOO0 ['sortable']='custom'#line:98
            OOOOO000O0000OO0O .append (OO0O0OOOOOO0OOOO0 )#line:99
        else :#line:100
            O0OO0O0OOOOOOOOO0 .append (O0000OOO0OO0O0OO0 )#line:101
            OOOOO0O0OO000O0OO =O0000OOO0OO0O0OO0 #line:102
            if hasattr (model_admin ,O0000OOO0OO0O0OO0 ):#line:103
                O0O0O0O0O00O00OOO =getattr (model_admin ,O0000OOO0OO0O0OO0 ).__dict__ #line:104
            else :#line:105
                O0O0O0O0O00O00OOO =getattr (model_admin .model ,O0000OOO0OO0O0OO0 ).__dict__ #line:106
            if 'short_description'in O0O0O0O0O00O00OOO :#line:107
                OOOOO0O0OO000O0OO =O0O0O0O0O00O00OOO .get ('short_description')#line:108
            elif OOOOO0O0OO000O0OO =='__str__':#line:109
                OOOOO0O0OO000O0OO =model_admin .model ._meta .verbose_name_plural #line:110
            OO0O0OOOOOO0OOOO0 ={'name':O0000OOO0OO0O0OO0 ,'label':OOOOO0O0OO000O0OO }#line:114
            if O0000OOO0OO0O0OO0 in OOOO0O0OOO0000000 :#line:115
                OO0O0OOOOOO0OOOO0 =dict (OO0O0OOOOOO0OOOO0 ,**OOOO0O0OOO0000000 .get (O0000OOO0OO0O0OO0 ))#line:116
            OO0O0OOOOOO0OOOO0 ['sortable']=False #line:118
            OOOOO000O0000OO0O .append (OO0O0OOOOOO0OOOO0 )#line:119
    OO0O00O0OO0O0OOOO =None #line:121
    if hasattr (model_admin ,'formatter'):#line:122
        OO0O00O0OO0O0OOOO =getattr (model_admin ,'formatter')#line:123
    OO0O0000OO00O0OO0 =model_admin .model #line:126
    OO00OO00O0OO000O0 ={}#line:127
    for O000OOO00OOO0O00O in dir (OO0O0000OO00O0OO0 ):#line:128
        if O000OOO00OOO0O00O .endswith ('choices'):#line:129
            OO0O0OO0OO0O0OOO0 ={}#line:130
            OOOOOO000000OOOOO =getattr (OO0O0000OO00O0OO0 ,O000OOO00OOO0O00O )#line:131
            for O0000OOO0OO0O0OO0 in OOOOOO000000OOOOO :#line:132
                OO0O0OO0OO0O0OOO0 [O0000OOO0OO0O0OO0 [0 ]]=O0000OOO0OO0O0OO0 [1 ]#line:133
            OO00OO00O0OO000O0 [O000OOO00OOO0O00O ]=OO0O0OO0OO0O0OOO0 #line:134
    for O000OOO00OOO0O00O in OO0O0000OO00O0OO0 ._meta .fields :#line:135
        OO0O0OO0OO0O0OOO0 ={}#line:136
        if hasattr (O000OOO00OOO0O00O ,'choices'):#line:137
            if len (O000OOO00OOO0O00O .choices )>0 :#line:138
                for O0000OOO0OO0O0OO0 in O000OOO00OOO0O00O .choices :#line:139
                    OO0O0OO0OO0O0OOO0 [O0000OOO0OO0O0OO0 [0 ]]=O0000OOO0OO0O0OO0 [1 ]#line:140
                OO00OO00O0OO000O0 [O000OOO00OOO0O00O .name ]=OO0O0OO0OO0O0OOO0 #line:141
    MODEL_CACHE [O00OOOOOOOOO00000 ]={'values_fields':O0OOOOO00OO0O00OO ,'fun_fields':O0OO0O0OOOOOOOOO0 ,'headers':OOOOO000O0000OO0O ,'formatter':OO0O00O0OO0O0OOOO ,'choices':OO00OO00O0OO000O0 ,}#line:148
    return O0OOOOO00OO0O00OO ,O0OO0O0OOOOOOOOO0 ,OOOOO000O0000OO0O ,OO0O00O0OO0O0OOOO ,OO00OO00O0OO000O0 #line:149
def get_custom_button (request ,admin ):#line:152
    O0OO0OOO0O0O0OOO0 ={}#line:153
    O0O0O000OO000000O =admin .get_actions (request )#line:154
    OO000O00O0OOO0000 =admin .opts .app_label #line:159
    if O0O0O000OO000000O :#line:160
        OO0OO00O000O0O00O =0 #line:161
        for OO0O0O0O0OO0O0OO0 in O0O0O000OO000000O :#line:162
            OOO0O00OO000000O0 ={}#line:163
            O000O00O0OO000OO0 =O0O0O000OO000000O .get (OO0O0O0O0OO0O0OO0 )[0 ]#line:164
            for O0OOO0O0OO000OO00 ,O0O0OOOOO0OO00OO0 in O000O00O0OO000OO0 .__dict__ .items ():#line:165
                if O0OOO0O0OO000OO00 !='__len__'and O0OOO0O0OO000OO00 !='__wrapped__':#line:166
                    OOO0O00OO000000O0 [O0OOO0O0OO000OO00 ]=O0O0OOOOO0OO00OO0 #line:167
            OOO0O00OO000000O0 ['eid']=OO0OO00O000O0O00O #line:168
            OO0OO00O000O0O00O +=1 #line:169
            if OO0O0O0O0OO0O0OO0 =='export_admin_action':#line:170
                OOO0O00OO000000O0 ['label']='选中导出'#line:171
                OOO0O00OO000000O0 ['isExport']=True #line:172
                OOO0O00OO000000O0 ['icon']='el-icon-finished'#line:173
                O000O0OOO0OO0OOO0 =[]#line:174
                for OOO00OO00OOO00000 in enumerate (admin .get_export_formats ()):#line:175
                    O000O0OOO0OO0OOO0 .append ({'value':OOO00OO00OOO00000 [0 ],'label':OOO00OO00OOO00000 [1 ]().get_title ()})#line:179
                OOO0O00OO000000O0 ['formats']=O000O0OOO0OO0OOO0 #line:181
            else :#line:182
                OOO0O00OO000000O0 ['label']=O0O0O000OO000000O .get (OO0O0O0O0OO0O0OO0 )[2 ]#line:183
            if request .user .has_perm ('{}.{}'.format (OO000O00O0OOO0000 ,OO0O0O0O0OO0O0OO0 )):#line:186
                O0OO0OOO0O0O0OOO0 [OO0O0O0O0OO0O0OO0 ]=OOO0O00OO000000O0 #line:187
    if 'delete_selected'in O0OO0OOO0O0O0OOO0 :#line:188
        del O0OO0OOO0O0O0OOO0 ['delete_selected']#line:189
    return O0OO0OOO0O0O0OOO0 #line:190
def search_placeholder (cl ):#line:193
    OOO000O0OO0O0O000 =get_model_fields (cl .model )#line:195
    for O00O00O0O0OO00OOO in cl .model ._meta .fields :#line:197
        if isinstance (O00O00O0O0OO00OOO ,ForeignKey ):#line:198
            OOO000O0OO0O0O000 .extend (get_model_fields (O00O00O0O0OO00OOO .related_model ,O00O00O0O0OO00OOO .name ))#line:199
    O0O00O00000OOOOOO =[]#line:201
    for O00O00000O00000OO in cl .search_fields :#line:203
        for O00O00O0O0OO00OOO in OOO000O0OO0O0O000 :#line:204
            if O00O00O0O0OO00OOO [0 ]==O00O00000O00000OO :#line:205
                O0O00O00000OOOOOO .append (O00O00O0O0OO00OOO [1 ])#line:206
                break #line:207
    return ",".join (O0O00O00000OOOOOO )#line:209
def write (data ,OO00OOOO0O0OOOOO0 ='ok',OO00000000O0OO000 =True ):#line:212
    OOOO000000O0O0OOO ={'state':OO00000000O0OO000 ,'msg':OO00OOOO0O0OOOOO0 ,'data':data }#line:217
    return HttpResponse (json .dumps (OOOO000000O0O0OOO ,cls =LazyEncoder ),content_type ='application/json')#line:219
def write_obj (obj ):#line:222
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:223
def has_permission (request ,admin ,permission ):#line:226
    OOO0O00OO0O0O0O0O =get_permission_codename (permission ,admin .opts )#line:227
    OOO0000OOO0O0000O ='{}.{}'.format (admin .opts .app_label ,OOO0O00OO0O0O0O0O )#line:228
    return request .user .has_perm (OOO0000OOO0O0000O )#line:229
def get_permission_codename (action ,opts ):#line:232
    ""#line:235
    return '%s_%s'%(action ,opts .model_name )#line:236
from simpleui .templatetags import simpletags #line:239
from simpleui .templatetags .simpletags import get_config #line:240
def get_menus (request ,admin_site ):#line:243
    ""#line:249
    OOOOOO0O000O00OO0 ={'app_list':admin_site .get_app_list (request ),'request':request }#line:253
    def O0OOO00OOO0OOO0OO (key ):#line:255
        return request .user .has_perm (key )#line:256
    def _O0OO0O0O0O00O0O00 (key ):#line:258
        if key =='SIMPLEUI_CONFIG':#line:259
            _OO000O0000OOO0OO0 =get_config (key )#line:261
            if _OO000O0000OOO0OO0 and 'menus'in _OO000O0000OOO0OO0 :#line:262
                O0OO00OO0OO0OOOO0 =_OO000O0000OOO0OO0 .get ('menus')#line:263
                O000O00O0OO0OO000 =[]#line:264
                for O0000OO00OO0O0OOO in O0OO00OO0OO0OOOO0 :#line:266
                    if 'codename'not in O0000OO00OO0O0OOO :#line:267
                        O000O00O0OO0OO000 .append (O0000OO00OO0O0OOO )#line:268
                        continue #line:269
                    OOOOO0O0OO0OO00O0 =O0000OO00OO0O0OOO .get ('codename')#line:270
                    key ='{}.{}'.format (OOOOO0O0OO0OO00O0 ,OOOOO0O0OO0OO00O0 )#line:273
                    if O0OOO00OOO0OOO0OO (key ):#line:274
                        if 'models'in O0000OO00OO0O0OOO :#line:276
                            OOOOOO0OO00O0O000 =O0000OO00OO0O0OOO .get ('models')#line:277
                            OOOO0OO00O00O0000 =[]#line:278
                            for O00000O00O0O000OO in OOOOOO0OO00O0O000 :#line:279
                                if 'codename'in O00000O00O0O000OO :#line:280
                                    if O0OOO00OOO0OOO0OO ('{}.{}'.format (OOOOO0O0OO0OO00O0 ,O00000O00O0O000OO .get ('codename'))):#line:281
                                        OOOO0OO00O00O0000 .append (O00000O00O0O000OO )#line:282
                                else :#line:283
                                    OOOO0OO00O00O0000 .append (O00000O00O0O000OO )#line:284
                            O0000OO00OO0O0OOO ['models']=OOOO0OO00O00O0000 #line:285
                        O000O00O0OO0OO000 .append (O0000OO00OO0O0OOO )#line:287
                _OO000O0000OOO0OO0 ['menus']=O000O00O0OO0OO000 #line:288
        return _OO000O0000OOO0OO0 #line:290
    return simpletags .menus (OOOOOO0O000O00OO0 ,_get_config =_O0OO0O0O0O00O0O00 )#line:292
