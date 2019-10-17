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
def get_model_fields (model ,OO0O000OOO0O00O0O =None ):#line:27
    ""#line:33
    OO0OOOO0O00O0O0OO =[]#line:34
    O0OOOOO00OO0O0O0O =model ._meta .fields #line:35
    for O000OOO00O0OOO000 in O0OOOOO00OO0O0O0O :#line:36
        OOOOOO0OOOO0000OO =O000OOO00O0OOO000 .name #line:37
        if hasattr (O000OOO00O0OOO000 ,'verbose_name'):#line:38
            OOOOOO0OOOO0000OO =getattr (O000OOO00O0OOO000 ,'verbose_name')#line:39
        if isinstance (OOOOOO0OOOO0000OO ,Promise ):#line:41
            OOOOOO0OOOO0000OO =str (OOOOOO0OOOO0000OO )#line:42
        if OO0O000OOO0O00O0O :#line:44
            OO0OOOO0O00O0O0OO .append (('{}__{}'.format (OO0O000OOO0O00O0O ,O000OOO00O0OOO000 .name ),OOOOOO0OOOO0000OO ))#line:45
        else :#line:46
            OO0OOOO0O00O0O0OO .append ((O000OOO00O0OOO000 .name ,OOOOOO0OOOO0000OO ))#line:47
    return OO0OOOO0O00O0O0OO #line:49
def find_field (fields ,name ):#line:52
    for O00O0O0O00OO00OOO in fields :#line:53
        if name ==O00O0O0O00OO00OOO [0 ]:#line:54
            return O00O0O0O00OO00OOO [1 ]#line:55
    return False #line:56
MODEL_CACHE ={}#line:60
def get_model_info (model_admin ,request ):#line:63
    O0O000O00OOO0OO0O =str (model_admin )#line:67
    if O0O000O00OOO0OO0O in MODEL_CACHE :#line:68
        O0O000OO0000O0000 =MODEL_CACHE .get (O0O000O00OOO0OO0O )#line:69
        return O0O000OO0000O0000 .get ('values_fields'),O0O000OO0000O0000 .get ('fun_fields'),O0O000OO0000O0000 .get ('headers'),O0O000OO0000O0000 .get ('formatter'),O0O000OO0000O0000 .get ('choices')#line:71
    O00O0OO0OOO0OO0OO =get_model_fields (model_admin .model )#line:72
    O0000O0OOO0O000OO =model_admin .get_list_display (request )#line:74
    OO000O0OO000O00OO =[]#line:75
    OO000OOO000OO000O =[]#line:76
    OO00OOOOO0O0OOOO0 =[]#line:77
    O0OOOO0O000O0OOO0 ={}#line:80
    if hasattr (model_admin ,'fields_options'):#line:81
        O0OOOO0O000O0OOO0 =getattr (model_admin ,'fields_options')#line:82
    for OO0OO0OOO0O0OO00O in O0000O0OOO0O000OO :#line:84
        OO0O00OOO0O00OOOO =find_field (O00O0OO0OOO0OO0OO ,OO0OO0OOO0O0OO00O )#line:85
        if OO0O00OOO0O00OOOO :#line:86
            OO000OOO000OO000O .append (OO0OO0OOO0O0OO00O )#line:87
            O0O0000O0O0OOOOOO ={'name':OO0OO0OOO0O0OO00O ,'label':OO0O00OOO0O00OOOO }#line:91
            if OO0OO0OOO0O0OO00O in O0OOOO0O000O0OOO0 :#line:92
                O0O0000O0O0OOOOOO =dict (O0O0000O0O0OOOOOO ,**O0OOOO0O000O0OOO0 .get (OO0OO0OOO0O0OO00O ))#line:93
            if 'sortable'not in O0O0000O0O0OOOOOO :#line:95
                O0O0000O0O0OOOOOO ['sortable']='custom'#line:97
            OO00OOOOO0O0OOOO0 .append (O0O0000O0O0OOOOOO )#line:98
        else :#line:99
            OO000O0OO000O00OO .append (OO0OO0OOO0O0OO00O )#line:100
            OO0O00OOO0O00OOOO =OO0OO0OOO0O0OO00O #line:101
            if hasattr (model_admin ,OO0OO0OOO0O0OO00O ):#line:102
                OOO0000OOO0O00OOO =getattr (model_admin ,OO0OO0OOO0O0OO00O ).__dict__ #line:103
            else :#line:104
                OOO0000OOO0O00OOO =getattr (model_admin .model ,OO0OO0OOO0O0OO00O ).__dict__ #line:105
            if 'short_description'in OOO0000OOO0O00OOO :#line:106
                OO0O00OOO0O00OOOO =OOO0000OOO0O00OOO .get ('short_description')#line:107
            elif OO0O00OOO0O00OOOO =='__str__':#line:108
                OO0O00OOO0O00OOOO =model_admin .model ._meta .verbose_name_plural #line:109
            O0O0000O0O0OOOOOO ={'name':OO0OO0OOO0O0OO00O ,'label':OO0O00OOO0O00OOOO }#line:113
            if OO0OO0OOO0O0OO00O in O0OOOO0O000O0OOO0 :#line:114
                O0O0000O0O0OOOOOO =dict (O0O0000O0O0OOOOOO ,**O0OOOO0O000O0OOO0 .get (OO0OO0OOO0O0OO00O ))#line:115
            O0O0000O0O0OOOOOO ['sortable']=False #line:117
            OO00OOOOO0O0OOOO0 .append (O0O0000O0O0OOOOOO )#line:118
    O00O0OO0O0O0OOOO0 =None #line:120
    if hasattr (model_admin ,'formatter'):#line:121
        O00O0OO0O0O0OOOO0 =getattr (model_admin ,'formatter')#line:122
    OO0O0O000000O00O0 =model_admin .model #line:125
    OO00OOOO000OOO0O0 ={}#line:126
    for O0OOO0O0O0O000000 in dir (OO0O0O000000O00O0 ):#line:127
        if O0OOO0O0O0O000000 .endswith ('choices'):#line:128
            OOO0O0OO0OO0OOO0O ={}#line:129
            O0O0O0OO000OOO000 =getattr (OO0O0O000000O00O0 ,O0OOO0O0O0O000000 )#line:130
            for OO0OO0OOO0O0OO00O in O0O0O0OO000OOO000 :#line:131
                OOO0O0OO0OO0OOO0O [OO0OO0OOO0O0OO00O [0 ]]=OO0OO0OOO0O0OO00O [1 ]#line:132
            OO00OOOO000OOO0O0 [O0OOO0O0O0O000000 ]=OOO0O0OO0OO0OOO0O #line:133
    for O0OOO0O0O0O000000 in OO0O0O000000O00O0 ._meta .fields :#line:134
        OOO0O0OO0OO0OOO0O ={}#line:135
        if hasattr (O0OOO0O0O0O000000 ,'choices'):#line:136
            if len (O0OOO0O0O0O000000 .choices )>0 :#line:137
                for OO0OO0OOO0O0OO00O in O0OOO0O0O0O000000 .choices :#line:138
                    OOO0O0OO0OO0OOO0O [OO0OO0OOO0O0OO00O [0 ]]=OO0OO0OOO0O0OO00O [1 ]#line:139
                OO00OOOO000OOO0O0 [O0OOO0O0O0O000000 .name ]=OOO0O0OO0OO0OOO0O #line:140
    MODEL_CACHE [O0O000O00OOO0OO0O ]={'values_fields':OO000OOO000OO000O ,'fun_fields':OO000O0OO000O00OO ,'headers':OO00OOOOO0O0OOOO0 ,'formatter':O00O0OO0O0O0OOOO0 ,'choices':OO00OOOO000OOO0O0 ,}#line:147
    return OO000OOO000OO000O ,OO000O0OO000O00OO ,OO00OOOOO0O0OOOO0 ,O00O0OO0O0O0OOOO0 ,OO00OOOO000OOO0O0 #line:148
