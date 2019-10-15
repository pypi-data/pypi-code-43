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
def get_model_fields (model ,O0OOOO0OO0OO0000O =None ):#line:27
    ""#line:33
    OO00000OO000OO0OO =[]#line:34
    OOO0000OOO0O00O0O =model ._meta .fields #line:35
    for OOOO0OO00OO000000 in OOO0000OOO0O00O0O :#line:36
        O00O0O0O0O0OOOO00 =OOOO0OO00OO000000 .name #line:37
        if hasattr (OOOO0OO00OO000000 ,'verbose_name'):#line:38
            O00O0O0O0O0OOOO00 =getattr (OOOO0OO00OO000000 ,'verbose_name')#line:39
        if isinstance (O00O0O0O0O0OOOO00 ,Promise ):#line:41
            O00O0O0O0O0OOOO00 =str (O00O0O0O0O0OOOO00 )#line:42
        if O0OOOO0OO0OO0000O :#line:44
            OO00000OO000OO0OO .append (('{}__{}'.format (O0OOOO0OO0OO0000O ,OOOO0OO00OO000000 .name ),O00O0O0O0O0OOOO00 ))#line:45
        else :#line:46
            OO00000OO000OO0OO .append ((OOOO0OO00OO000000 .name ,O00O0O0O0O0OOOO00 ))#line:47
    return OO00000OO000OO0OO #line:49
def find_field (fields ,name ):#line:52
    for OO00000O00O0O0000 in fields :#line:53
        if name ==OO00000O00O0O0000 [0 ]:#line:54
            return OO00000O00O0O0000 [1 ]#line:55
    return False #line:56
MODEL_CACHE ={}#line:60
def get_model_info (model_admin ,request ):#line:63
    O0O0OOOO000O0OO0O =str (model_admin )#line:67
    if O0O0OOOO000O0OO0O in MODEL_CACHE :#line:68
        O0O000O00O00O0O0O =MODEL_CACHE .get (O0O0OOOO000O0OO0O )#line:69
        return O0O000O00O00O0O0O .get ('values_fields'),O0O000O00O00O0O0O .get ('fun_fields'),O0O000O00O00O0O0O .get ('headers'),O0O000O00O00O0O0O .get ('formatter'),O0O000O00O00O0O0O .get ('choices')#line:71
    O00OOO00OO0OO0O0O =get_model_fields (model_admin .model )#line:72
    OO000000O0O0000O0 =model_admin .get_list_display (request )#line:74
    OOO00O0OO00000000 =[]#line:75
    O0OO00O0O00O0000O =[]#line:76
    O0OOO000O00OOOOOO =[]#line:77
    OOO0O0OOO00O000O0 ={}#line:80
    if hasattr (model_admin ,'fields_options'):#line:81
        OOO0O0OOO00O000O0 =getattr (model_admin ,'fields_options')#line:82
    for O0O0OOO0OO000OO00 in OO000000O0O0000O0 :#line:84
        O0OOOO0O000OO0O00 =find_field (O00OOO00OO0OO0O0O ,O0O0OOO0OO000OO00 )#line:85
        if O0OOOO0O000OO0O00 :#line:86
            O0OO00O0O00O0000O .append (O0O0OOO0OO000OO00 )#line:87
            O0000O0OO0O00O00O ={'name':O0O0OOO0OO000OO00 ,'label':O0OOOO0O000OO0O00 }#line:91
            if O0O0OOO0OO000OO00 in OOO0O0OOO00O000O0 :#line:92
                O0000O0OO0O00O00O =dict (O0000O0OO0O00O00O ,**OOO0O0OOO00O000O0 .get (O0O0OOO0OO000OO00 ))#line:93
            if 'sortable'not in O0000O0OO0O00O00O :#line:95
                O0000O0OO0O00O00O ['sortable']='custom'#line:97
            O0OOO000O00OOOOOO .append (O0000O0OO0O00O00O )#line:98
        else :#line:99
            OOO00O0OO00000000 .append (O0O0OOO0OO000OO00 )#line:100
            O0OOOO0O000OO0O00 =O0O0OOO0OO000OO00 #line:101
            OOO0OO0000OO000OO =getattr (model_admin .model ,O0O0OOO0OO000OO00 ).__dict__ #line:102
            if 'short_description'in OOO0OO0000OO000OO :#line:103
                O0OOOO0O000OO0O00 =OOO0OO0000OO000OO .get ('short_description')#line:104
            elif O0OOOO0O000OO0O00 =='__str__':#line:105
                O0OOOO0O000OO0O00 =model_admin .model ._meta .verbose_name_plural #line:106
            O0000O0OO0O00O00O ={'name':O0O0OOO0OO000OO00 ,'label':O0OOOO0O000OO0O00 }#line:110
            if O0O0OOO0OO000OO00 in OOO0O0OOO00O000O0 :#line:111
                O0000O0OO0O00O00O =dict (O0000O0OO0O00O00O ,**OOO0O0OOO00O000O0 .get (O0O0OOO0OO000OO00 ))#line:112
            O0000O0OO0O00O00O ['sortable']=False #line:114
            O0OOO000O00OOOOOO .append (O0000O0OO0O00O00O )#line:115
    O0OO00OO00O0O0O0O =None #line:117
    if hasattr (model_admin ,'formatter'):#line:118
        O0OO00OO00O0O0O0O =getattr (model_admin ,'formatter')#line:119
    O0OO0O0000OO000O0 =model_admin .model #line:122
    OO0O000OO0O00000O ={}#line:123
    for OO00OOO0O0000O000 in dir (O0OO0O0000OO000O0 ):#line:124
        if OO00OOO0O0000O000 .endswith ('choices'):#line:125
            OO00O00O0OOOOO0OO ={}#line:126
            O0OOOO0O0O000O00O =getattr (O0OO0O0000OO000O0 ,OO00OOO0O0000O000 )#line:127
            for O0O0OOO0OO000OO00 in O0OOOO0O0O000O00O :#line:128
                OO00O00O0OOOOO0OO [O0O0OOO0OO000OO00 [0 ]]=O0O0OOO0OO000OO00 [1 ]#line:129
            OO0O000OO0O00000O [OO00OOO0O0000O000 ]=OO00O00O0OOOOO0OO #line:130
    for OO00OOO0O0000O000 in O0OO0O0000OO000O0 ._meta .fields :#line:131
        OO00O00O0OOOOO0OO ={}#line:132
        if hasattr (OO00OOO0O0000O000 ,'choices'):#line:133
            if len (OO00OOO0O0000O000 .choices )>0 :#line:134
                for O0O0OOO0OO000OO00 in OO00OOO0O0000O000 .choices :#line:135
                    OO00O00O0OOOOO0OO [O0O0OOO0OO000OO00 [0 ]]=O0O0OOO0OO000OO00 [1 ]#line:136
                OO0O000OO0O00000O [OO00OOO0O0000O000 .name ]=OO00O00O0OOOOO0OO #line:137
    MODEL_CACHE [O0O0OOOO000O0OO0O ]={'values_fields':O0OO00O0O00O0000O ,'fun_fields':OOO00O0OO00000000 ,'headers':O0OOO000O00OOOOOO ,'formatter':O0OO00OO00O0O0O0O ,'choices':OO0O000OO0O00000O ,}#line:144
    return O0OO00O0O00O0000O ,OOO00O0OO00000000 ,O0OOO000O00OOOOOO ,O0OO00OO00O0O0O0O ,OO0O000OO0O00000O #line:145
