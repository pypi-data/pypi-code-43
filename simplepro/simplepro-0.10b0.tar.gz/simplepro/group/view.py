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
    O0O0OO00O00O0O0O0 =request .POST .get ('action')#line:14
    OO000OO00O00OOO00 ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return OO000OO00O00OOO00 .get (O0O0OO00O00O0O0O0 )(request )#line:22
def get_detail (request ):#line:25
    O0O0O0O000OOO00O0 =request .POST .get ('id')#line:26
    O0O00OOOO0OOOOO0O =Group .objects .filter (id =O0O0O0O000OOO00O0 ).first ()#line:27
    O0OOOO000OOO0000O =[]#line:28
    if O0O00OOOO0OOOOO0O :#line:29
        O000O00OO0O00000O =O0O00OOOO0OOOOO0O .permissions .all ()#line:30
        for O000OOO0OOOO00000 in O000O00OO0O00000O :#line:31
            O0OOOO000OOO0000O .append (O000OOO0OOOO00000 .id )#line:32
    return write (O0OOOO000OOO0000O )#line:34
def save (request ):#line:37
    O00OO000OOOO000OO =True #line:38
    O0OO00O0OOO0O0OOO ="ok"#line:39
    try :#line:40
        OO0OO0OO00O0000O0 =request .POST .get ('name')#line:41
        OOO0OOOOO00OO0000 =request .POST .get ('ids')#line:42
        O0O0O000OOO0OO00O =request .POST .get ('id')#line:43
        if O0O0O000OOO0OO00O and O0O0O000OOO0OO00O !='':#line:46
            O00000OO0O000O000 =Group .objects .get (id =O0O0O000OOO0OO00O )#line:47
            O00000OO0O000O000 .permissions .clear ()#line:49
        else :#line:50
            O00000OO0O000O000 =Group .objects .create (name =OO0OO0OO00O0000O0 )#line:51
        if OOO0OOOOO00OO0000 and OOO0OOOOO00OO0000 !='':#line:52
            OOO0OOOOO00OO0000 =OOO0OOOOO00OO0000 .split (',')#line:53
            for OO0OO0OOO0OO0O00O in OOO0OOOOO00OO0000 :#line:54
                O00000OO0O000O000 .permissions .add (OO0OO0OOO0OO0O00O )#line:56
    except Exception as OOO0OO0O000000000 :#line:57
        O00OO000OOOO000OO =False #line:58
        O0OO00O0OOO0O0OOO =OOO0OO0O000000000 .args [0 ]#line:59
    return write (None ,O0OO00O0OOO0O0OOO ,O00OO000OOOO000OO )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OO00OOOO0O0OO0OOO =get_permissions ()#line:69
    return write (OO00OOOO0O0OO0OOO )#line:70
