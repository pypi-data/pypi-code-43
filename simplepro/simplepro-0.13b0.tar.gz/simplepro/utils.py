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
def get_model_fields (model ,O000OO0O0OOOO0O0O =None ):#line:28
    ""#line:34
    O000OOO0000O00000 =[]#line:35
    OOO0OO0O00O0000O0 =model ._meta .fields #line:36
    for OO00O0O00OO00O00O in OOO0OO0O00O0000O0 :#line:37
        OOO00O0O00O0OOO00 =OO00O0O00OO00O00O .name #line:38
        if hasattr (OO00O0O00OO00O00O ,'verbose_name'):#line:39
            OOO00O0O00O0OOO00 =getattr (OO00O0O00OO00O00O ,'verbose_name')#line:40
        if isinstance (OOO00O0O00O0OOO00 ,Promise ):#line:42
            OOO00O0O00O0OOO00 =str (OOO00O0O00O0OOO00 )#line:43
        if O000OO0O0OOOO0O0O :#line:45
            O000OOO0000O00000 .append (('{}__{}'.format (O000OO0O0OOOO0O0O ,OO00O0O00OO00O00O .name ),OOO00O0O00O0OOO00 ))#line:46
        else :#line:47
            O000OOO0000O00000 .append ((OO00O0O00OO00O00O .name ,OOO00O0O00O0OOO00 ))#line:48
    return O000OOO0000O00000 #line:50
def find_field (fields ,name ):#line:53
    for O0OO00OO0OOO0OOOO in fields :#line:54
        if name ==O0OO00OO0OOO0OOOO [0 ]:#line:55
            return O0OO00OO0OOO0OOOO [1 ]#line:56
    return False #line:57
