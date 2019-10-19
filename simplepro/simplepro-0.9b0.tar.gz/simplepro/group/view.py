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
    OOO000OOO0OOOO0OO =request .POST .get ('action')#line:14
    O0O00O0OOOOO0O0O0 ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O0O00O0OOOOO0O0O0 .get (OOO000OOO0OOOO0OO )(request )#line:22
def get_detail (request ):#line:25
    OOO0OOOO000O000O0 =request .POST .get ('id')#line:26
    OOO00000000000000 =Group .objects .filter (id =OOO0OOOO000O000O0 ).first ()#line:27
    O0O00O00OO00O000O =[]#line:28
    if OOO00000000000000 :#line:29
        O00O00O00OOO000O0 =OOO00000000000000 .permissions .all ()#line:30
        for O0OO00OOO00O0OO00 in O00O00O00OOO000O0 :#line:31
            O0O00O00OO00O000O .append (O0OO00OOO00O0OO00 .id )#line:32
    return write (O0O00O00OO00O000O )#line:34
def save (request ):#line:37
    O0000O00O0O0OOO0O =True #line:38
    O00O0O00OOOOOOO0O ="ok"#line:39
    try :#line:40
        OOOO0OO0O0OO0O0OO =request .POST .get ('name')#line:41
        OOO0OO0OOOOO0O0O0 =request .POST .get ('ids')#line:42
        OO00OOOOO0O0OO0OO =request .POST .get ('id')#line:43
        if OO00OOOOO0O0OO0OO and OO00OOOOO0O0OO0OO !='':#line:46
            O0O0OO000O000OOO0 =Group .objects .get (id =OO00OOOOO0O0OO0OO )#line:47
            O0O0OO000O000OOO0 .permissions .clear ()#line:49
        else :#line:50
            O0O0OO000O000OOO0 =Group .objects .create (name =OOOO0OO0O0OO0O0OO )#line:51
        if OOO0OO0OOOOO0O0O0 and OOO0OO0OOOOO0O0O0 !='':#line:52
            OOO0OO0OOOOO0O0O0 =OOO0OO0OOOOO0O0O0 .split (',')#line:53
            for O00O000O0O00OO0OO in OOO0OO0OOOOO0O0O0 :#line:54
                O0O0OO000O000OOO0 .permissions .add (O00O000O0O00OO0OO )#line:56
    except Exception as OOOO000O00OO00O00 :#line:57
        O0000O00O0O0OOO0O =False #line:58
        O00O0O00OOOOOOO0O =OOOO000O00OO00O00 .args [0 ]#line:59
    return write (None ,O00O0O00OOOOOOO0O ,O0000O00O0O0OOO0O )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OOO0O0OO0O00OO0OO =get_permissions ()#line:69
    return write (OOO0O0OO0O00OO0OO )#line:70
