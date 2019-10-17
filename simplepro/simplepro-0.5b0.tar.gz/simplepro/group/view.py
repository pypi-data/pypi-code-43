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
    O000O0O00OOO0O000 =request .POST .get ('action')#line:14
    O00O00OO0OO000O0O ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O00O00OO0OO000O0O .get (O000O0O00OOO0O000 )(request )#line:22
def get_detail (request ):#line:25
    O00O00O0000OOO0OO =request .POST .get ('id')#line:26
    O0O00OOO0000OO0O0 =Group .objects .filter (id =O00O00O0000OOO0OO ).first ()#line:27
    O000OOOO00O00OOOO =[]#line:28
    if O0O00OOO0000OO0O0 :#line:29
        OO00000000O00OO0O =O0O00OOO0000OO0O0 .permissions .all ()#line:30
        for OOO0OOOO00O0OO0OO in OO00000000O00OO0O :#line:31
            O000OOOO00O00OOOO .append (OOO0OOOO00O0OO0OO .id )#line:32
    return write (O000OOOO00O00OOOO )#line:34
def save (request ):#line:37
    OO00O00OO0O0OO0OO =True #line:38
    OOO00O0OOOO00O0O0 ="ok"#line:39
    try :#line:40
        O0000O0O0OO00O000 =request .POST .get ('name')#line:41
        O000O0O0OO0OOOO0O =request .POST .get ('ids')#line:42
        OOOO0OOO000000O00 =request .POST .get ('id')#line:43
        if OOOO0OOO000000O00 and OOOO0OOO000000O00 !='':#line:46
            OOO0OOO00O000O0OO =Group .objects .get (id =OOOO0OOO000000O00 )#line:47
            OOO0OOO00O000O0OO .permissions .clear ()#line:49
        else :#line:50
            OOO0OOO00O000O0OO =Group .objects .create (name =O0000O0O0OO00O000 )#line:51
        if O000O0O0OO0OOOO0O and O000O0O0OO0OOOO0O !='':#line:52
            O000O0O0OO0OOOO0O =O000O0O0OO0OOOO0O .split (',')#line:53
            for O0OOOOOOOO00OOO0O in O000O0O0OO0OOOO0O :#line:54
                OOO0OOO00O000O0OO .permissions .add (O0OOOOOOOO00OOO0O )#line:56
    except Exception as OOOO0O0OOO0O000OO :#line:57
        OO00O00OO0O0OO0OO =False #line:58
        OOO00O0OOOO00O0O0 =OOOO0O0OOO0O000OO .args [0 ]#line:59
    return write (None ,OOO00O0OOOO00O0O0 ,OO00O00OO0O0OO0OO )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OOO00OOOO0O0OOO00 =get_permissions ()#line:69
    return write (OOO00OOOO0O0OOO00 )#line:70
