from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O0OOOOOOO0OOOO000 =Permission .objects .all ()#line:20
    O0OOOO0O0OOOO0O00 ={}#line:23
    for O0000O000OOOOO000 in O0OOOOOOO0OOOO000 :#line:25
        O00OOOOO0OOOOOOO0 =O0000O000OOOOO000 .content_type .app_label #line:26
        if O00OOOOO0OOOOOOO0 not in O0OOOO0O0OOOO0O00 :#line:27
            O0OOOO0O0OOOO0O00 [O00OOOOO0OOOOOOO0 ]={'label':O00OOOOO0OOOOOOO0 ,'children':[O0000O000OOOOO000 ]}#line:31
        else :#line:32
            OOOO0OO0O000O00OO =O0OOOO0O0OOOO0O00 .get (O00OOOOO0OOOOOOO0 )#line:33
            O000000OOO0OO0000 =OOOO0OO0O000O00OO .get ('children')#line:34
            O000000OOO0OO0000 .append (O0000O000OOOOO000 )#line:35
    for O0000O00000OOOO0O in O0OOOO0O0OOOO0O00 :#line:40
        O0000O000OOOOO000 =O0OOOO0O0OOOO0O00 .get (O0000O00000OOOO0O )#line:41
        O000000OOO0OO0000 =O0000O000OOOOO000 .get ('children')#line:42
        O00OO0OOOO0O0OOO0 ={}#line:45
        for O00O0000O0OO00000 in O000000OOO0OO0000 :#line:46
            O00OOOOO0OOOOOOO0 =O00O0000O0OO00000 .content_type .name #line:48
            if O00OOOOO0OOOOOOO0 not in O00OO0OOOO0O0OOO0 :#line:49
                O00OO0OOOO0O0OOO0 [O00OOOOO0OOOOOOO0 ]={'label':O00OOOOO0OOOOOOO0 ,'children':[{'id':O00O0000O0OO00000 .id ,'label':get_action_name (O00O0000O0OO00000 .name )}]}#line:56
            else :#line:57
                O00OO0OOOO0O0OOO0 [O00OOOOO0OOOOOOO0 ].get ('children').append ({'id':O00O0000O0OO00000 .id ,'label':get_action_name (O00O0000O0OO00000 .name )})#line:61
        OO0OOO000O0000OOO =[]#line:62
        for O00O0000O0OO00000 in O00OO0OOOO0O0OOO0 :#line:63
            OO0OOO000O0000OOO .append (O00OO0OOOO0O0OOO0 .get (O00O0000O0OO00000 ))#line:64
        O0000O000OOOOO000 ['children']=OO0OOO000O0000OOO #line:65
    OOO0O0000OOOOOOO0 =[]#line:67
    for O00O0000O0OO00000 in O0OOOO0O0OOOO0O00 :#line:68
        OOO0O0000OOOOOOO0 .append (O0OOOO0O0OOOO0O00 .get (O00O0000O0OO00000 ))#line:69
    return OOO0O0000OOOOOOO0 #line:71
