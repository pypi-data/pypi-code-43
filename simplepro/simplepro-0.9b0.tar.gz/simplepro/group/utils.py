from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O00OOO00OOO00O0OO =Permission .objects .all ()#line:20
    O00O000OO0OOOOOOO ={}#line:23
    for O000O00000OOO0OO0 in O00OOO00OOO00O0OO :#line:25
        O00OOO00OOOO0O0O0 =O000O00000OOO0OO0 .content_type .app_label #line:26
        if O00OOO00OOOO0O0O0 not in O00O000OO0OOOOOOO :#line:27
            O00O000OO0OOOOOOO [O00OOO00OOOO0O0O0 ]={'label':O00OOO00OOOO0O0O0 ,'children':[O000O00000OOO0OO0 ]}#line:31
        else :#line:32
            OOOOOOO0OO0OOO000 =O00O000OO0OOOOOOO .get (O00OOO00OOOO0O0O0 )#line:33
            OOOOO0OOOO00OO00O =OOOOOOO0OO0OOO000 .get ('children')#line:34
            OOOOO0OOOO00OO00O .append (O000O00000OOO0OO0 )#line:35
    for OOOO00OO0O0O00O00 in O00O000OO0OOOOOOO :#line:40
        O000O00000OOO0OO0 =O00O000OO0OOOOOOO .get (OOOO00OO0O0O00O00 )#line:41
        OOOOO0OOOO00OO00O =O000O00000OOO0OO0 .get ('children')#line:42
        OO000000OOOO0O00O ={}#line:45
        for O000O0OO000O000O0 in OOOOO0OOOO00OO00O :#line:46
            O00OOO00OOOO0O0O0 =O000O0OO000O000O0 .content_type .name #line:48
            if O00OOO00OOOO0O0O0 not in OO000000OOOO0O00O :#line:49
                OO000000OOOO0O00O [O00OOO00OOOO0O0O0 ]={'label':O00OOO00OOOO0O0O0 ,'children':[{'id':O000O0OO000O000O0 .id ,'label':get_action_name (O000O0OO000O000O0 .name )}]}#line:56
            else :#line:57
                OO000000OOOO0O00O [O00OOO00OOOO0O0O0 ].get ('children').append ({'id':O000O0OO000O000O0 .id ,'label':get_action_name (O000O0OO000O000O0 .name )})#line:61
        O0OOO0O0000000O0O =[]#line:62
        for O000O0OO000O000O0 in OO000000OOOO0O00O :#line:63
            O0OOO0O0000000O0O .append (OO000000OOOO0O00O .get (O000O0OO000O000O0 ))#line:64
        O000O00000OOO0OO0 ['children']=O0OOO0O0000000O0O #line:65
    O00O000OO0O00OO00 =[]#line:67
    for O000O0OO000O000O0 in O00O000OO0OOOOOOO :#line:68
        O00O000OO0O00OO00 .append (O00O000OO0OOOOOOO .get (O000O0OO000O000O0 ))#line:69
    return O00O000OO0O00OO00 #line:71
