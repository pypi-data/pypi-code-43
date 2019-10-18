from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O00O0OO0OO0OO00O0 =Permission .objects .all ()#line:20
    OO00000000OOO0O00 ={}#line:23
    for O000O000OO0O0O0OO in O00O0OO0OO0OO00O0 :#line:25
        O00OO0OO00000OO00 =O000O000OO0O0O0OO .content_type .app_label #line:26
        if O00OO0OO00000OO00 not in OO00000000OOO0O00 :#line:27
            OO00000000OOO0O00 [O00OO0OO00000OO00 ]={'label':O00OO0OO00000OO00 ,'children':[O000O000OO0O0O0OO ]}#line:31
        else :#line:32
            O00OO0O0OOOOOOO00 =OO00000000OOO0O00 .get (O00OO0OO00000OO00 )#line:33
            O0OO00000O0OO000O =O00OO0O0OOOOOOO00 .get ('children')#line:34
            O0OO00000O0OO000O .append (O000O000OO0O0O0OO )#line:35
    for O0OOOO0OO0OOO0O0O in OO00000000OOO0O00 :#line:40
        O000O000OO0O0O0OO =OO00000000OOO0O00 .get (O0OOOO0OO0OOO0O0O )#line:41
        O0OO00000O0OO000O =O000O000OO0O0O0OO .get ('children')#line:42
        O000O0000000O0OOO ={}#line:45
        for O0O0000O00000O000 in O0OO00000O0OO000O :#line:46
            O00OO0OO00000OO00 =O0O0000O00000O000 .content_type .name #line:48
            if O00OO0OO00000OO00 not in O000O0000000O0OOO :#line:49
                O000O0000000O0OOO [O00OO0OO00000OO00 ]={'label':O00OO0OO00000OO00 ,'children':[{'id':O0O0000O00000O000 .id ,'label':get_action_name (O0O0000O00000O000 .name )}]}#line:56
            else :#line:57
                O000O0000000O0OOO [O00OO0OO00000OO00 ].get ('children').append ({'id':O0O0000O00000O000 .id ,'label':get_action_name (O0O0000O00000O000 .name )})#line:61
        OO0OO0O00000OOO0O =[]#line:62
        for O0O0000O00000O000 in O000O0000000O0OOO :#line:63
            OO0OO0O00000OOO0O .append (O000O0000000O0OOO .get (O0O0000O00000O000 ))#line:64
        O000O000OO0O0O0OO ['children']=OO0OO0O00000OOO0O #line:65
    O00O00OOOO0O00OO0 =[]#line:67
    for O0O0000O00000O000 in OO00000000OOO0O00 :#line:68
        O00O00OOOO0O00OO0 .append (OO00000000OOO0O00 .get (O0O0000O00000O000 ))#line:69
    return O00O00OOOO0O00OO0 #line:71
