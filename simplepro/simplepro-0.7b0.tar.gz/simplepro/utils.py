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
        return super (LazyEncoder ,self ).default (obj )#line:24
def get_model_fields (model ,O00OO00OO00OOO000 =None ):#line:27
    ""#line:33
    O0OOOO00OO0O0O00O =[]#line:34
    O00OO0OOO0O000000 =model ._meta .fields #line:35
    for OO0O00OO0OOOO0OOO in O00OO0OOO0O000000 :#line:36
        O0OOOO0000O00OOOO =OO0O00OO0OOOO0OOO .name #line:37
        if hasattr (OO0O00OO0OOOO0OOO ,'verbose_name'):#line:38
            O0OOOO0000O00OOOO =getattr (OO0O00OO0OOOO0OOO ,'verbose_name')#line:39
        if isinstance (O0OOOO0000O00OOOO ,Promise ):#line:41
            O0OOOO0000O00OOOO =str (O0OOOO0000O00OOOO )#line:42
        if O00OO00OO00OOO000 :#line:44
            O0OOOO00OO0O0O00O .append (('{}__{}'.format (O00OO00OO00OOO000 ,OO0O00OO0OOOO0OOO .name ),O0OOOO0000O00OOOO ))#line:45
        else :#line:46
            O0OOOO00OO0O0O00O .append ((OO0O00OO0OOOO0OOO .name ,O0OOOO0000O00OOOO ))#line:47
    return O0OOOO00OO0O0O00O #line:49
def find_field (fields ,name ):#line:52
    for O0O00O0OOOO0O0OO0 in fields :#line:53
        if name ==O0O00O0OOOO0O0OO0 [0 ]:#line:54
            return O0O00O0OOOO0O0OO0 [1 ]#line:55
    return False #line:56