MODEL_CACHE ={}#line:61
def get_model_info (model_admin ,request ):#line:64
    OO0O0O00OOO0OO0OO =str (model_admin )#line:68
    if OO0O0O00OOO0OO0OO in MODEL_CACHE :#line:69
        OO00OOOOOOO00000O =MODEL_CACHE .get (OO0O0O00OOO0OO0OO )#line:70
        return OO00OOOOOOO00000O .get ('values_fields'),OO00OOOOOOO00000O .get ('fun_fields'),OO00OOOOOOO00000O .get ('headers'),OO00OOOOOOO00000O .get ('formatter'),OO00OOOOOOO00000O .get ('choices')#line:72
    O0O00OOOOOOOOO0OO =get_model_fields (model_admin .model )#line:73
    O00OO000000000OO0 =model_admin .get_list_display (request )#line:75
    OO000OO00O0OO0OO0 =[]#line:76
    OO0OOOO000OOO0OOO =[]#line:77
    OO0OO00OOO0O0OOO0 =[]#line:78
    OO0O00O0O0000O00O ={}#line:81
    if hasattr (model_admin ,'fields_options'):#line:82
        OO0O00O0O0000O00O =getattr (model_admin ,'fields_options')#line:83
    for OO00000OO00000O0O in O00OO000000000OO0 :#line:85
        OOO0O0O000O0O0O0O =find_field (O0O00OOOOOOOOO0OO ,OO00000OO00000O0O )#line:86
        if OOO0O0O000O0O0O0O :#line:87
            OO0OOOO000OOO0OOO .append (OO00000OO00000O0O )#line:88
            O0OOO00O0O00O0OO0 ={'name':OO00000OO00000O0O ,'label':OOO0O0O000O0O0O0O }#line:92
            if OO00000OO00000O0O in OO0O00O0O0000O00O :#line:93
                O0OOO00O0O00O0OO0 =dict (O0OOO00O0O00O0OO0 ,**OO0O00O0O0000O00O .get (OO00000OO00000O0O ))#line:94
            if 'sortable'not in O0OOO00O0O00O0OO0 :#line:96
                O0OOO00O0O00O0OO0 ['sortable']='custom'#line:98
            OO0OO00OOO0O0OOO0 .append (O0OOO00O0O00O0OO0 )#line:99
        else :#line:100
            OO000OO00O0OO0OO0 .append (OO00000OO00000O0O )#line:101
            OOO0O0O000O0O0O0O =OO00000OO00000O0O #line:102
            if hasattr (model_admin ,OO00000OO00000O0O ):#line:103
                OO0OOOOOO00O0000O =getattr (model_admin ,OO00000OO00000O0O ).__dict__ #line:104
            else :#line:105
                OO0OOOOOO00O0000O =getattr (model_admin .model ,OO00000OO00000O0O ).__dict__ #line:106
            if 'short_description'in OO0OOOOOO00O0000O :#line:107
                OOO0O0O000O0O0O0O =OO0OOOOOO00O0000O .get ('short_description')#line:108
            elif OOO0O0O000O0O0O0O =='__str__':#line:109
                OOO0O0O000O0O0O0O =model_admin .model ._meta .verbose_name_plural #line:110
            O0OOO00O0O00O0OO0 ={'name':OO00000OO00000O0O ,'label':OOO0O0O000O0O0O0O }#line:114
            if OO00000OO00000O0O in OO0O00O0O0000O00O :#line:115
                O0OOO00O0O00O0OO0 =dict (O0OOO00O0O00O0OO0 ,**OO0O00O0O0000O00O .get (OO00000OO00000O0O ))#line:116
            O0OOO00O0O00O0OO0 ['sortable']=False #line:118
            OO0OO00OOO0O0OOO0 .append (O0OOO00O0O00O0OO0 )#line:119
    O0O00OO000O00O0OO =None #line:121
    if hasattr (model_admin ,'formatter'):#line:122
        O0O00OO000O00O0OO =getattr (model_admin ,'formatter')#line:123
    OO00O000O0OO00OOO =model_admin .model #line:126
    OOO0O0OOOO00OOO0O ={}#line:127
    for OOO0OOOO0O00O0OO0 in dir (OO00O000O0OO00OOO ):#line:128
        if OOO0OOOO0O00O0OO0 .endswith ('choices'):#line:129
            O00000OO0OO000OOO ={}#line:130
            O0OO0O00OO0O0000O =getattr (OO00O000O0OO00OOO ,OOO0OOOO0O00O0OO0 )#line:131
            for OO00000OO00000O0O in O0OO0O00OO0O0000O :#line:132
                O00000OO0OO000OOO [OO00000OO00000O0O [0 ]]=OO00000OO00000O0O [1 ]#line:133
            OOO0O0OOOO00OOO0O [OOO0OOOO0O00O0OO0 ]=O00000OO0OO000OOO #line:134
    for OOO0OOOO0O00O0OO0 in OO00O000O0OO00OOO ._meta .fields :#line:135
        O00000OO0OO000OOO ={}#line:136
        if hasattr (OOO0OOOO0O00O0OO0 ,'choices'):#line:137
            if len (OOO0OOOO0O00O0OO0 .choices )>0 :#line:138
                for OO00000OO00000O0O in OOO0OOOO0O00O0OO0 .choices :#line:139
                    O00000OO0OO000OOO [OO00000OO00000O0O [0 ]]=OO00000OO00000O0O [1 ]#line:140
                OOO0O0OOOO00OOO0O [OOO0OOOO0O00O0OO0 .name ]=O00000OO0OO000OOO #line:141
    MODEL_CACHE [OO0O0O00OOO0OO0OO ]={'values_fields':OO0OOOO000OOO0OOO ,'fun_fields':OO000OO00O0OO0OO0 ,'headers':OO0OO00OOO0O0OOO0 ,'formatter':O0O00OO000O00O0OO ,'choices':OOO0O0OOOO00OOO0O ,}#line:148
    return OO0OOOO000OOO0OOO ,OO000OO00O0OO0OO0 ,OO0OO00OOO0O0OOO0 ,O0O00OO000O00O0OO ,OOO0O0OOOO00OOO0O #line:149