def get_custom_button (request ,admin ):#line:148
    O00O0OOOOO0O0OOOO ={}#line:149
    OO00OO00OO00O0OO0 =admin .get_actions (request )#line:150
    OO0O0OOO00OO0O000 =admin .opts .app_label #line:155
    if OO00OO00OO00O0OO0 :#line:156
        O00O0000OO000O00O =0 #line:157
        for O0OOOOOOO0O00O0OO in OO00OO00OO00O0OO0 :#line:158
            OOO0O0000OOO00O00 ={}#line:159
            O00O0OO000O0OOO0O =OO00OO00OO00O0OO0 .get (O0OOOOOOO0O00O0OO )[0 ]#line:160
            for O0OO0O0O0OO0OO000 ,O0O0OOOO000OO0OO0 in O00O0OO000O0OOO0O .__dict__ .items ():#line:161
                if O0OO0O0O0OO0OO000 !='__len__'and O0OO0O0O0OO0OO000 !='__wrapped__':#line:162
                    OOO0O0000OOO00O00 [O0OO0O0O0OO0OO000 ]=O0O0OOOO000OO0OO0 #line:163
            OOO0O0000OOO00O00 ['eid']=O00O0000OO000O00O #line:164
            O00O0000OO000O00O +=1 #line:165
            if O0OOOOOOO0O00O0OO =='export_admin_action':#line:166
                OOO0O0000OOO00O00 ['label']='选中导出'#line:167
                OOO0O0000OOO00O00 ['isExport']=True #line:168
                OOO0O0000OOO00O00 ['icon']='el-icon-finished'#line:169
                OO0OO0OOO0OOO00O0 =[]#line:170
                for O0000000O0000000O in enumerate (admin .get_export_formats ()):#line:171
                    OO0OO0OOO0OOO00O0 .append ({'value':O0000000O0000000O [0 ],'label':O0000000O0000000O [1 ]().get_title ()})#line:175
                OOO0O0000OOO00O00 ['formats']=OO0OO0OOO0OOO00O0 #line:177
            else :#line:178
                OOO0O0000OOO00O00 ['label']=OO00OO00OO00O0OO0 .get (O0OOOOOOO0O00O0OO )[2 ]#line:179
            if request .user .has_perm ('{}.{}'.format (OO0O0OOO00OO0O000 ,O0OOOOOOO0O00O0OO )):#line:182
                O00O0OOOOO0O0OOOO [O0OOOOOOO0O00O0OO ]=OOO0O0000OOO00O00 #line:183
    if 'delete_selected'in O00O0OOOOO0O0OOOO :#line:184
        del O00O0OOOOO0O0OOOO ['delete_selected']#line:185
    return O00O0OOOOO0O0OOOO #line:186
