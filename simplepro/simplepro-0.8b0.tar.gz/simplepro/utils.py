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
def get_model_fields (model ,O0O0OOO0O000000O0 =None ):#line:27
    ""#line:33
    OOOOO00O0OO00000O =[]#line:34
    O0O0O000OOOO0OO00 =model ._meta .fields #line:35
    for O0OOOO0OO0OOO0O00 in O0O0O000OOOO0OO00 :#line:36
        OOO0O0OOOO0O0000O =O0OOOO0OO0OOO0O00 .name #line:37
        if hasattr (O0OOOO0OO0OOO0O00 ,'verbose_name'):#line:38
            OOO0O0OOOO0O0000O =getattr (O0OOOO0OO0OOO0O00 ,'verbose_name')#line:39
        if isinstance (OOO0O0OOOO0O0000O ,Promise ):#line:41
            OOO0O0OOOO0O0000O =str (OOO0O0OOOO0O0000O )#line:42
        if O0O0OOO0O000000O0 :#line:44
            OOOOO00O0OO00000O .append (('{}__{}'.format (O0O0OOO0O000000O0 ,O0OOOO0OO0OOO0O00 .name ),OOO0O0OOOO0O0000O ))#line:45
        else :#line:46
            OOOOO00O0OO00000O .append ((O0OOOO0OO0OOO0O00 .name ,OOO0O0OOOO0O0000O ))#line:47
    return OOOOO00O0OO00000O #line:49
def find_field (fields ,name ):#line:52
    for O00OOOOOOO0OO000O in fields :#line:53
        if name ==O00OOOOOOO0OO000O [0 ]:#line:54
            return O00OOOOOOO0OO000O [1 ]#line:55
    return False #line:56
MODEL_CACHE ={}#line:60
def get_model_info (model_admin ,request ):#line:63
    OO0OO0O00O00O00O0 =str (model_admin )#line:67
    if OO0OO0O00O00O00O0 in MODEL_CACHE :#line:68
        OO0OOOOO0O0OOOO0O =MODEL_CACHE .get (OO0OO0O00O00O00O0 )#line:69
        return OO0OOOOO0O0OOOO0O .get ('values_fields'),OO0OOOOO0O0OOOO0O .get ('fun_fields'),OO0OOOOO0O0OOOO0O .get ('headers'),OO0OOOOO0O0OOOO0O .get ('formatter'),OO0OOOOO0O0OOOO0O .get ('choices')#line:71
    O000O0O0O0OO00000 =get_model_fields (model_admin .model )#line:72
    OOO0O000O00O00OO0 =model_admin .get_list_display (request )#line:74
    OO0000OOOO0OOO000 =[]#line:75
    O0O0OOO0OOO0O0OOO =[]#line:76
    O00OOO00OOOOO0O0O =[]#line:77
    O00O0000OO0OOO000 ={}#line:80
    if hasattr (model_admin ,'fields_options'):#line:81
        O00O0000OO0OOO000 =getattr (model_admin ,'fields_options')#line:82
    for OO0O0000OO0O000OO in OOO0O000O00O00OO0 :#line:84
        O0O000OOO0O0O0OOO =find_field (O000O0O0O0OO00000 ,OO0O0000OO0O000OO )#line:85
        if O0O000OOO0O0O0OOO :#line:86
            O0O0OOO0OOO0O0OOO .append (OO0O0000OO0O000OO )#line:87
            O0OOO0OOOO00O0O00 ={'name':OO0O0000OO0O000OO ,'label':O0O000OOO0O0O0OOO }#line:91
            if OO0O0000OO0O000OO in O00O0000OO0OOO000 :#line:92
                O0OOO0OOOO00O0O00 =dict (O0OOO0OOOO00O0O00 ,**O00O0000OO0OOO000 .get (OO0O0000OO0O000OO ))#line:93
            if 'sortable'not in O0OOO0OOOO00O0O00 :#line:95
                O0OOO0OOOO00O0O00 ['sortable']='custom'#line:97
            O00OOO00OOOOO0O0O .append (O0OOO0OOOO00O0O00 )#line:98
        else :#line:99
            OO0000OOOO0OOO000 .append (OO0O0000OO0O000OO )#line:100
            O0O000OOO0O0O0OOO =OO0O0000OO0O000OO #line:101
            if hasattr (model_admin ,OO0O0000OO0O000OO ):#line:102
                O0OO0O0OOO0O00O0O =getattr (model_admin ,OO0O0000OO0O000OO ).__dict__ #line:103
            else :#line:104
                O0OO0O0OOO0O00O0O =getattr (model_admin .model ,OO0O0000OO0O000OO ).__dict__ #line:105
            if 'short_description'in O0OO0O0OOO0O00O0O :#line:106
                O0O000OOO0O0O0OOO =O0OO0O0OOO0O00O0O .get ('short_description')#line:107
            elif O0O000OOO0O0O0OOO =='__str__':#line:108
                O0O000OOO0O0O0OOO =model_admin .model ._meta .verbose_name_plural #line:109
            O0OOO0OOOO00O0O00 ={'name':OO0O0000OO0O000OO ,'label':O0O000OOO0O0O0OOO }#line:113
            if OO0O0000OO0O000OO in O00O0000OO0OOO000 :#line:114
                O0OOO0OOOO00O0O00 =dict (O0OOO0OOOO00O0O00 ,**O00O0000OO0OOO000 .get (OO0O0000OO0O000OO ))#line:115
            O0OOO0OOOO00O0O00 ['sortable']=False #line:117
            O00OOO00OOOOO0O0O .append (O0OOO0OOOO00O0O00 )#line:118
    OOO000O0O0OO0OO00 =None #line:120
    if hasattr (model_admin ,'formatter'):#line:121
        OOO000O0O0OO0OO00 =getattr (model_admin ,'formatter')#line:122
    OOOO0000000O0OOO0 =model_admin .model #line:125
    O000O00OOOOO000O0 ={}#line:126
    for O000OO00O00O0000O in dir (OOOO0000000O0OOO0 ):#line:127
        if O000OO00O00O0000O .endswith ('choices'):#line:128
            O00O000OOOOO00O00 ={}#line:129
            O0O0OO00000OO0000 =getattr (OOOO0000000O0OOO0 ,O000OO00O00O0000O )#line:130
            for OO0O0000OO0O000OO in O0O0OO00000OO0000 :#line:131
                O00O000OOOOO00O00 [OO0O0000OO0O000OO [0 ]]=OO0O0000OO0O000OO [1 ]#line:132
            O000O00OOOOO000O0 [O000OO00O00O0000O ]=O00O000OOOOO00O00 #line:133
    for O000OO00O00O0000O in OOOO0000000O0OOO0 ._meta .fields :#line:134
        O00O000OOOOO00O00 ={}#line:135
        if hasattr (O000OO00O00O0000O ,'choices'):#line:136
            if len (O000OO00O00O0000O .choices )>0 :#line:137
                for OO0O0000OO0O000OO in O000OO00O00O0000O .choices :#line:138
                    O00O000OOOOO00O00 [OO0O0000OO0O000OO [0 ]]=OO0O0000OO0O000OO [1 ]#line:139
                O000O00OOOOO000O0 [O000OO00O00O0000O .name ]=O00O000OOOOO00O00 #line:140
    MODEL_CACHE [OO0OO0O00O00O00O0 ]={'values_fields':O0O0OOO0OOO0O0OOO ,'fun_fields':OO0000OOOO0OOO000 ,'headers':O00OOO00OOOOO0O0O ,'formatter':OOO000O0O0OO0OO00 ,'choices':O000O00OOOOO000O0 ,}#line:147
    return O0O0OOO0OOO0O0OOO ,OO0000OOOO0OOO000 ,O00OOO00OOOOO0O0O ,OOO000O0O0OO0OO00 ,O000O00OOOOO000O0 #line:148
