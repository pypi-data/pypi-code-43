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
    OOO00OO0OO000OOO0 =request .POST .get ('action')#line:14
    O0O0O0OO0O0OO0OOO ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O0O0O0OO0O0OO0OOO .get (OOO00OO0OO000OOO0 )(request )#line:22
def get_detail (request ):#line:25
    OOOOO00O000O00OO0 =request .POST .get ('id')#line:26
    OOO000000O00000OO =Group .objects .filter (id =OOOOO00O000O00OO0 ).first ()#line:27
    OOOO00OO00OOOO000 =[]#line:28
    if OOO000000O00000OO :#line:29
        OO00O00OOO000000O =OOO000000O00000OO .permissions .all ()#line:30
        for O000OOO00OOOO00OO in OO00O00OOO000000O :#line:31
            OOOO00OO00OOOO000 .append (O000OOO00OOOO00OO .id )#line:32
    return write (OOOO00OO00OOOO000 )#line:34
def save (request ):#line:37
    OOO000O0O0OOO0O00 =True #line:38
    OO0OO0OO000000O00 ="ok"#line:39
    try :#line:40
        O0O0OO00O0OO00000 =request .POST .get ('name')#line:41
        OO0OO0OO000O0O0OO =request .POST .get ('ids')#line:42
        O0O00OO000OO000OO =request .POST .get ('id')#line:43
        if O0O00OO000OO000OO and O0O00OO000OO000OO !='':#line:46
            OOOOOOOOO00O0O0O0 =Group .objects .get (id =O0O00OO000OO000OO )#line:47
            OOOOOOOOO00O0O0O0 .permissions .clear ()#line:49
        else :#line:50
            OOOOOOOOO00O0O0O0 =Group .objects .create (name =O0O0OO00O0OO00000 )#line:51
        if OO0OO0OO000O0O0OO and OO0OO0OO000O0O0OO !='':#line:52
            OO0OO0OO000O0O0OO =OO0OO0OO000O0O0OO .split (',')#line:53
            for O0O000OOOO0OOO000 in OO0OO0OO000O0O0OO :#line:54
                OOOOOOOOO00O0O0O0 .permissions .add (O0O000OOOO0OOO000 )#line:56
    except Exception as O00OOO00O0O00OO00 :#line:57
        OOO000O0O0OOO0O00 =False #line:58
        OO0OO0OO000000O00 =O00OOO00O0O00OO00 .args [0 ]#line:59
    return write (None ,OO0OO0OO000000O00 ,OOO000O0O0OOO0O00 )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OO000000000OOOOOO =get_permissions ()#line:69
    return write (OO000000000OOOOOO )#line:70
