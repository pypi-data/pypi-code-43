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
def get_model_fields (model ,O000OO000OOO00O0O =None ):#line:28
    ""#line:34
    OO0000000O0O0O0O0 =[]#line:35
    OOO0O00OOOOOO0OO0 =model ._meta .fields #line:36
    for O00O0O0000O000OO0 in OOO0O00OOOOOO0OO0 :#line:37
        O00O0O0O00000000O =O00O0O0000O000OO0 .name #line:38
        if hasattr (O00O0O0000O000OO0 ,'verbose_name'):#line:39
            O00O0O0O00000000O =getattr (O00O0O0000O000OO0 ,'verbose_name')#line:40
        if isinstance (O00O0O0O00000000O ,Promise ):#line:42
            O00O0O0O00000000O =str (O00O0O0O00000000O )#line:43
        if O000OO000OOO00O0O :#line:45
            OO0000000O0O0O0O0 .append (('{}__{}'.format (O000OO000OOO00O0O ,O00O0O0000O000OO0 .name ),O00O0O0O00000000O ))#line:46
        else :#line:47
            OO0000000O0O0O0O0 .append ((O00O0O0000O000OO0 .name ,O00O0O0O00000000O ))#line:48
    return OO0000000O0O0O0O0 #line:50
def find_field (fields ,name ):#line:53
    for OOOOOO000000OOOOO in fields :#line:54
        if name ==OOOOOO000000OOOOO [0 ]:#line:55
            return OOOOOO000000OOOOO [1 ]#line:56
    return False #line:57
MODEL_CACHE ={}#line:61
def get_model_info (model_admin ,request ):#line:64
    O0O00000000OOO00O =str (model_admin )#line:68
    if O0O00000000OOO00O in MODEL_CACHE :#line:69
        OO00O00000O0O00O0 =MODEL_CACHE .get (O0O00000000OOO00O )#line:70
        return OO00O00000O0O00O0 .get ('values_fields'),OO00O00000O0O00O0 .get ('fun_fields'),OO00O00000O0O00O0 .get ('headers'),OO00O00000O0O00O0 .get ('formatter'),OO00O00000O0O00O0 .get ('choices')#line:72
    OOO0OO000OOOOO0O0 =get_model_fields (model_admin .model )#line:73
    OO0OO0O0000OO000O =model_admin .get_list_display (request )#line:75
    OO000OOOOO0OOO000 =[]#line:76
    O0O0OO0O0O0000O0O =[]#line:77
    OOO0O000O0O00OOOO =[]#line:78
    OOO000000O00OO00O ={}#line:81
    if hasattr (model_admin ,'fields_options'):#line:82
        OOO000000O00OO00O =getattr (model_admin ,'fields_options')#line:83
    for OOOOOO000OOOO0OO0 in OO0OO0O0000OO000O :#line:85
        OO000O00OO0O0OOO0 =find_field (OOO0OO000OOOOO0O0 ,OOOOOO000OOOO0OO0 )#line:86
        if OO000O00OO0O0OOO0 :#line:87
            O0O0OO0O0O0000O0O .append (OOOOOO000OOOO0OO0 )#line:88
            O0O0OOOOOOO000O00 ={'name':OOOOOO000OOOO0OO0 ,'label':OO000O00OO0O0OOO0 }#line:92
            if OOOOOO000OOOO0OO0 in OOO000000O00OO00O :#line:93
                O0O0OOOOOOO000O00 =dict (O0O0OOOOOOO000O00 ,**OOO000000O00OO00O .get (OOOOOO000OOOO0OO0 ))#line:94
            if 'sortable'not in O0O0OOOOOOO000O00 :#line:96
                O0O0OOOOOOO000O00 ['sortable']='custom'#line:98
            OOO0O000O0O00OOOO .append (O0O0OOOOOOO000O00 )#line:99
        else :#line:100
            OO000OOOOO0OOO000 .append (OOOOOO000OOOO0OO0 )#line:101
            OO000O00OO0O0OOO0 =OOOOOO000OOOO0OO0 #line:102
            if hasattr (model_admin ,OOOOOO000OOOO0OO0 ):#line:103
                O00O0OO0OOOOOO0O0 =getattr (model_admin ,OOOOOO000OOOO0OO0 ).__dict__ #line:104
            else :#line:105
                O00O0OO0OOOOOO0O0 =getattr (model_admin .model ,OOOOOO000OOOO0OO0 ).__dict__ #line:106
            if 'short_description'in O00O0OO0OOOOOO0O0 :#line:107
                OO000O00OO0O0OOO0 =O00O0OO0OOOOOO0O0 .get ('short_description')#line:108
            elif OO000O00OO0O0OOO0 =='__str__':#line:109
                OO000O00OO0O0OOO0 =model_admin .model ._meta .verbose_name_plural #line:110
            O0O0OOOOOOO000O00 ={'name':OOOOOO000OOOO0OO0 ,'label':OO000O00OO0O0OOO0 }#line:114
            if OOOOOO000OOOO0OO0 in OOO000000O00OO00O :#line:115
                O0O0OOOOOOO000O00 =dict (O0O0OOOOOOO000O00 ,**OOO000000O00OO00O .get (OOOOOO000OOOO0OO0 ))#line:116
            O0O0OOOOOOO000O00 ['sortable']=False #line:118
            OOO0O000O0O00OOOO .append (O0O0OOOOOOO000O00 )#line:119
    O00O0O00O0O0OO0O0 =None #line:121
    if hasattr (model_admin ,'formatter'):#line:122
        O00O0O00O0O0OO0O0 =getattr (model_admin ,'formatter')#line:123
    OO00000OO0O0O0000 =model_admin .model #line:126
    O0OOO0O00O0O00OOO ={}#line:127
    for OOO00O000OOO0O0OO in dir (OO00000OO0O0O0000 ):#line:128
        if OOO00O000OOO0O0OO .endswith ('choices'):#line:129
            O0OOOO0000000000O ={}#line:130
            O00OO000OO00OO000 =getattr (OO00000OO0O0O0000 ,OOO00O000OOO0O0OO )#line:131
            for OOOOOO000OOOO0OO0 in O00OO000OO00OO000 :#line:132
                O0OOOO0000000000O [OOOOOO000OOOO0OO0 [0 ]]=OOOOOO000OOOO0OO0 [1 ]#line:133
            O0OOO0O00O0O00OOO [OOO00O000OOO0O0OO ]=O0OOOO0000000000O #line:134
    for OOO00O000OOO0O0OO in OO00000OO0O0O0000 ._meta .fields :#line:135
        O0OOOO0000000000O ={}#line:136
        if hasattr (OOO00O000OOO0O0OO ,'choices'):#line:137
            if len (OOO00O000OOO0O0OO .choices )>0 :#line:138
                for OOOOOO000OOOO0OO0 in OOO00O000OOO0O0OO .choices :#line:139
                    O0OOOO0000000000O [OOOOOO000OOOO0OO0 [0 ]]=OOOOOO000OOOO0OO0 [1 ]#line:140
                O0OOO0O00O0O00OOO [OOO00O000OOO0O0OO .name ]=O0OOOO0000000000O #line:141
    MODEL_CACHE [O0O00000000OOO00O ]={'values_fields':O0O0OO0O0O0000O0O ,'fun_fields':OO000OOOOO0OOO000 ,'headers':OOO0O000O0O00OOOO ,'formatter':O00O0O00O0O0OO0O0 ,'choices':O0OOO0O00O0O00OOO ,}#line:148
    return O0O0OO0O0O0000O0O ,OO000OOOOO0OOO000 ,OOO0O000O0O00OOOO ,O00O0O00O0O0OO0O0 ,O0OOO0O00O0O00OOO #line:149