MODEL_CACHE ={}#line:60
def get_model_info (model_admin ,request ):#line:63
    OOO0OO0O0OOO0O00O =str (model_admin )#line:67
    if OOO0OO0O0OOO0O00O in MODEL_CACHE :#line:68
        OOOOOO0OO0OO0O0O0 =MODEL_CACHE .get (OOO0OO0O0OOO0O00O )#line:69
        return OOOOOO0OO0OO0O0O0 .get ('values_fields'),OOOOOO0OO0OO0O0O0 .get ('fun_fields'),OOOOOO0OO0OO0O0O0 .get ('headers'),OOOOOO0OO0OO0O0O0 .get ('formatter'),OOOOOO0OO0OO0O0O0 .get ('choices')#line:71
    OOO00OO0O0O0OO00O =get_model_fields (model_admin .model )#line:72
    OO0OO000OOO00OOO0 =model_admin .get_list_display (request )#line:74
    O0O0O0000OOOO000O =[]#line:75
    O0O0OOOOO00O0O0O0 =[]#line:76
    OO0O0O000O0O00OOO =[]#line:77
    O0OOOO0OOOOO000OO ={}#line:80
    if hasattr (model_admin ,'fields_options'):#line:81
        O0OOOO0OOOOO000OO =getattr (model_admin ,'fields_options')#line:82
    for OO0O0O000O0OOO00O in OO0OO000OOO00OOO0 :#line:84
        O0O0OOO000OOOO0OO =find_field (OOO00OO0O0O0OO00O ,OO0O0O000O0OOO00O )#line:85
        if O0O0OOO000OOOO0OO :#line:86
            O0O0OOOOO00O0O0O0 .append (OO0O0O000O0OOO00O )#line:87
            O0O0OOO0000OOO00O ={'name':OO0O0O000O0OOO00O ,'label':O0O0OOO000OOOO0OO }#line:91
            if OO0O0O000O0OOO00O in O0OOOO0OOOOO000OO :#line:92
                O0O0OOO0000OOO00O =dict (O0O0OOO0000OOO00O ,**O0OOOO0OOOOO000OO .get (OO0O0O000O0OOO00O ))#line:93
            if 'sortable'not in O0O0OOO0000OOO00O :#line:95
                O0O0OOO0000OOO00O ['sortable']='custom'#line:97
            OO0O0O000O0O00OOO .append (O0O0OOO0000OOO00O )#line:98
        else :#line:99
            O0O0O0000OOOO000O .append (OO0O0O000O0OOO00O )#line:100
            O0O0OOO000OOOO0OO =OO0O0O000O0OOO00O #line:101
            if hasattr (model_admin ,OO0O0O000O0OOO00O ):#line:102
                OO0O0O00O0O0O0OO0 =getattr (model_admin ,OO0O0O000O0OOO00O ).__dict__ #line:103
            else :#line:104
                OO0O0O00O0O0O0OO0 =getattr (model_admin .model ,OO0O0O000O0OOO00O ).__dict__ #line:105
            if 'short_description'in OO0O0O00O0O0O0OO0 :#line:106
                O0O0OOO000OOOO0OO =OO0O0O00O0O0O0OO0 .get ('short_description')#line:107
            elif O0O0OOO000OOOO0OO =='__str__':#line:108
                O0O0OOO000OOOO0OO =model_admin .model ._meta .verbose_name_plural #line:109
            O0O0OOO0000OOO00O ={'name':OO0O0O000O0OOO00O ,'label':O0O0OOO000OOOO0OO }#line:113
            if OO0O0O000O0OOO00O in O0OOOO0OOOOO000OO :#line:114
                O0O0OOO0000OOO00O =dict (O0O0OOO0000OOO00O ,**O0OOOO0OOOOO000OO .get (OO0O0O000O0OOO00O ))#line:115
            O0O0OOO0000OOO00O ['sortable']=False #line:117
            OO0O0O000O0O00OOO .append (O0O0OOO0000OOO00O )#line:118
    OOOOOOOO0O0000O0O =None #line:120
    if hasattr (model_admin ,'formatter'):#line:121
        OOOOOOOO0O0000O0O =getattr (model_admin ,'formatter')#line:122
    O000OOO0000OOO0OO =model_admin .model #line:125
    O0OOO00OOOOO000O0 ={}#line:126
    for OO00OO000OO0O0000 in dir (O000OOO0000OOO0OO ):#line:127
        if OO00OO000OO0O0000 .endswith ('choices'):#line:128
            O00O0000000O00O00 ={}#line:129
            O0OO0O0O0O000OO0O =getattr (O000OOO0000OOO0OO ,OO00OO000OO0O0000 )#line:130
            for OO0O0O000O0OOO00O in O0OO0O0O0O000OO0O :#line:131
                O00O0000000O00O00 [OO0O0O000O0OOO00O [0 ]]=OO0O0O000O0OOO00O [1 ]#line:132
            O0OOO00OOOOO000O0 [OO00OO000OO0O0000 ]=O00O0000000O00O00 #line:133
    for OO00OO000OO0O0000 in O000OOO0000OOO0OO ._meta .fields :#line:134
        O00O0000000O00O00 ={}#line:135
        if hasattr (OO00OO000OO0O0000 ,'choices'):#line:136
            if len (OO00OO000OO0O0000 .choices )>0 :#line:137
                for OO0O0O000O0OOO00O in OO00OO000OO0O0000 .choices :#line:138
                    O00O0000000O00O00 [OO0O0O000O0OOO00O [0 ]]=OO0O0O000O0OOO00O [1 ]#line:139
                O0OOO00OOOOO000O0 [OO00OO000OO0O0000 .name ]=O00O0000000O00O00 #line:140
    MODEL_CACHE [OOO0OO0O0OOO0O00O ]={'values_fields':O0O0OOOOO00O0O0O0 ,'fun_fields':O0O0O0000OOOO000O ,'headers':OO0O0O000O0O00OOO ,'formatter':OOOOOOOO0O0000O0O ,'choices':O0OOO00OOOOO000O0 ,}#line:147
    return O0O0OOOOO00O0O0O0 ,O0O0O0000OOOO000O ,OO0O0O000O0O00OOO ,OOOOOOOO0O0000O0O ,O0OOO00OOOOO000O0 #line:148