def get_custom_button (request ,admin ):#line:152
    O000O000OOOO00O00 ={}#line:153
    O0OO000OO0O00O0OO =admin .get_actions (request )#line:154
    O0O00O0O0OOOOOO00 =admin .opts .app_label #line:159
    if O0OO000OO0O00O0OO :#line:160
        O0OOO000O000000OO =0 #line:161
        for O00OO0O0O0O00O000 in O0OO000OO0O00O0OO :#line:162
            O00OOO0O00O0OO0OO ={}#line:163
            OO00OO0000000OO0O =O0OO000OO0O00O0OO .get (O00OO0O0O0O00O000 )[0 ]#line:164
            for OOOOOOO00O0000OO0 ,O0O00OOO0000OO0OO in OO00OO0000000OO0O .__dict__ .items ():#line:165
                if OOOOOOO00O0000OO0 !='__len__'and OOOOOOO00O0000OO0 !='__wrapped__':#line:166
                    O00OOO0O00O0OO0OO [OOOOOOO00O0000OO0 ]=O0O00OOO0000OO0OO #line:167
            O00OOO0O00O0OO0OO ['eid']=O0OOO000O000000OO #line:168
            O0OOO000O000000OO +=1 #line:169
            if O00OO0O0O0O00O000 =='export_admin_action':#line:170
                O00OOO0O00O0OO0OO ['label']='选中导出'#line:171
                O00OOO0O00O0OO0OO ['isExport']=True #line:172
                O00OOO0O00O0OO0OO ['icon']='el-icon-finished'#line:173
                O0OOO00OO0O00OOOO =[]#line:174
                for O00O0OO0OO000OOO0 in enumerate (admin .get_export_formats ()):#line:175
                    O0OOO00OO0O00OOOO .append ({'value':O00O0OO0OO000OOO0 [0 ],'label':O00O0OO0OO000OOO0 [1 ]().get_title ()})#line:179
                O00OOO0O00O0OO0OO ['formats']=O0OOO00OO0O00OOOO #line:181
            else :#line:182
                O00OOO0O00O0OO0OO ['label']=O0OO000OO0O00O0OO .get (O00OO0O0O0O00O000 )[2 ]#line:183
            if request .user .has_perm ('{}.{}'.format (O0O00O0O0OOOOOO00 ,O00OO0O0O0O00O000 )):#line:186
                O000O000OOOO00O00 [O00OO0O0O0O00O000 ]=O00OOO0O00O0OO0OO #line:187
    if 'delete_selected'in O000O000OOOO00O00 :#line:188
        del O000O000OOOO00O00 ['delete_selected']#line:189
    return O000O000OOOO00O00 #line:190
def search_placeholder (cl ):#line:193
    OOO0OO000OOO0000O =get_model_fields (cl .model )#line:195
    for O0O000O00O0O0OOO0 in cl .model ._meta .fields :#line:197
        if isinstance (O0O000O00O0O0OOO0 ,ForeignKey ):#line:198
            OOO0OO000OOO0000O .extend (get_model_fields (O0O000O00O0O0OOO0 .related_model ,O0O000O00O0O0OOO0 .name ))#line:199
    O00OO00000OO00O00 =[]#line:201
    for OO0O0O00O00OO0000 in cl .search_fields :#line:203
        for O0O000O00O0O0OOO0 in OOO0OO000OOO0000O :#line:204
            if O0O000O00O0O0OOO0 [0 ]==OO0O0O00O00OO0000 :#line:205
                O00OO00000OO00O00 .append (O0O000O00O0O0OOO0 [1 ])#line:206
                break #line:207
    return ",".join (O00OO00000OO00O00 )#line:209
