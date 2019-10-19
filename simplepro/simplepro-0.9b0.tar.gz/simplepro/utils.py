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
def get_model_fields (model ,O0000OOO0O000O000 =None ):#line:28
    ""#line:34
    OOO00000O0O000O00 =[]#line:35
    OOO0OO0O00000OO0O =model ._meta .fields #line:36
    for OO0O00OO0O00OOOOO in OOO0OO0O00000OO0O :#line:37
        O0000OOO00O0O0OOO =OO0O00OO0O00OOOOO .name #line:38
        if hasattr (OO0O00OO0O00OOOOO ,'verbose_name'):#line:39
            O0000OOO00O0O0OOO =getattr (OO0O00OO0O00OOOOO ,'verbose_name')#line:40
        if isinstance (O0000OOO00O0O0OOO ,Promise ):#line:42
            O0000OOO00O0O0OOO =str (O0000OOO00O0O0OOO )#line:43
        if O0000OOO0O000O000 :#line:45
            OOO00000O0O000O00 .append (('{}__{}'.format (O0000OOO0O000O000 ,OO0O00OO0O00OOOOO .name ),O0000OOO00O0O0OOO ))#line:46
        else :#line:47
            OOO00000O0O000O00 .append ((OO0O00OO0O00OOOOO .name ,O0000OOO00O0O0OOO ))#line:48
    return OOO00000O0O000O00 #line:50
def find_field (fields ,name ):#line:53
    for O0000OO0OO0OO000O in fields :#line:54
        if name ==O0000OO0OO0OO000O [0 ]:#line:55
            return O0000OO0OO0OO000O [1 ]#line:56
    return False #line:57
