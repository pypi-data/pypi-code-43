from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O0OO000OO0OO00OO0 =Permission .objects .all ()#line:20
    OOO0OOO0O0OO0O0OO ={}#line:23
    for O0OOO0O0OO0O0000O in O0OO000OO0OO00OO0 :#line:25
        OOO0O000O0OO0OO00 =O0OOO0O0OO0O0000O .content_type .app_label #line:26
        if OOO0O000O0OO0OO00 not in OOO0OOO0O0OO0O0OO :#line:27
            OOO0OOO0O0OO0O0OO [OOO0O000O0OO0OO00 ]={'label':OOO0O000O0OO0OO00 ,'children':[O0OOO0O0OO0O0000O ]}#line:31
        else :#line:32
            OOOO0OOOOOOO000O0 =OOO0OOO0O0OO0O0OO .get (OOO0O000O0OO0OO00 )#line:33
            O00O0O0O000O0000O =OOOO0OOOOOOO000O0 .get ('children')#line:34
            O00O0O0O000O0000O .append (O0OOO0O0OO0O0000O )#line:35
    for O0O0000OOOOO0OO0O in OOO0OOO0O0OO0O0OO :#line:40
        O0OOO0O0OO0O0000O =OOO0OOO0O0OO0O0OO .get (O0O0000OOOOO0OO0O )#line:41
        O00O0O0O000O0000O =O0OOO0O0OO0O0000O .get ('children')#line:42
        OO0000O00OOO0OOOO ={}#line:45
        for OO00OOOO000OOO0O0 in O00O0O0O000O0000O :#line:46
            OOO0O000O0OO0OO00 =OO00OOOO000OOO0O0 .content_type .name #line:48
            if OOO0O000O0OO0OO00 not in OO0000O00OOO0OOOO :#line:49
                OO0000O00OOO0OOOO [OOO0O000O0OO0OO00 ]={'label':OOO0O000O0OO0OO00 ,'children':[{'id':OO00OOOO000OOO0O0 .id ,'label':get_action_name (OO00OOOO000OOO0O0 .name )}]}#line:56
            else :#line:57
                OO0000O00OOO0OOOO [OOO0O000O0OO0OO00 ].get ('children').append ({'id':OO00OOOO000OOO0O0 .id ,'label':get_action_name (OO00OOOO000OOO0O0 .name )})#line:61
        OOO0OOO00OOO0O000 =[]#line:62
        for OO00OOOO000OOO0O0 in OO0000O00OOO0OOOO :#line:63
            OOO0OOO00OOO0O000 .append (OO0000O00OOO0OOOO .get (OO00OOOO000OOO0O0 ))#line:64
        O0OOO0O0OO0O0000O ['children']=OOO0OOO00OOO0O000 #line:65
    OO00O000O0O00000O =[]#line:67
    for OO00OOOO000OOO0O0 in OOO0OOO0O0OO0O0OO :#line:68
        OO00O000O0O00000O .append (OOO0OOO0O0OO0O0OO .get (OO00OOOO000OOO0O0 ))#line:69
    return OO00O000O0O00000O #line:71