def write (data ,O0OO0O0O0OO00O000 ='ok',OO0OO00O0OOOO0O0O =True ):#line:212
    O0OOO0OOOO0O0O0O0 ={'state':OO0OO00O0OOOO0O0O ,'msg':O0OO0O0O0OO00O000 ,'data':data }#line:217
    return HttpResponse (json .dumps (O0OOO0OOOO0O0O0O0 ,cls =LazyEncoder ),content_type ='application/json')#line:219
def write_obj (obj ):#line:222
    return HttpResponse (json .dumps (obj ,cls =LazyEncoder ),content_type ='application/json')#line:223
def has_permission (request ,admin ,permission ):#line:226
    O0OOO0OO0O00O0000 =get_permission_codename (permission ,admin .opts )#line:227
    O000O00O00OO00O00 ='{}.{}'.format (admin .opts .app_label ,O0OOO0OO0O00O0000 )#line:228
    return request .user .has_perm (O000O00O00OO00O00 )#line:229
def get_permission_codename (action ,opts ):#line:232
    ""#line:235
    return '%s_%s'%(action ,opts .model_name )#line:236
from simpleui .templatetags import simpletags #line:239
from simpleui .templatetags .simpletags import get_config #line:240
def get_menus (request ,admin_site ):#line:243
    ""#line:249
    OOO0000OOO000OOO0 ={'app_list':admin_site .get_app_list (request ),'request':request }#line:253
    def OO000O0OO00OOOO00 (key ):#line:255
        return request .user .has_perm (key )#line:256
    def _OOO00OO0OO0OO0OOO (key ):#line:258
        if key =='SIMPLEUI_CONFIG':#line:259
            _O0O0OOOO00O0OOOOO =get_config (key )#line:261
            if _O0O0OOOO00O0OOOOO and 'menus'in _O0O0OOOO00O0OOOOO :#line:262
                OO0O00OO00000O0OO =_O0O0OOOO00O0OOOOO .get ('menus')#line:263
                OO00OO0O00OO0OO00 =[]#line:264
                for OO00OO0OOOO0OOO0O in OO0O00OO00000O0OO :#line:266
                    if 'codename'not in OO00OO0OOOO0OOO0O :#line:267
                        OO00OO0O00OO0OO00 .append (OO00OO0OOOO0OOO0O )#line:268
                        continue #line:269
                    O0OOO00O00000000O =OO00OO0OOOO0OOO0O .get ('codename')#line:270
                    key ='{}.{}'.format (O0OOO00O00000000O ,O0OOO00O00000000O )#line:273
                    if OO000O0OO00OOOO00 (key ):#line:274
                        if 'models'in OO00OO0OOOO0OOO0O :#line:276
                            O00OOO0000O00O00O =OO00OO0OOOO0OOO0O .get ('models')#line:277
                            OO00OO000OOO0O0OO =[]#line:278
                            for OOOOOO00O000OOOOO in O00OOO0000O00O00O :#line:279
                                if 'codename'in OOOOOO00O000OOOOO :#line:280
                                    if OO000O0OO00OOOO00 ('{}.{}'.format (O0OOO00O00000000O ,OOOOOO00O000OOOOO .get ('codename'))):#line:281
                                        OO00OO000OOO0O0OO .append (OOOOOO00O000OOOOO )#line:282
                                else :#line:283
                                    OO00OO000OOO0O0OO .append (OOOOOO00O000OOOOO )#line:284
                            OO00OO0OOOO0OOO0O ['models']=OO00OO000OOO0O0OO #line:285
                        OO00OO0O00OO0OO00 .append (OO00OO0OOOO0OOO0O )#line:287
                _O0O0OOOO00O0OOOOO ['menus']=OO00OO0O00OO0OO00 #line:288
        return _O0O0OOOO00O0OOOOO #line:290
    return simpletags .menus (OOO0000OOO000OOO0 ,_get_config =_OOO00OO0OO0OO0OOO )#line:292