def get_custom_button (request ,admin ):#line:151
    O00OOOO0OOOOO000O ={}#line:152
    O00000O000O0000OO =admin .get_actions (request )#line:153
    O0O0O0000O0O0O0O0 =admin .opts .app_label #line:158
    if O00000O000O0000OO :#line:159
        OO0O00OO00OOOOO0O =0 #line:160
        for OO0O000O0000O0O00 in O00000O000O0000OO :#line:161
            O000OO0OOO0OO00O0 ={}#line:162
            O00OOOOOO0O00O0OO =O00000O000O0000OO .get (OO0O000O0000O0O00 )[0 ]#line:163
            for OO0O0O0O00O0O00OO ,OOOO0OOO00OOO00O0 in O00OOOOOO0O00O0OO .__dict__ .items ():#line:164
                if OO0O0O0O00O0O00OO !='__len__'and OO0O0O0O00O0O00OO !='__wrapped__':#line:165
                    O000OO0OOO0OO00O0 [OO0O0O0O00O0O00OO ]=OOOO0OOO00OOO00O0 #line:166
            O000OO0OOO0OO00O0 ['eid']=OO0O00OO00OOOOO0O #line:167
            OO0O00OO00OOOOO0O +=1 #line:168
            if OO0O000O0000O0O00 =='export_admin_action':#line:169
                O000OO0OOO0OO00O0 ['label']='选中导出'#line:170
                O000OO0OOO0OO00O0 ['isExport']=True #line:171
                O000OO0OOO0OO00O0 ['icon']='el-icon-finished'#line:172
                OO0OOOO00O000OOO0 =[]#line:173
                for OOOO00O0OOOO0OO0O in enumerate (admin .get_export_formats ()):#line:174
                    OO0OOOO00O000OOO0 .append ({'value':OOOO00O0OOOO0OO0O [0 ],'label':OOOO00O0OOOO0OO0O [1 ]().get_title ()})#line:178
                O000OO0OOO0OO00O0 ['formats']=OO0OOOO00O000OOO0 #line:180
            else :#line:181
                O000OO0OOO0OO00O0 ['label']=O00000O000O0000OO .get (OO0O000O0000O0O00 )[2 ]#line:182
            if request .user .has_perm ('{}.{}'.format (O0O0O0000O0O0O0O0 ,OO0O000O0000O0O00 )):#line:185
                O00OOOO0OOOOO000O [OO0O000O0000O0O00 ]=O000OO0OOO0OO00O0 #line:186
    if 'delete_selected'in O00OOOO0OOOOO000O :#line:187
        del O00OOOO0OOOOO000O ['delete_selected']#line:188
    return O00OOOO0OOOOO000O #line:189
