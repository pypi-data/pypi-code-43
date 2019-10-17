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
def get_model_fields (model ,O0OOOOOO0OOOO0O00 =None ):#line:27
    ""#line:33
    O00O0OOO00OOO0OOO =[]#line:34
    OO00OO00O00OOOOO0 =model ._meta .fields #line:35
    for O00O00OO0000O0OOO in OO00OO00O00OOOOO0 :#line:36
        O0O0OOOO0000O0OOO =O00O00OO0000O0OOO .name #line:37
        if hasattr (O00O00OO0000O0OOO ,'verbose_name'):#line:38
            O0O0OOOO0000O0OOO =getattr (O00O00OO0000O0OOO ,'verbose_name')#line:39
        if isinstance (O0O0OOOO0000O0OOO ,Promise ):#line:41
            O0O0OOOO0000O0OOO =str (O0O0OOOO0000O0OOO )#line:42
        if O0OOOOOO0OOOO0O00 :#line:44
            O00O0OOO00OOO0OOO .append (('{}__{}'.format (O0OOOOOO0OOOO0O00 ,O00O00OO0000O0OOO .name ),O0O0OOOO0000O0OOO ))#line:45
        else :#line:46
            O00O0OOO00OOO0OOO .append ((O00O00OO0000O0OOO .name ,O0O0OOOO0000O0OOO ))#line:47
    return O00O0OOO00OOO0OOO #line:49
def find_field (fields ,name ):#line:52
    for O0O0OO0OOOOOO0OOO in fields :#line:53
        if name ==O0O0OO0OOOOOO0OOO [0 ]:#line:54
            return O0O0OO0OOOOOO0OOO [1 ]#line:55
    return False #line:56
MODEL_CACHE ={}#line:60
def get_model_info (model_admin ,request ):#line:63
    O000OO0O0O00OO00O =str (model_admin )#line:67
    if O000OO0O0O00OO00O in MODEL_CACHE :#line:68
        OOO0O000OO0OO0O00 =MODEL_CACHE .get (O000OO0O0O00OO00O )#line:69
        return OOO0O000OO0OO0O00 .get ('values_fields'),OOO0O000OO0OO0O00 .get ('fun_fields'),OOO0O000OO0OO0O00 .get ('headers'),OOO0O000OO0OO0O00 .get ('formatter'),OOO0O000OO0OO0O00 .get ('choices')#line:71
    OOO0O000OOOO0OO00 =get_model_fields (model_admin .model )#line:72
    OO0000O0OO00O0OOO =model_admin .get_list_display (request )#line:74
    O0O0000OOOOO0OOOO =[]#line:75
    OO0O00O0OO0O0O00O =[]#line:76
    O000OO00O0OO000OO =[]#line:77
    OO00O0OOO0OOO0O00 ={}#line:80
    if hasattr (model_admin ,'fields_options'):#line:81
        OO00O0OOO0OOO0O00 =getattr (model_admin ,'fields_options')#line:82
    for O00OOOOOO0O000O00 in OO0000O0OO00O0OOO :#line:84
        OO00OOOO0O0OOO0OO =find_field (OOO0O000OOOO0OO00 ,O00OOOOOO0O000O00 )#line:85
        if OO00OOOO0O0OOO0OO :#line:86
            OO0O00O0OO0O0O00O .append (O00OOOOOO0O000O00 )#line:87
            O00O000OO0O0OOO00 ={'name':O00OOOOOO0O000O00 ,'label':OO00OOOO0O0OOO0OO }#line:91
            if O00OOOOOO0O000O00 in OO00O0OOO0OOO0O00 :#line:92
                O00O000OO0O0OOO00 =dict (O00O000OO0O0OOO00 ,**OO00O0OOO0OOO0O00 .get (O00OOOOOO0O000O00 ))#line:93
            if 'sortable'not in O00O000OO0O0OOO00 :#line:95
                O00O000OO0O0OOO00 ['sortable']='custom'#line:97
            O000OO00O0OO000OO .append (O00O000OO0O0OOO00 )#line:98
        else :#line:99
            O0O0000OOOOO0OOOO .append (O00OOOOOO0O000O00 )#line:100
            OO00OOOO0O0OOO0OO =O00OOOOOO0O000O00 #line:101
            if hasattr (model_admin ,O00OOOOOO0O000O00 ):#line:102
                OOOOOOOO0O0O00OOO =getattr (model_admin ,O00OOOOOO0O000O00 ).__dict__ #line:103
            else :#line:104
                OOOOOOOO0O0O00OOO =getattr (model_admin .model ,O00OOOOOO0O000O00 ).__dict__ #line:105
            if 'short_description'in OOOOOOOO0O0O00OOO :#line:106
                OO00OOOO0O0OOO0OO =OOOOOOOO0O0O00OOO .get ('short_description')#line:107
            elif OO00OOOO0O0OOO0OO =='__str__':#line:108
                OO00OOOO0O0OOO0OO =model_admin .model ._meta .verbose_name_plural #line:109
            O00O000OO0O0OOO00 ={'name':O00OOOOOO0O000O00 ,'label':OO00OOOO0O0OOO0OO }#line:113
            if O00OOOOOO0O000O00 in OO00O0OOO0OOO0O00 :#line:114
                O00O000OO0O0OOO00 =dict (O00O000OO0O0OOO00 ,**OO00O0OOO0OOO0O00 .get (O00OOOOOO0O000O00 ))#line:115
            O00O000OO0O0OOO00 ['sortable']=False #line:117
            O000OO00O0OO000OO .append (O00O000OO0O0OOO00 )#line:118
    O0O00O0OOOOOO00O0 =None #line:120
    if hasattr (model_admin ,'formatter'):#line:121
        O0O00O0OOOOOO00O0 =getattr (model_admin ,'formatter')#line:122
    O00O0000O0OO0OOOO =model_admin .model #line:125
    O0O0OO000O0OO0000 ={}#line:126
    for OO0000000O0O0000O in dir (O00O0000O0OO0OOOO ):#line:127
        if OO0000000O0O0000O .endswith ('choices'):#line:128
            OOOO00OO0O0OO0O0O ={}#line:129
            O0O00000O0O000OO0 =getattr (O00O0000O0OO0OOOO ,OO0000000O0O0000O )#line:130
            for O00OOOOOO0O000O00 in O0O00000O0O000OO0 :#line:131
                OOOO00OO0O0OO0O0O [O00OOOOOO0O000O00 [0 ]]=O00OOOOOO0O000O00 [1 ]#line:132
            O0O0OO000O0OO0000 [OO0000000O0O0000O ]=OOOO00OO0O0OO0O0O #line:133
    for OO0000000O0O0000O in O00O0000O0OO0OOOO ._meta .fields :#line:134
        OOOO00OO0O0OO0O0O ={}#line:135
        if hasattr (OO0000000O0O0000O ,'choices'):#line:136
            if len (OO0000000O0O0000O .choices )>0 :#line:137
                for O00OOOOOO0O000O00 in OO0000000O0O0000O .choices :#line:138
                    OOOO00OO0O0OO0O0O [O00OOOOOO0O000O00 [0 ]]=O00OOOOOO0O000O00 [1 ]#line:139
                O0O0OO000O0OO0000 [OO0000000O0O0000O .name ]=OOOO00OO0O0OO0O0O #line:140
    MODEL_CACHE [O000OO0O0O00OO00O ]={'values_fields':OO0O00O0OO0O0O00O ,'fun_fields':O0O0000OOOOO0OOOO ,'headers':O000OO00O0OO000OO ,'formatter':O0O00O0OOOOOO00O0 ,'choices':O0O0OO000O0OO0000 ,}#line:147
    return OO0O00O0OO0O0O00O ,O0O0000OOOOO0OOOO ,O000OO00O0OO000OO ,O0O00O0OOOOOO00O0 ,O0O0OO000O0OO0000 #line:148