MODEL_CACHE ={}#line:61
def get_model_info (model_admin ,request ):#line:64
    OO0OO0OOOO0OO0000 =str (model_admin )#line:68
    if OO0OO0OOOO0OO0000 in MODEL_CACHE :#line:69
        OO000OO00O0OO0000 =MODEL_CACHE .get (OO0OO0OOOO0OO0000 )#line:70
        return OO000OO00O0OO0000 .get ('values_fields'),OO000OO00O0OO0000 .get ('fun_fields'),OO000OO00O0OO0000 .get ('headers'),OO000OO00O0OO0000 .get ('formatter'),OO000OO00O0OO0000 .get ('choices')#line:72
    OOO0OO000000O0OOO =get_model_fields (model_admin .model )#line:73
    O00OOO00000O00000 =model_admin .get_list_display (request )#line:75
    O0O0OO00000O0OOO0 =[]#line:76
    O0OO0O0O0O0O0OO0O =[]#line:77
    OOOOO00OOOOO0OOOO =[]#line:78
    OO00OO00O0O00O000 ={}#line:81
    if hasattr (model_admin ,'fields_options'):#line:82
        OO00OO00O0O00O000 =getattr (model_admin ,'fields_options')#line:83
    for O00O0O0OOOOO00O0O in O00OOO00000O00000 :#line:85
        O0O0OOOOOO00O0OO0 =find_field (OOO0OO000000O0OOO ,O00O0O0OOOOO00O0O )#line:86
        if O0O0OOOOOO00O0OO0 :#line:87
            O0OO0O0O0O0O0OO0O .append (O00O0O0OOOOO00O0O )#line:88
            OO00O0O0OOO0O0O0O ={'name':O00O0O0OOOOO00O0O ,'label':O0O0OOOOOO00O0OO0 }#line:92
            if O00O0O0OOOOO00O0O in OO00OO00O0O00O000 :#line:93
                OO00O0O0OOO0O0O0O =dict (OO00O0O0OOO0O0O0O ,**OO00OO00O0O00O000 .get (O00O0O0OOOOO00O0O ))#line:94
            if 'sortable'not in OO00O0O0OOO0O0O0O :#line:96
                OO00O0O0OOO0O0O0O ['sortable']='custom'#line:98
            OOOOO00OOOOO0OOOO .append (OO00O0O0OOO0O0O0O )#line:99
        else :#line:100
            O0O0OO00000O0OOO0 .append (O00O0O0OOOOO00O0O )#line:101
            O0O0OOOOOO00O0OO0 =O00O0O0OOOOO00O0O #line:102
            if hasattr (model_admin ,O00O0O0OOOOO00O0O ):#line:103
                O0O00OO00OOO0000O =getattr (model_admin ,O00O0O0OOOOO00O0O ).__dict__ #line:104
            else :#line:105
                O0O00OO00OOO0000O =getattr (model_admin .model ,O00O0O0OOOOO00O0O ).__dict__ #line:106
            if 'short_description'in O0O00OO00OOO0000O :#line:107
                O0O0OOOOOO00O0OO0 =O0O00OO00OOO0000O .get ('short_description')#line:108
            elif O0O0OOOOOO00O0OO0 =='__str__':#line:109
                O0O0OOOOOO00O0OO0 =model_admin .model ._meta .verbose_name_plural #line:110
            OO00O0O0OOO0O0O0O ={'name':O00O0O0OOOOO00O0O ,'label':O0O0OOOOOO00O0OO0 }#line:114
            if O00O0O0OOOOO00O0O in OO00OO00O0O00O000 :#line:115
                OO00O0O0OOO0O0O0O =dict (OO00O0O0OOO0O0O0O ,**OO00OO00O0O00O000 .get (O00O0O0OOOOO00O0O ))#line:116
            OO00O0O0OOO0O0O0O ['sortable']=False #line:118
            OOOOO00OOOOO0OOOO .append (OO00O0O0OOO0O0O0O )#line:119
    O0OOOO0OO00O0O00O =None #line:121
    if hasattr (model_admin ,'formatter'):#line:122
        O0OOOO0OO00O0O00O =getattr (model_admin ,'formatter')#line:123
    OO00OOO000O0000O0 =model_admin .model #line:126
    OOOO000O0O0O0OOO0 ={}#line:127
    for OOOO00OO0OOOO0O0O in dir (OO00OOO000O0000O0 ):#line:128
        if OOOO00OO0OOOO0O0O .endswith ('choices'):#line:129
            O00OOO000000OO0O0 ={}#line:130
            O00O0OO000O0O00OO =getattr (OO00OOO000O0000O0 ,OOOO00OO0OOOO0O0O )#line:131
            for O00O0O0OOOOO00O0O in O00O0OO000O0O00OO :#line:132
                O00OOO000000OO0O0 [O00O0O0OOOOO00O0O [0 ]]=O00O0O0OOOOO00O0O [1 ]#line:133
            OOOO000O0O0O0OOO0 [OOOO00OO0OOOO0O0O ]=O00OOO000000OO0O0 #line:134
    for OOOO00OO0OOOO0O0O in OO00OOO000O0000O0 ._meta .fields :#line:135
        O00OOO000000OO0O0 ={}#line:136
        if hasattr (OOOO00OO0OOOO0O0O ,'choices'):#line:137
            if len (OOOO00OO0OOOO0O0O .choices )>0 :#line:138
                for O00O0O0OOOOO00O0O in OOOO00OO0OOOO0O0O .choices :#line:139
                    O00OOO000000OO0O0 [O00O0O0OOOOO00O0O [0 ]]=O00O0O0OOOOO00O0O [1 ]#line:140
                OOOO000O0O0O0OOO0 [OOOO00OO0OOOO0O0O .name ]=O00OOO000000OO0O0 #line:141
    MODEL_CACHE [OO0OO0OOOO0OO0000 ]={'values_fields':O0OO0O0O0O0O0OO0O ,'fun_fields':O0O0OO00000O0OOO0 ,'headers':OOOOO00OOOOO0OOOO ,'formatter':O0OOOO0OO00O0O00O ,'choices':OOOO000O0O0O0OOO0 ,}#line:148
    return O0OO0O0O0O0O0OO0O ,O0O0OO00000O0OOO0 ,OOOOO00OOOOO0OOOO ,O0OOOO0OO00O0O00O ,OOOO000O0O0O0OOO0 #line:149