def get_custom_button (request ,admin ):#line:151
    OOOOO00000O00O0OO ={}#line:152
    OOO0OOO0OOOOO0O00 =admin .get_actions (request )#line:153
    OO0OOOO0000O0O0O0 =admin .opts .app_label #line:158
    if OOO0OOO0OOOOO0O00 :#line:159
        OO000O0O000000OOO =0 #line:160
        for O0OOOOOO0OO00O0OO in OOO0OOO0OOOOO0O00 :#line:161
            OOO0O00OOOOOO0000 ={}#line:162
            O0O0OO0OOO0O0000O =OOO0OOO0OOOOO0O00 .get (O0OOOOOO0OO00O0OO )[0 ]#line:163
            for OOO000O00OO000OO0 ,OOO00OOO00OOOOOOO in O0O0OO0OOO0O0000O .__dict__ .items ():#line:164
                if OOO000O00OO000OO0 !='__len__'and OOO000O00OO000OO0 !='__wrapped__':#line:165
                    OOO0O00OOOOOO0000 [OOO000O00OO000OO0 ]=OOO00OOO00OOOOOOO #line:166
            OOO0O00OOOOOO0000 ['eid']=OO000O0O000000OOO #line:167
            OO000O0O000000OOO +=1 #line:168
            if O0OOOOOO0OO00O0OO =='export_admin_action':#line:169
                OOO0O00OOOOOO0000 ['label']='选中导出'#line:170
                OOO0O00OOOOOO0000 ['isExport']=True #line:171
                OOO0O00OOOOOO0000 ['icon']='el-icon-finished'#line:172
                OOO000O0OO0O000OO =[]#line:173
                for O00000O0O0OOO00O0 in enumerate (admin .get_export_formats ()):#line:174
                    OOO000O0OO0O000OO .append ({'value':O00000O0O0OOO00O0 [0 ],'label':O00000O0O0OOO00O0 [1 ]().get_title ()})#line:178
                OOO0O00OOOOOO0000 ['formats']=OOO000O0OO0O000OO #line:180
            else :#line:181
                OOO0O00OOOOOO0000 ['label']=OOO0OOO0OOOOO0O00 .get (O0OOOOOO0OO00O0OO )[2 ]#line:182
            if request .user .has_perm ('{}.{}'.format (OO0OOOO0000O0O0O0 ,O0OOOOOO0OO00O0OO )):#line:185
                OOOOO00000O00O0OO [O0OOOOOO0OO00O0OO ]=OOO0O00OOOOOO0000 #line:186
    if 'delete_selected'in OOOOO00000O00O0OO :#line:187
        del OOOOO00000O00O0OO ['delete_selected']#line:188
    return OOOOO00000O00O0OO #line:189
def search_placeholder (cl ):#line:192
    O0000OOO00OOO000O =get_model_fields (cl .model )#line:194
    for OOO00OO000OO0OO00 in cl .model ._meta .fields :#line:196
        if isinstance (OOO00OO000OO0OO00 ,ForeignKey ):#line:197
            O0000OOO00OOO000O .extend (get_model_fields (OOO00OO000OO0OO00 .related_model ,OOO00OO000OO0OO00 .name ))#line:198
    O00000O0O000O0OO0 =[]#line:200
    for OOO00OOO0OOO0O00O in cl .search_fields :#line:202
        for OOO00OO000OO0OO00 in O0000OOO00OOO000O :#line:203
            if OOO00OO000OO0OO00 [0 ]==OOO00OOO0OOO0O00O :#line:204
                O00000O0O000O0OO0 .append (OOO00OO000OO0OO00 [1 ])#line:205
                break #line:206
    return ",".join (O00000O0O000O0OO0 )#line:208