def get_custom_button (request ,admin ):#line:151
    OO00000O0OO0000OO ={}#line:152
    OO000OO0OOOO0O0OO =admin .get_actions (request )#line:153
    OOO0OOOOO0OOOOOOO =admin .opts .app_label #line:158
    if OO000OO0OOOO0O0OO :#line:159
        O00O00O000O00O00O =0 #line:160
        for OOO00000OOOOO0OOO in OO000OO0OOOO0O0OO :#line:161
            O00OOO0O000OO0O0O ={}#line:162
            OOO0OOO0O0OOO0OO0 =OO000OO0OOOO0O0OO .get (OOO00000OOOOO0OOO )[0 ]#line:163
            for OOO000OO0O00OOOOO ,O0000OOO0O0O00OO0 in OOO0OOO0O0OOO0OO0 .__dict__ .items ():#line:164
                if OOO000OO0O00OOOOO !='__len__'and OOO000OO0O00OOOOO !='__wrapped__':#line:165
                    O00OOO0O000OO0O0O [OOO000OO0O00OOOOO ]=O0000OOO0O0O00OO0 #line:166
            O00OOO0O000OO0O0O ['eid']=O00O00O000O00O00O #line:167
            O00O00O000O00O00O +=1 #line:168
            if OOO00000OOOOO0OOO =='export_admin_action':#line:169
                O00OOO0O000OO0O0O ['label']='选中导出'#line:170
                O00OOO0O000OO0O0O ['isExport']=True #line:171
                O00OOO0O000OO0O0O ['icon']='el-icon-finished'#line:172
                O000OOO0O0000OOOO =[]#line:173
                for OO00OO00000OO000O in enumerate (admin .get_export_formats ()):#line:174
                    O000OOO0O0000OOOO .append ({'value':OO00OO00000OO000O [0 ],'label':OO00OO00000OO000O [1 ]().get_title ()})#line:178
                O00OOO0O000OO0O0O ['formats']=O000OOO0O0000OOOO #line:180
            else :#line:181
                O00OOO0O000OO0O0O ['label']=OO000OO0OOOO0O0OO .get (OOO00000OOOOO0OOO )[2 ]#line:182
            if request .user .has_perm ('{}.{}'.format (OOO0OOOOO0OOOOOOO ,OOO00000OOOOO0OOO )):#line:185
                OO00000O0OO0000OO [OOO00000OOOOO0OOO ]=O00OOO0O000OO0O0O #line:186
    if 'delete_selected'in OO00000O0OO0000OO :#line:187
        del OO00000O0OO0000OO ['delete_selected']#line:188
    return OO00000O0OO0000OO #line:189
