from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    OO0OO0OOO000OOO0O =Permission .objects .all ()#line:20
    OOOO0OO00OOO000OO ={}#line:23
    for O00O0OO000O0O0O0O in OO0OO0OOO000OOO0O :#line:25
        O000OOOOOOO00O00O =O00O0OO000O0O0O0O .content_type .app_label #line:26
        if O000OOOOOOO00O00O not in OOOO0OO00OOO000OO :#line:27
            OOOO0OO00OOO000OO [O000OOOOOOO00O00O ]={'label':O000OOOOOOO00O00O ,'children':[O00O0OO000O0O0O0O ]}#line:31
        else :#line:32
            OO00000OO000O0O0O =OOOO0OO00OOO000OO .get (O000OOOOOOO00O00O )#line:33
            O000OOO0000OOOO0O =OO00000OO000O0O0O .get ('children')#line:34
            O000OOO0000OOOO0O .append (O00O0OO000O0O0O0O )#line:35
    for O000O00OO00O0OOO0 in OOOO0OO00OOO000OO :#line:40
        O00O0OO000O0O0O0O =OOOO0OO00OOO000OO .get (O000O00OO00O0OOO0 )#line:41
        O000OOO0000OOOO0O =O00O0OO000O0O0O0O .get ('children')#line:42
        O00OO00OOO000O0OO ={}#line:45
        for OO00O000000O0O0O0 in O000OOO0000OOOO0O :#line:46
            O000OOOOOOO00O00O =OO00O000000O0O0O0 .content_type .name #line:48
            if O000OOOOOOO00O00O not in O00OO00OOO000O0OO :#line:49
                O00OO00OOO000O0OO [O000OOOOOOO00O00O ]={'label':O000OOOOOOO00O00O ,'children':[{'id':OO00O000000O0O0O0 .id ,'label':get_action_name (OO00O000000O0O0O0 .name )}]}#line:56
            else :#line:57
                O00OO00OOO000O0OO [O000OOOOOOO00O00O ].get ('children').append ({'id':OO00O000000O0O0O0 .id ,'label':get_action_name (OO00O000000O0O0O0 .name )})#line:61
        OO0OO0O0O00OOO00O =[]#line:62
        for OO00O000000O0O0O0 in O00OO00OOO000O0OO :#line:63
            OO0OO0O0O00OOO00O .append (O00OO00OOO000O0OO .get (OO00O000000O0O0O0 ))#line:64
        O00O0OO000O0O0O0O ['children']=OO0OO0O0O00OOO00O #line:65
    OO00O0000000O0O0O =[]#line:67
    for OO00O000000O0O0O0 in OOOO0OO00OOO000OO :#line:68
        OO00O0000000O0O0O .append (OOOO0OO00OOO000OO .get (OO00O000000O0O0O0 ))#line:69
    return OO00O0000000O0O0O #line:71