def write (data ,O0O0OO00000O0O0OO ='ok',OOO00000OO00O0OO0 =True ):#line:211
    OOOOOO0OOOOO00OOO ={'state':OOO00000OO00O0OO0 ,'msg':O0O0OO00000O0O0OO ,'data':data }#line:216
    return HttpResponse (json .dumps (OOOOOO0OOOOO00OOO ,cls =LazyEncoder ),content_type ='application/json')#line:218
def write_obj (obj ):#line:221
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:222
def has_permission (request ,admin ,permission ):#line:225
    O00000O0OOOO0000O =get_permission_codename (permission ,admin .opts )#line:226
    OOOOOO000O0O00O00 ='{}.{}'.format (admin .opts .app_label ,O00000O0OOOO0000O )#line:227
    return request .user .has_perm (OOOOOO000O0O00O00 )#line:228
def get_permission_codename (action ,opts ):#line:231
    ""#line:234
    return '%s_%s'%(action ,opts .model_name )#line:235
from simpleui .templatetags import simpletags #line:238
from simpleui .templatetags .simpletags import get_config #line:239
def get_menus (request ,admin_site ):#line:242
    ""#line:248
    O0000O000O0OOOO0O ={'app_list':admin_site .get_app_list (request ),'request':request }#line:252
    def OO0OO0OOO00O0O0O0 (key ):#line:254
        return request .user .has_perm (key )#line:255
    def _OO00O0O0000OO00O0 (key ):#line:257
        if key =='SIMPLEUI_CONFIG':#line:258
            _OOO00OO0O0O000O00 =get_config (key )#line:260
            if 'menus'in _OOO00OO0O0O000O00 :#line:261
                O000000O00000O00O =_OOO00OO0O0O000O00 .get ('menus')#line:262
                OO00O0O0000O0OO0O =[]#line:263
                for OOOOO0O00O0OO0OO0 in O000000O00000O00O :#line:265
                    if 'codename'not in OOOOO0O00O0OO0OO0 :#line:266
                        OO00O0O0000O0OO0O .append (OOOOO0O00O0OO0OO0 )#line:267
                        continue #line:268
                    O0OOOO000O0O0OO0O =OOOOO0O00O0OO0OO0 .get ('codename')#line:269
                    key ='{}.{}'.format (O0OOOO000O0O0OO0O ,O0OOOO000O0O0OO0O )#line:272
                    if OO0OO0OOO00O0O0O0 (key ):#line:273
                        if 'models'in OOOOO0O00O0OO0OO0 :#line:275
                            OOOOO0OO0OO0OO0OO =OOOOO0O00O0OO0OO0 .get ('models')#line:276
                            O0OOOO0O0O0OO0O00 =[]#line:277
                            for OOOO0O0O000000000 in OOOOO0OO0OO0OO0OO :#line:278
                                if 'codename'in OOOO0O0O000000000 :#line:279
                                    if OO0OO0OOO00O0O0O0 ('{}.{}'.format (O0OOOO000O0O0OO0O ,OOOO0O0O000000000 .get ('codename'))):#line:280
                                        O0OOOO0O0O0OO0O00 .append (OOOO0O0O000000000 )#line:281
                                else :#line:282
                                    O0OOOO0O0O0OO0O00 .append (OOOO0O0O000000000 )#line:283
                            OOOOO0O00O0OO0OO0 ['models']=O0OOOO0O0O0OO0O00 #line:284
                        OO00O0O0000O0OO0O .append (OOOOO0O00O0OO0OO0 )#line:286
                _OOO00OO0O0O000O00 ['menus']=OO00O0O0000O0OO0O #line:287
        return _OOO00OO0O0O000O00 #line:289
    return simpletags .menus (O0000O000O0OOOO0O ,_get_config =_OO00O0O0000OO00O0 )#line:291