def get_custom_button (request ,admin ):#line:151
    OOOO0OO0O000000O0 ={}#line:152
    OO0O0O0OOO00O000O =admin .get_actions (request )#line:153
    OOO00O000O0O00OO0 =admin .opts .app_label #line:158
    if OO0O0O0OOO00O000O :#line:159
        OO00000OOOOO00O00 =0 #line:160
        for O00O0OO0000000O00 in OO0O0O0OOO00O000O :#line:161
            O00OOO000O0O0000O ={}#line:162
            O00O00OO0O0000OOO =OO0O0O0OOO00O000O .get (O00O0OO0000000O00 )[0 ]#line:163
            for O00OO00O000OO00O0 ,OOOOOOOOOOO00OOO0 in O00O00OO0O0000OOO .__dict__ .items ():#line:164
                if O00OO00O000OO00O0 !='__len__'and O00OO00O000OO00O0 !='__wrapped__':#line:165
                    O00OOO000O0O0000O [O00OO00O000OO00O0 ]=OOOOOOOOOOO00OOO0 #line:166
            O00OOO000O0O0000O ['eid']=OO00000OOOOO00O00 #line:167
            OO00000OOOOO00O00 +=1 #line:168
            if O00O0OO0000000O00 =='export_admin_action':#line:169
                O00OOO000O0O0000O ['label']='选中导出'#line:170
                O00OOO000O0O0000O ['isExport']=True #line:171
                O00OOO000O0O0000O ['icon']='el-icon-finished'#line:172
                OO0OO0O0OO0000O0O =[]#line:173
                for O0000OOO00000OO00 in enumerate (admin .get_export_formats ()):#line:174
                    OO0OO0O0OO0000O0O .append ({'value':O0000OOO00000OO00 [0 ],'label':O0000OOO00000OO00 [1 ]().get_title ()})#line:178
                O00OOO000O0O0000O ['formats']=OO0OO0O0OO0000O0O #line:180
            else :#line:181
                O00OOO000O0O0000O ['label']=OO0O0O0OOO00O000O .get (O00O0OO0000000O00 )[2 ]#line:182
            if request .user .has_perm ('{}.{}'.format (OOO00O000O0O00OO0 ,O00O0OO0000000O00 )):#line:185
                OOOO0OO0O000000O0 [O00O0OO0000000O00 ]=O00OOO000O0O0000O #line:186
    if 'delete_selected'in OOOO0OO0O000000O0 :#line:187
        del OOOO0OO0O000000O0 ['delete_selected']#line:188
    return OOOO0OO0O000000O0 #line:189
