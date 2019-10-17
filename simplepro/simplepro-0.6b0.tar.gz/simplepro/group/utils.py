from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O0O0O00OO0O000O0O =Permission .objects .all ()#line:20
    OO0OOOOO0OOO0O0OO ={}#line:23
    for O00O000O0O000O000 in O0O0O00OO0O000O0O :#line:25
        OO000O0O0OO0OO000 =O00O000O0O000O000 .content_type .app_label #line:26
        if OO000O0O0OO0OO000 not in OO0OOOOO0OOO0O0OO :#line:27
            OO0OOOOO0OOO0O0OO [OO000O0O0OO0OO000 ]={'label':OO000O0O0OO0OO000 ,'children':[O00O000O0O000O000 ]}#line:31
        else :#line:32
            O0OOO0000O00OOO00 =OO0OOOOO0OOO0O0OO .get (OO000O0O0OO0OO000 )#line:33
            OOO00O000000OO0O0 =O0OOO0000O00OOO00 .get ('children')#line:34
            OOO00O000000OO0O0 .append (O00O000O0O000O000 )#line:35
    for OO00OO0000O000000 in OO0OOOOO0OOO0O0OO :#line:40
        O00O000O0O000O000 =OO0OOOOO0OOO0O0OO .get (OO00OO0000O000000 )#line:41
        OOO00O000000OO0O0 =O00O000O0O000O000 .get ('children')#line:42
        OO0O0O0OO0O000O0O ={}#line:45
        for OO0OO00OO00O0OO0O in OOO00O000000OO0O0 :#line:46
            OO000O0O0OO0OO000 =OO0OO00OO00O0OO0O .content_type .name #line:48
            if OO000O0O0OO0OO000 not in OO0O0O0OO0O000O0O :#line:49
                OO0O0O0OO0O000O0O [OO000O0O0OO0OO000 ]={'label':OO000O0O0OO0OO000 ,'children':[{'id':OO0OO00OO00O0OO0O .id ,'label':get_action_name (OO0OO00OO00O0OO0O .name )}]}#line:56
            else :#line:57
                OO0O0O0OO0O000O0O [OO000O0O0OO0OO000 ].get ('children').append ({'id':OO0OO00OO00O0OO0O .id ,'label':get_action_name (OO0OO00OO00O0OO0O .name )})#line:61
        O0000OOOOO000OOOO =[]#line:62
        for OO0OO00OO00O0OO0O in OO0O0O0OO0O000O0O :#line:63
            O0000OOOOO000OOOO .append (OO0O0O0OO0O000O0O .get (OO0OO00OO00O0OO0O ))#line:64
        O00O000O0O000O000 ['children']=O0000OOOOO000OOOO #line:65
    O0OO0O0O0O0OOOOOO =[]#line:67
    for OO0OO00OO00O0OO0O in OO0OOOOO0OOO0O0OO :#line:68
        O0OO0O0O0O0OOOOOO .append (OO0OOOOO0OOO0O0OO .get (OO0OO00OO00O0OO0O ))#line:69
    return O0OO0O0O0O0OOOOOO #line:71