def get_custom_button (request ,admin ):#line:152
    O0O00O0OOO0O0OO0O ={}#line:153
    OOOO0OO00O0O0OOO0 =admin .get_actions (request )#line:154
    OO000O0O00O000O0O =admin .opts .app_label #line:159
    if OOOO0OO00O0O0OOO0 :#line:160
        O000OO000O000OOOO =0 #line:161
        for O0000O0O000O000OO in OOOO0OO00O0O0OOO0 :#line:162
            O0OOOOO000OOOO0OO ={}#line:163
            O00OOO000OOO000OO =OOOO0OO00O0O0OOO0 .get (O0000O0O000O000OO )[0 ]#line:164
            for OO00OO00OO00O0OO0 ,OO0O00OO000O0OOOO in O00OOO000OOO000OO .__dict__ .items ():#line:165
                if OO00OO00OO00O0OO0 !='__len__'and OO00OO00OO00O0OO0 !='__wrapped__':#line:166
                    O0OOOOO000OOOO0OO [OO00OO00OO00O0OO0 ]=OO0O00OO000O0OOOO #line:167
            O0OOOOO000OOOO0OO ['eid']=O000OO000O000OOOO #line:168
            O000OO000O000OOOO +=1 #line:169
            if O0000O0O000O000OO =='export_admin_action':#line:170
                O0OOOOO000OOOO0OO ['label']='选中导出'#line:171
                O0OOOOO000OOOO0OO ['isExport']=True #line:172
                O0OOOOO000OOOO0OO ['icon']='el-icon-finished'#line:173
                O0OOO0000O0OO0O0O =[]#line:174
                for OOO000O0O0O0OO0OO in enumerate (admin .get_export_formats ()):#line:175
                    O0OOO0000O0OO0O0O .append ({'value':OOO000O0O0O0OO0OO [0 ],'label':OOO000O0O0O0OO0OO [1 ]().get_title ()})#line:179
                O0OOOOO000OOOO0OO ['formats']=O0OOO0000O0OO0O0O #line:181
            else :#line:182
                O0OOOOO000OOOO0OO ['label']=OOOO0OO00O0O0OOO0 .get (O0000O0O000O000OO )[2 ]#line:183
            if request .user .has_perm ('{}.{}'.format (OO000O0O00O000O0O ,O0000O0O000O000OO )):#line:186
                O0O00O0OOO0O0OO0O [O0000O0O000O000OO ]=O0OOOOO000OOOO0OO #line:187
    if 'delete_selected'in O0O00O0OOO0O0OO0O :#line:188
        del O0O00O0OOO0O0OO0O ['delete_selected']#line:189
    return O0O00O0OOO0O0OO0O #line:190
def search_placeholder (cl ):#line:193
    O0O00000O00O0OO00 =get_model_fields (cl .model )#line:195
    for OO00O0OOO00OO0000 in cl .model ._meta .fields :#line:197
        if isinstance (OO00O0OOO00OO0000 ,ForeignKey ):#line:198
            O0O00000O00O0OO00 .extend (get_model_fields (OO00O0OOO00OO0000 .related_model ,OO00O0OOO00OO0000 .name ))#line:199
    OO0O000O000OO0OO0 =[]#line:201
    for O00O0OOOO00OOOOO0 in cl .search_fields :#line:203
        for OO00O0OOO00OO0000 in O0O00000O00O0OO00 :#line:204
            if OO00O0OOO00OO0000 [0 ]==O00O0OOOO00OOOOO0 :#line:205
                OO0O000O000OO0OO0 .append (OO00O0OOO00OO0000 [1 ])#line:206
                break #line:207
    return ",".join (OO0O000O000OO0OO0 )#line:209
