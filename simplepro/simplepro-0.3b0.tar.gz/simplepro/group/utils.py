from django .contrib .auth .models import Permission #line:1
def get_action_name (name ):#line:4
    ""#line:9
    name =name .replace ('Can add ','增加').replace ('Can change ','编辑').replace ('Can delete ','删除').replace ('Can view ','查看')#line:11
    return name #line:12
def get_permissions ():#line:15
    ""#line:19
    O0OO000000O0O00O0 =Permission .objects .all ()#line:20
    OOO00OO00O00OOO00 ={}#line:23
    for O0O0O00000OOOOO00 in O0OO000000O0O00O0 :#line:25
        OOO0O0O0OOOOOOO00 =O0O0O00000OOOOO00 .content_type .app_label #line:26
        if OOO0O0O0OOOOOOO00 not in OOO00OO00O00OOO00 :#line:27
            OOO00OO00O00OOO00 [OOO0O0O0OOOOOOO00 ]={'label':OOO0O0O0OOOOOOO00 ,'children':[O0O0O00000OOOOO00 ]}#line:31
        else :#line:32
            OO000O000O0OOO0O0 =OOO00OO00O00OOO00 .get (OOO0O0O0OOOOOOO00 )#line:33
            OO00OOO0O00O0O00O =OO000O000O0OOO0O0 .get ('children')#line:34
            OO00OOO0O00O0O00O .append (O0O0O00000OOOOO00 )#line:35
    for O0O0OO0OO0000O0OO in OOO00OO00O00OOO00 :#line:40
        O0O0O00000OOOOO00 =OOO00OO00O00OOO00 .get (O0O0OO0OO0000O0OO )#line:41
        OO00OOO0O00O0O00O =O0O0O00000OOOOO00 .get ('children')#line:42
        O000OO00O00OO0O0O ={}#line:45
        for O0OO00OOO0000OO0O in OO00OOO0O00O0O00O :#line:46
            OOO0O0O0OOOOOOO00 =O0OO00OOO0000OO0O .content_type .name #line:48
            if OOO0O0O0OOOOOOO00 not in O000OO00O00OO0O0O :#line:49
                O000OO00O00OO0O0O [OOO0O0O0OOOOOOO00 ]={'label':OOO0O0O0OOOOOOO00 ,'children':[{'id':O0OO00OOO0000OO0O .id ,'label':get_action_name (O0OO00OOO0000OO0O .name )}]}#line:56
            else :#line:57
                O000OO00O00OO0O0O [OOO0O0O0OOOOOOO00 ].get ('children').append ({'id':O0OO00OOO0000OO0O .id ,'label':get_action_name (O0OO00OOO0000OO0O .name )})#line:61
        O0O0OOO00OOO00000 =[]#line:62
        for O0OO00OOO0000OO0O in O000OO00O00OO0O0O :#line:63
            O0O0OOO00OOO00000 .append (O000OO00O00OO0O0O .get (O0OO00OOO0000OO0O ))#line:64
        O0O0O00000OOOOO00 ['children']=O0O0OOO00OOO00000 #line:65
    O0OOO0OO00OOOOO00 =[]#line:67
    for O0OO00OOO0000OO0O in OOO00OO00O00OOO00 :#line:68
        O0OOO0OO00OOOOO00 .append (OOO00OO00O00OOO00 .get (O0OO00OOO0000OO0O ))#line:69
    return O0OOO0OO00OOOOO00 #line:71