def get_custom_button (request ,admin ):#line:152
    O00O0O0OOO000000O ={}#line:153
    O0O00OO0O0O0OO000 =admin .get_actions (request )#line:154
    OO00OOOO0O0OOOO00 =admin .opts .app_label #line:159
    if O0O00OO0O0O0OO000 :#line:160
        OOOOOOOO00O0OOOO0 =0 #line:161
        for OOO0000OOO0OOO00O in O0O00OO0O0O0OO000 :#line:162
            OO00O00O0O0O00O00 ={}#line:163
            O00OOO0O00O0OO000 =O0O00OO0O0O0OO000 .get (OOO0000OOO0OOO00O )[0 ]#line:164
            for OO000000OO0OO00OO ,OO00O00OOOO0OOOO0 in O00OOO0O00O0OO000 .__dict__ .items ():#line:165
                if OO000000OO0OO00OO !='__len__'and OO000000OO0OO00OO !='__wrapped__':#line:166
                    OO00O00O0O0O00O00 [OO000000OO0OO00OO ]=OO00O00OOOO0OOOO0 #line:167
            OO00O00O0O0O00O00 ['eid']=OOOOOOOO00O0OOOO0 #line:168
            OOOOOOOO00O0OOOO0 +=1 #line:169
            if OOO0000OOO0OOO00O =='export_admin_action':#line:170
                OO00O00O0O0O00O00 ['label']='选中导出'#line:171
                OO00O00O0O0O00O00 ['isExport']=True #line:172
                OO00O00O0O0O00O00 ['icon']='el-icon-finished'#line:173
                OOOO00O00O0000O00 =[]#line:174
                for O0O0O0OO0O0O0O00O in enumerate (admin .get_export_formats ()):#line:175
                    OOOO00O00O0000O00 .append ({'value':O0O0O0OO0O0O0O00O [0 ],'label':O0O0O0OO0O0O0O00O [1 ]().get_title ()})#line:179
                OO00O00O0O0O00O00 ['formats']=OOOO00O00O0000O00 #line:181
            else :#line:182
                OO00O00O0O0O00O00 ['label']=O0O00OO0O0O0OO000 .get (OOO0000OOO0OOO00O )[2 ]#line:183
            if request .user .has_perm ('{}.{}'.format (OO00OOOO0O0OOOO00 ,OOO0000OOO0OOO00O )):#line:186
                O00O0O0OOO000000O [OOO0000OOO0OOO00O ]=OO00O00O0O0O00O00 #line:187
    if 'delete_selected'in O00O0O0OOO000000O :#line:188
        del O00O0O0OOO000000O ['delete_selected']#line:189
    return O00O0O0OOO000000O #line:190