def search_placeholder (cl ):#line:192
    OOO00O00O00O0O0O0 =get_model_fields (cl .model )#line:194
    for O000O0OO00O0O0000 in cl .model ._meta .fields :#line:196
        if isinstance (O000O0OO00O0O0000 ,ForeignKey ):#line:197
            OOO00O00O00O0O0O0 .extend (get_model_fields (O000O0OO00O0O0000 .related_model ,O000O0OO00O0O0000 .name ))#line:198
    O00000O0OOO0O0OO0 =[]#line:200
    for O0O0OO00O0O0OO00O in cl .search_fields :#line:202
        for O000O0OO00O0O0000 in OOO00O00O00O0O0O0 :#line:203
            if O000O0OO00O0O0000 [0 ]==O0O0OO00O0O0OO00O :#line:204
                O00000O0OOO0O0OO0 .append (O000O0OO00O0O0000 [1 ])#line:205
                break #line:206
    return ",".join (O00000O0OOO0O0OO0 )#line:208
def write (data ,O00000OO000O00OO0 ='ok',OO00000O00O000OO0 =True ):#line:211
    O000OOOOOO00OO0OO ={'state':OO00000O00O000OO0 ,'msg':O00000OO000O00OO0 ,'data':data }#line:216
    return HttpResponse (json .dumps (O000OOOOOO00OO0OO ,cls =LazyEncoder ),content_type ='application/json')#line:218
def write_obj (obj ):#line:221
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:222
def has_permission (request ,admin ,permission ):#line:225
    OOOO000OO00OOO000 =get_permission_codename (permission ,admin .opts )#line:226
    OO0O0OO000O0OOO0O ='{}.{}'.format (admin .opts .app_label ,OOOO000OO00OOO000 )#line:227
    return request .user .has_perm (OO0O0OO000O0OOO0O )#line:228
def get_permission_codename (action ,opts ):#line:231
    ""#line:234
    return '%s_%s'%(action ,opts .model_name )#line:235
from simpleui .templatetags import simpletags #line:238
from simpleui .templatetags .simpletags import get_config #line:239
def get_menus (request ,admin_site ):#line:242
    ""#line:248
    OO000OO00OO0O0000 ={'app_list':admin_site .get_app_list (request ),'request':request }#line:252
    def OOOOO00O0OO0O0OOO (key ):#line:254
        return request .user .has_perm (key )#line:255
    def _O0O00O0OO0000OOO0 (key ):#line:257
        if key =='SIMPLEUI_CONFIG':#line:258
            _OO0OOOOOO00OOOOOO =get_config (key )#line:260
            if 'menus'in _OO0OOOOOO00OOOOOO :#line:261
                OOO00O0000O0000O0 =_OO0OOOOOO00OOOOOO .get ('menus')#line:262
                OOO0OOO0OO00000O0 =[]#line:263
                for OOOOO00O00O00OO0O in OOO00O0000O0000O0 :#line:265
                    if 'codename'not in OOOOO00O00O00OO0O :#line:266
                        OOO0OOO0OO00000O0 .append (OOOOO00O00O00OO0O )#line:267
                        continue #line:268
                    O0O00OOO0OOOOO00O =OOOOO00O00O00OO0O .get ('codename')#line:269
                    key ='{}.{}'.format (O0O00OOO0OOOOO00O ,O0O00OOO0OOOOO00O )#line:272
                    if OOOOO00O0OO0O0OOO (key ):#line:273
                        if 'models'in OOOOO00O00O00OO0O :#line:275
                            OOOO0O0000OOO0OOO =OOOOO00O00O00OO0O .get ('models')#line:276
                            OO0O0OOO00O0O0O00 =[]#line:277
                            for OO00O00O0OO00O0OO in OOOO0O0000OOO0OOO :#line:278
                                if 'codename'in OO00O00O0OO00O0OO :#line:279
                                    if OOOOO00O0OO0O0OOO ('{}.{}'.format (O0O00OOO0OOOOO00O ,OO00O00O0OO00O0OO .get ('codename'))):#line:280
                                        OO0O0OOO00O0O0O00 .append (OO00O00O0OO00O0OO )#line:281
                                else :#line:282
                                    OO0O0OOO00O0O0O00 .append (OO00O00O0OO00O0OO )#line:283
                            OOOOO00O00O00OO0O ['models']=OO0O0OOO00O0O0O00 #line:284
                        OOO0OOO0OO00000O0 .append (OOOOO00O00O00OO0O )#line:286
                _OO0OOOOOO00OOOOOO ['menus']=OOO0OOO0OO00000O0 #line:287
        return _OO0OOOOOO00OOOOOO #line:289
    return simpletags .menus (OO000OO00OO0O0000 ,_get_config =_O0O00O0OO0000OOO0 )#line:291