def search_placeholder (cl ):#line:189
    O0000O00OOOO00OO0 =get_model_fields (cl .model )#line:191
    for OOO0OO0000OO0OOO0 in cl .model ._meta .fields :#line:193
        if isinstance (OOO0OO0000OO0OOO0 ,ForeignKey ):#line:194
            O0000O00OOOO00OO0 .extend (get_model_fields (OOO0OO0000OO0OOO0 .related_model ,OOO0OO0000OO0OOO0 .name ))#line:195
    O000O0OOOOOOOOOO0 =[]#line:197
    for O0O0O00O0O0O00O0O in cl .search_fields :#line:199
        for OOO0OO0000OO0OOO0 in O0000O00OOOO00OO0 :#line:200
            if OOO0OO0000OO0OOO0 [0 ]==O0O0O00O0O0O00O0O :#line:201
                O000O0OOOOOOOOOO0 .append (OOO0OO0000OO0OOO0 [1 ])#line:202
                break #line:203
    return ",".join (O000O0OOOOOOOOOO0 )#line:205
def write (data ,O0OO00OOO0OOOO000 ='ok',O000000O0OO00O00O =True ):#line:208
    OOOO00O00O0O000O0 ={'state':O000000O0OO00O00O ,'msg':O0OO00OOO0OOOO000 ,'data':data }#line:213
    return HttpResponse (json .dumps (OOOO00O00O0O000O0 ,cls =LazyEncoder ),content_type ='application/json')#line:215
def write_obj (obj ):#line:218
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:219
def has_permission (request ,admin ,permission ):#line:222
    OOO000O00O0O0000O =get_permission_codename (permission ,admin .opts )#line:223
    OO0000O0000O0000O ='{}.{}'.format (admin .opts .app_label ,OOO000O00O0O0000O )#line:224
    return request .user .has_perm (OO0000O0000O0000O )#line:225
def get_permission_codename (action ,opts ):#line:228
    ""#line:231
    return '%s_%s'%(action ,opts .model_name )#line:232
from simpleui .templatetags import simpletags #line:235
from simpleui .templatetags .simpletags import get_config #line:236
def get_menus (request ,admin_site ):#line:239
    ""#line:245
    O000OO0O000000O0O ={'app_list':admin_site .get_app_list (request ),'request':request }#line:249
    def O000OOOO0OOOOOOOO (key ):#line:251
        return request .user .has_perm (key )#line:252
    def _O00O000O000O000OO (key ):#line:254
        if key =='SIMPLEUI_CONFIG':#line:255
            _O0OO0OO00O0OOOO0O =get_config (key )#line:257
            if 'menus'in _O0OO0OO00O0OOOO0O :#line:258
                O0OO00O00O000OO0O =_O0OO0OO00O0OOOO0O .get ('menus')#line:259
                O0OOO0O0O0000O0OO =[]#line:260
                for OOO00O000O0OO0000 in O0OO00O00O000OO0O :#line:262
                    if 'codename'not in OOO00O000O0OO0000 :#line:263
                        O0OOO0O0O0000O0OO .append (OOO00O000O0OO0000 )#line:264
                        continue #line:265
                    O00O0OOOOOO0000O0 =OOO00O000O0OO0000 .get ('codename')#line:266
                    key ='{}.{}'.format (O00O0OOOOOO0000O0 ,O00O0OOOOOO0000O0 )#line:269
                    if O000OOOO0OOOOOOOO (key ):#line:270
                        if 'models'in OOO00O000O0OO0000 :#line:272
                            OOO0OO0O0OOOO0OO0 =OOO00O000O0OO0000 .get ('models')#line:273
                            O00000000O0OO0O0O =[]#line:274
                            for OO00OOO000O00OO0O in OOO0OO0O0OOOO0OO0 :#line:275
                                if 'codename'in OO00OOO000O00OO0O :#line:276
                                    if O000OOOO0OOOOOOOO ('{}.{}'.format (O00O0OOOOOO0000O0 ,OO00OOO000O00OO0O .get ('codename'))):#line:277
                                        O00000000O0OO0O0O .append (OO00OOO000O00OO0O )#line:278
                                else :#line:279
                                    O00000000O0OO0O0O .append (OO00OOO000O00OO0O )#line:280
                            OOO00O000O0OO0000 ['models']=O00000000O0OO0O0O #line:281
                        O0OOO0O0O0000O0OO .append (OOO00O000O0OO0000 )#line:283
                _O0OO0OO00O0OOOO0O ['menus']=O0OOO0O0O0000O0OO #line:284
        return _O0OO0OO00O0OOOO0O #line:286
    return simpletags .menus (O000OO0O000000O0O ,_get_config =_O00O000O000O000OO )#line:288