def search_placeholder (cl ):#line:193
    OOO0O0OO0OO00O0OO =get_model_fields (cl .model )#line:195
    for O0000OOOOOOOOO000 in cl .model ._meta .fields :#line:197
        if isinstance (O0000OOOOOOOOO000 ,ForeignKey ):#line:198
            OOO0O0OO0OO00O0OO .extend (get_model_fields (O0000OOOOOOOOO000 .related_model ,O0000OOOOOOOOO000 .name ))#line:199
    OO0000O00OO00OO0O =[]#line:201
    for OOOOOO00O0OO0OO00 in cl .search_fields :#line:203
        for O0000OOOOOOOOO000 in OOO0O0OO0OO00O0OO :#line:204
            if O0000OOOOOOOOO000 [0 ]==OOOOOO00O0OO0OO00 :#line:205
                OO0000O00OO00OO0O .append (O0000OOOOOOOOO000 [1 ])#line:206
                break #line:207
    return ",".join (OO0000O00OO00OO0O )#line:209
def write (data ,OOOO0O0000O00OOOO ='ok',O0O0O0OO0O0OO0OOO =True ):#line:212
    O0O0OO0000O0O0O00 ={'state':O0O0O0OO0O0OO0OOO ,'msg':OOOO0O0000O00OOOO ,'data':data }#line:217
    return HttpResponse (json .dumps (O0O0OO0000O0O0O00 ,cls =LazyEncoder ),content_type ='application/json')#line:219
def write_obj (obj ):#line:222
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:223
def has_permission (request ,admin ,permission ):#line:226
    O0000O0O0OO0000O0 =get_permission_codename (permission ,admin .opts )#line:227
    O0O00OO000OOO000O ='{}.{}'.format (admin .opts .app_label ,O0000O0O0OO0000O0 )#line:228
    return request .user .has_perm (O0O00OO000OOO000O )#line:229
def get_permission_codename (action ,opts ):#line:232
    ""#line:235
    return '%s_%s'%(action ,opts .model_name )#line:236
from simpleui .templatetags import simpletags #line:239
from simpleui .templatetags .simpletags import get_config #line:240
def get_menus (request ,admin_site ):#line:243
    ""#line:249
    O0O0OOOOOO0OO0OOO ={'app_list':admin_site .get_app_list (request ),'request':request }#line:253
    def OO00O0OO000O0OOO0 (key ):#line:255
        return request .user .has_perm (key )#line:256
    def _OOOO0O000000000OO (key ):#line:258
        if key =='SIMPLEUI_CONFIG':#line:259
            _OOO0O00OOOO00O0O0 =get_config (key )#line:261
            if _OOO0O00OOOO00O0O0 and 'menus'in _OOO0O00OOOO00O0O0 :#line:262
                O0000OO0OOOO0O0OO =_OOO0O00OOOO00O0O0 .get ('menus')#line:263
                OOOO0000O0O0OO0OO =[]#line:264
                for O00000OOO0OOO0O00 in O0000OO0OOOO0O0OO :#line:266
                    if 'codename'not in O00000OOO0OOO0O00 :#line:267
                        OOOO0000O0O0OO0OO .append (O00000OOO0OOO0O00 )#line:268
                        continue #line:269
                    OO00OOOOO0O0O00O0 =O00000OOO0OOO0O00 .get ('codename')#line:270
                    key ='{}.{}'.format (OO00OOOOO0O0O00O0 ,OO00OOOOO0O0O00O0 )#line:273
                    if OO00O0OO000O0OOO0 (key ):#line:274
                        if 'models'in O00000OOO0OOO0O00 :#line:276
                            O00OOO0OO0O0O0O00 =O00000OOO0OOO0O00 .get ('models')#line:277
                            O0000000O0OOOO00O =[]#line:278
                            for O0O000O00O00OOOO0 in O00OOO0OO0O0O0O00 :#line:279
                                if 'codename'in O0O000O00O00OOOO0 :#line:280
                                    if OO00O0OO000O0OOO0 ('{}.{}'.format (OO00OOOOO0O0O00O0 ,O0O000O00O00OOOO0 .get ('codename'))):#line:281
                                        O0000000O0OOOO00O .append (O0O000O00O00OOOO0 )#line:282
                                else :#line:283
                                    O0000000O0OOOO00O .append (O0O000O00O00OOOO0 )#line:284
                            O00000OOO0OOO0O00 ['models']=O0000000O0OOOO00O #line:285
                        OOOO0000O0O0OO0OO .append (O00000OOO0OOO0O00 )#line:287
                _OOO0O00OOOO00O0O0 ['menus']=OOOO0000O0O0OO0OO #line:288
        return _OOO0O00OOOO00O0O0 #line:290
    return simpletags .menus (O0O0OOOOOO0OO0OOO ,_get_config =_OOOO0O000000000OO )#line:292
