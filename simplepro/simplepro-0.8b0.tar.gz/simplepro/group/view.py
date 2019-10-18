import json #line:1
import os #line:2
from django .contrib .auth .models import Permission ,Group #line:4
from django .shortcuts import render #line:5
from .utils import get_permissions #line:6
from simplepro .utils import write ,write_obj #line:7
from simplepro import conf #line:8
import requests #line:9
import struct #line:10
def action (request ):#line:13
    O00O0OOOOO00O0O0O =request .POST .get ('action')#line:14
    OO0OOOOO0OO00O0O0 ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return OO0OOOOO0OO00O0O0 .get (O00O0OOOOO00O0O0O )(request )#line:22
def get_detail (request ):#line:25
    O0O0O0O0OO00O0OOO =request .POST .get ('id')#line:26
    O0O0O00O00O0OOOO0 =Group .objects .filter (id =O0O0O0O0OO00O0OOO ).first ()#line:27
    OO0000OOO00O00000 =[]#line:28
    if O0O0O00O00O0OOOO0 :#line:29
        OOOO0OOO0OO00O0OO =O0O0O00O00O0OOOO0 .permissions .all ()#line:30
        for OO00OOO0O00O00000 in OOOO0OOO0OO00O0OO :#line:31
            OO0000OOO00O00000 .append (OO00OOO0O00O00000 .id )#line:32
    return write (OO0000OOO00O00000 )#line:34
def save (request ):#line:37
    O00O0OO00OOO0OOOO =True #line:38
    OOOOOOOOOOOO0O000 ="ok"#line:39
    try :#line:40
        O00OO000O00OO00O0 =request .POST .get ('name')#line:41
        OO00O0O00O0000OO0 =request .POST .get ('ids')#line:42
        OO0OOOO000OO0O000 =request .POST .get ('id')#line:43
        if OO0OOOO000OO0O000 and OO0OOOO000OO0O000 !='':#line:46
            OO000O0O00OOOO0OO =Group .objects .get (id =OO0OOOO000OO0O000 )#line:47
            OO000O0O00OOOO0OO .permissions .clear ()#line:49
        else :#line:50
            OO000O0O00OOOO0OO =Group .objects .create (name =O00OO000O00OO00O0 )#line:51
        if OO00O0O00O0000OO0 and OO00O0O00O0000OO0 !='':#line:52
            OO00O0O00O0000OO0 =OO00O0O00O0000OO0 .split (',')#line:53
            for O0O0O0O0000O0O000 in OO00O0O00O0000OO0 :#line:54
                OO000O0O00OOOO0OO .permissions .add (O0O0O0O0000O0O000 )#line:56
    except Exception as OO00000OOOOOOO00O :#line:57
        O00O0OO00OOO0OOOO =False #line:58
        OOOOOOOOOOOO0O000 =OO00000OOOOOOO00O .args [0 ]#line:59
    return write (None ,OOOOOOOOOOOO0O000 ,O00O0OO00OOO0OOOO )#line:60
def get_tree (request ):#line:63
    ""#line:68
    O00000O0OO000O000 =get_permissions ()#line:69
    return write (O00000O0OO000O000 )#line:70