def search_placeholder (cl ):#line:192
    OOO0OO0OO0O00OO00 =get_model_fields (cl .model )#line:194
    for OO0O00O00O0O00OOO in cl .model ._meta .fields :#line:196
        if isinstance (OO0O00O00O0O00OOO ,ForeignKey ):#line:197
            OOO0OO0OO0O00OO00 .extend (get_model_fields (OO0O00O00O0O00OOO .related_model ,OO0O00O00O0O00OOO .name ))#line:198
    OO0O0OO0OOOO00OOO =[]#line:200
    for OO0O0OOO0O00O00O0 in cl .search_fields :#line:202
        for OO0O00O00O0O00OOO in OOO0OO0OO0O00OO00 :#line:203
            if OO0O00O00O0O00OOO [0 ]==OO0O0OOO0O00O00O0 :#line:204
                OO0O0OO0OOOO00OOO .append (OO0O00O00O0O00OOO [1 ])#line:205
                break #line:206
    return ",".join (OO0O0OO0OOOO00OOO )#line:208
def write (data ,OOOOO00O0OOOOOOOO ='ok',O0OO0OO00O0O00O00 =True ):#line:211
    O0OOO0OO0OO00O0OO ={'state':O0OO0OO00O0O00O00 ,'msg':OOOOO00O0OOOOOOOO ,'data':data }#line:216
    return HttpResponse (json .dumps (O0OOO0OO0OO00O0OO ,cls =LazyEncoder ),content_type ='application/json')#line:218
def write_obj (obj ):#line:221
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:222
def has_permission (request ,admin ,permission ):#line:225
    O0OO0O000O0O000OO =get_permission_codename (permission ,admin .opts )#line:226
    O00O0O0OOOOO00O00 ='{}.{}'.format (admin .opts .app_label ,O0OO0O000O0O000OO )#line:227
    return request .user .has_perm (O00O0O0OOOOO00O00 )#line:228
def get_permission_codename (action ,opts ):#line:231
    ""#line:234
    return '%s_%s'%(action ,opts .model_name )#line:235
from simpleui .templatetags import simpletags #line:238
from simpleui .templatetags .simpletags import get_config #line:239
def get_menus (request ,admin_site ):#line:242
    ""#line:248
    OOO0O00000000OOO0 ={'app_list':admin_site .get_app_list (request ),'request':request }#line:252
    def OO0O000OOO0OO0OOO (key ):#line:254
        return request .user .has_perm (key )#line:255
    def _O000O0O0000OOO0O0 (key ):#line:257
        if key =='SIMPLEUI_CONFIG':#line:258
            _OOO00000OOO0O00O0 =get_config (key )#line:260
            if 'menus'in _OOO00000OOO0O00O0 :#line:261
                O00OO00O000OO000O =_OOO00000OOO0O00O0 .get ('menus')#line:262
                OO0OOO00OOO00OOOO =[]#line:263
                for OO00OOOOOO00O0O00 in O00OO00O000OO000O :#line:265
                    if 'codename'not in OO00OOOOOO00O0O00 :#line:266
                        OO0OOO00OOO00OOOO .append (OO00OOOOOO00O0O00 )#line:267
                        continue #line:268
                    OOOOO00OO00000000 =OO00OOOOOO00O0O00 .get ('codename')#line:269
                    key ='{}.{}'.format (OOOOO00OO00000000 ,OOOOO00OO00000000 )#line:272
                    if OO0O000OOO0OO0OOO (key ):#line:273
                        if 'models'in OO00OOOOOO00O0O00 :#line:275
                            OOO0OOOOO0OO0000O =OO00OOOOOO00O0O00 .get ('models')#line:276
                            O0OOO000OOO0OO00O =[]#line:277
                            for OO0OO000OOOO0O000 in OOO0OOOOO0OO0000O :#line:278
                                if 'codename'in OO0OO000OOOO0O000 :#line:279
                                    if OO0O000OOO0OO0OOO ('{}.{}'.format (OOOOO00OO00000000 ,OO0OO000OOOO0O000 .get ('codename'))):#line:280
                                        O0OOO000OOO0OO00O .append (OO0OO000OOOO0O000 )#line:281
                                else :#line:282
                                    O0OOO000OOO0OO00O .append (OO0OO000OOOO0O000 )#line:283
                            OO00OOOOOO00O0O00 ['models']=O0OOO000OOO0OO00O #line:284
                        OO0OOO00OOO00OOOO .append (OO00OOOOOO00O0O00 )#line:286
                _OOO00000OOO0O00O0 ['menus']=OO0OOO00OOO00OOOO #line:287
        return _OOO00000OOO0O00O0 #line:289
    return simpletags .menus (OOO0O00000000OOO0 ,_get_config =_O000O0O0000OOO0O0 )#line:291
