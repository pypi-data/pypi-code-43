from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O00000O00OO00O0O0 =Permission .objects .all ()#line:20
    O000OOO00OOOOOOOO ={}#line:23
    for OOOOOO0OO00OOOOOO in O00000O00OO00O0O0 :#line:25
        OOO000O00OO0000OO =OOOOOO0OO00OOOOOO .content_type .app_label #line:26
        if OOO000O00OO0000OO not in O000OOO00OOOOOOOO :#line:27
            O000OOO00OOOOOOOO [OOO000O00OO0000OO ]={'label':OOO000O00OO0000OO ,'children':[OOOOOO0OO00OOOOOO ]}#line:31
        else :#line:32
            OO00O00000000O0OO =O000OOO00OOOOOOOO .get (OOO000O00OO0000OO )#line:33
            O0OOOO0000O00O000 =OO00O00000000O0OO .get ('children')#line:34
            O0OOOO0000O00O000 .append (OOOOOO0OO00OOOOOO )#line:35
    for OO0OO00O0O00OOO00 in O000OOO00OOOOOOOO :#line:40
        OOOOOO0OO00OOOOOO =O000OOO00OOOOOOOO .get (OO0OO00O0O00OOO00 )#line:41
        O0OOOO0000O00O000 =OOOOOO0OO00OOOOOO .get ('children')#line:42
        O0000O0000OOO0000 ={}#line:45
        for O0O0OOOOOO000OO0O in O0OOOO0000O00O000 :#line:46
            OOO000O00OO0000OO =O0O0OOOOOO000OO0O .content_type .name #line:48
            if OOO000O00OO0000OO not in O0000O0000OOO0000 :#line:49
                O0000O0000OOO0000 [OOO000O00OO0000OO ]={'label':OOO000O00OO0000OO ,'children':[{'id':O0O0OOOOOO000OO0O .id ,'label':get_action_name (O0O0OOOOOO000OO0O .name )}]}#line:56
            else :#line:57
                O0000O0000OOO0000 [OOO000O00OO0000OO ].get ('children').append ({'id':O0O0OOOOOO000OO0O .id ,'label':get_action_name (O0O0OOOOOO000OO0O .name )})#line:61
        OOO0O00O000OOOO00 =[]#line:62
        for O0O0OOOOOO000OO0O in O0000O0000OOO0000 :#line:63
            OOO0O00O000OOOO00 .append (O0000O0000OOO0000 .get (O0O0OOOOOO000OO0O ))#line:64
        OOOOOO0OO00OOOOOO ['children']=OOO0O00O000OOOO00 #line:65
    OOO0OOO0OO0O000OO =[]#line:67
    for O0O0OOOOOO000OO0O in O000OOO00OOOOOOOO :#line:68
        OOO0OOO0OO0O000OO .append (O000OOO00OOOOOOOO .get (O0O0OOOOOO000OO0O ))#line:69
    return OOO0OOO0OO0O000OO #line:71