def write (data ,O0O0O0OOOO000O0O0 ='ok',O00O00O00OO00O000 =True ):#line:212
    O0O00OOO0O0O0O000 ={'state':O00O00O00OO00O000 ,'msg':O0O0O0OOOO000O0O0 ,'data':data }#line:217
    return HttpResponse (json .dumps (O0O00OOO0O0O0O000 ,cls =LazyEncoder ),content_type ='application/json')#line:219
def write_obj (obj ):#line:222
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:223
def has_permission (request ,admin ,permission ):#line:226
    OO000O00O0OO0OOOO =get_permission_codename (permission ,admin .opts )#line:227
    O000000O000O0O0OO ='{}.{}'.format (admin .opts .app_label ,OO000O00O0OO0OOOO )#line:228
    return request .user .has_perm (O000000O000O0O0OO )#line:229
def get_permission_codename (action ,opts ):#line:232
    ""#line:235
    return '%s_%s'%(action ,opts .model_name )#line:236
from simpleui .templatetags import simpletags #line:239
from simpleui .templatetags .simpletags import get_config #line:240
def get_menus (request ,admin_site ):#line:243
    ""#line:249
    O0O00000O0000000O ={'app_list':admin_site .get_app_list (request ),'request':request }#line:253
    def OO00OO0O00O0O0OO0 (key ):#line:255
        return request .user .has_perm (key )#line:256
    def _O000OOO000OOOO0OO (key ):#line:258
        if key =='SIMPLEUI_CONFIG':#line:259
            _O000OOO00O0O000O0 =get_config (key )#line:261
            if 'menus'in _O000OOO00O0O000O0 :#line:262
                OO000O0OOOOO0OOOO =_O000OOO00O0O000O0 .get ('menus')#line:263
                OOOOO000O0OOO0O00 =[]#line:264
                for O00O0O0O00O0O00OO in OO000O0OOOOO0OOOO :#line:266
                    if 'codename'not in O00O0O0O00O0O00OO :#line:267
                        OOOOO000O0OOO0O00 .append (O00O0O0O00O0O00OO )#line:268
                        continue #line:269
                    OOOOOO00O000O0OO0 =O00O0O0O00O0O00OO .get ('codename')#line:270
                    key ='{}.{}'.format (OOOOOO00O000O0OO0 ,OOOOOO00O000O0OO0 )#line:273
                    if OO00OO0O00O0O0OO0 (key ):#line:274
                        if 'models'in O00O0O0O00O0O00OO :#line:276
                            OO0O000000O0OOO0O =O00O0O0O00O0O00OO .get ('models')#line:277
                            O0O00O0O00OOOO000 =[]#line:278
                            for O0OOOO0OO0OO00O0O in OO0O000000O0OOO0O :#line:279
                                if 'codename'in O0OOOO0OO0OO00O0O :#line:280
                                    if OO00OO0O00O0O0OO0 ('{}.{}'.format (OOOOOO00O000O0OO0 ,O0OOOO0OO0OO00O0O .get ('codename'))):#line:281
                                        O0O00O0O00OOOO000 .append (O0OOOO0OO0OO00O0O )#line:282
                                else :#line:283
                                    O0O00O0O00OOOO000 .append (O0OOOO0OO0OO00O0O )#line:284
                            O00O0O0O00O0O00OO ['models']=O0O00O0O00OOOO000 #line:285
                        OOOOO000O0OOO0O00 .append (O00O0O0O00O0O00OO )#line:287
                _O000OOO00O0O000O0 ['menus']=OOOOO000O0OOO0O00 #line:288
        return _O000OOO00O0O000O0 #line:290
    return simpletags .menus (O0O00000O0000000O ,_get_config =_O000OOO000OOOO0OO )#line:292