def search_placeholder (cl ):#line:192
    OO0O0O0O000000O0O =get_model_fields (cl .model )#line:194
    for O0000OO0O0O000O00 in cl .model ._meta .fields :#line:196
        if isinstance (O0000OO0O0O000O00 ,ForeignKey ):#line:197
            OO0O0O0O000000O0O .extend (get_model_fields (O0000OO0O0O000O00 .related_model ,O0000OO0O0O000O00 .name ))#line:198
    OOO000O0O00O0O000 =[]#line:200
    for O0O0O00O0O000O00O in cl .search_fields :#line:202
        for O0000OO0O0O000O00 in OO0O0O0O000000O0O :#line:203
            if O0000OO0O0O000O00 [0 ]==O0O0O00O0O000O00O :#line:204
                OOO000O0O00O0O000 .append (O0000OO0O0O000O00 [1 ])#line:205
                break #line:206
    return ",".join (OOO000O0O00O0O000 )#line:208
def write (data ,OOOO0OOO0OO0O0OO0 ='ok',OO00000O000O0000O =True ):#line:211
    O0O000O00000OO0O0 ={'state':OO00000O000O0000O ,'msg':OOOO0OOO0OO0O0OO0 ,'data':data }#line:216
    return HttpResponse (json .dumps (O0O000O00000OO0O0 ,cls =LazyEncoder ),content_type ='application/json')#line:218
def write_obj (obj ):#line:221
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:222
def has_permission (request ,admin ,permission ):#line:225
    O00000OOO0OO0O0OO =get_permission_codename (permission ,admin .opts )#line:226
    OO00O000O00OO00OO ='{}.{}'.format (admin .opts .app_label ,O00000OOO0OO0O0OO )#line:227
    return request .user .has_perm (OO00O000O00OO00OO )#line:228
def get_permission_codename (action ,opts ):#line:231
    ""#line:234
    return '%s_%s'%(action ,opts .model_name )#line:235
from simpleui .templatetags import simpletags #line:238
from simpleui .templatetags .simpletags import get_config #line:239
def get_menus (request ,admin_site ):#line:242
    ""#line:248
    O000O0OO0O0OO0O0O ={'app_list':admin_site .get_app_list (request ),'request':request }#line:252
    def OOO00O0O0OO00000O (key ):#line:254
        return request .user .has_perm (key )#line:255
    def _O0OOOOO00OO0OO0OO (key ):#line:257
        if key =='SIMPLEUI_CONFIG':#line:258
            _OOO0OO000OO000000 =get_config (key )#line:260
            if 'menus'in _OOO0OO000OO000000 :#line:261
                OO00OO00OO000O00O =_OOO0OO000OO000000 .get ('menus')#line:262
                OO00O00O0O0OO0OOO =[]#line:263
                for OOOOOO00O0O00O0O0 in OO00OO00OO000O00O :#line:265
                    if 'codename'not in OOOOOO00O0O00O0O0 :#line:266
                        OO00O00O0O0OO0OOO .append (OOOOOO00O0O00O0O0 )#line:267
                        continue #line:268
                    OO00O0O0OOOO00O00 =OOOOOO00O0O00O0O0 .get ('codename')#line:269
                    key ='{}.{}'.format (OO00O0O0OOOO00O00 ,OO00O0O0OOOO00O00 )#line:272
                    if OOO00O0O0OO00000O (key ):#line:273
                        if 'models'in OOOOOO00O0O00O0O0 :#line:275
                            O00O00O00OO0000OO =OOOOOO00O0O00O0O0 .get ('models')#line:276
                            O000O00000000OO0O =[]#line:277
                            for O00000OOOO0O00O00 in O00O00O00OO0000OO :#line:278
                                if 'codename'in O00000OOOO0O00O00 :#line:279
                                    if OOO00O0O0OO00000O ('{}.{}'.format (OO00O0O0OOOO00O00 ,O00000OOOO0O00O00 .get ('codename'))):#line:280
                                        O000O00000000OO0O .append (O00000OOOO0O00O00 )#line:281
                                else :#line:282
                                    O000O00000000OO0O .append (O00000OOOO0O00O00 )#line:283
                            OOOOOO00O0O00O0O0 ['models']=O000O00000000OO0O #line:284
                        OO00O00O0O0OO0OOO .append (OOOOOO00O0O00O0O0 )#line:286
                _OOO0OO000OO000000 ['menus']=OO00O00O0O0OO0OOO #line:287
        return _OOO0OO000OO000000 #line:289
    return simpletags .menus (O000O0OO0O0OO0O0O ,_get_config =_O0OOOOO00OO0OO0OO )#line:291
