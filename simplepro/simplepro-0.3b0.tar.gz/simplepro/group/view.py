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
    O0O000OOO000O000O =request .POST .get ('action')#line:14
    O0O00OOOOO000000O ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O0O00OOOOO000000O .get (O0O000OOO000O000O )(request )#line:22
def get_detail (request ):#line:25
    OOOOOOOO000000OO0 =request .POST .get ('id')#line:26
    O000O0OO0OO0O000O =Group .objects .filter (id =OOOOOOOO000000OO0 ).first ()#line:27
    O0OOO00O0O0000O0O =[]#line:28
    if O000O0OO0OO0O000O :#line:29
        OOO000O0OO000OO0O =O000O0OO0OO0O000O .permissions .all ()#line:30
        for OOOOO0000000OOOO0 in OOO000O0OO000OO0O :#line:31
            O0OOO00O0O0000O0O .append (OOOOO0000000OOOO0 .id )#line:32
    return write (O0OOO00O0O0000O0O )#line:34
def save (request ):#line:37
    O00OOOO00OOO00O00 =True #line:38
    O000O0O00O0OOO000 ="ok"#line:39
    try :#line:40
        OOOOOO00000OO0OO0 =request .POST .get ('name')#line:41
        O0000O0OOOOO0OO0O =request .POST .get ('ids')#line:42
        O0OOO0000OOO0O0OO =request .POST .get ('id')#line:43
        if O0OOO0000OOO0O0OO and O0OOO0000OOO0O0OO !='':#line:46
            OOO0OO00000000OOO =Group .objects .get (id =O0OOO0000OOO0O0OO )#line:47
            OOO0OO00000000OOO .permissions .clear ()#line:49
        else :#line:50
            OOO0OO00000000OOO =Group .objects .create (name =OOOOOO00000OO0OO0 )#line:51
        if O0000O0OOOOO0OO0O and O0000O0OOOOO0OO0O !='':#line:52
            O0000O0OOOOO0OO0O =O0000O0OOOOO0OO0O .split (',')#line:53
            for OOO0O00O000O0OOO0 in O0000O0OOOOO0OO0O :#line:54
                OOO0OO00000000OOO .permissions .add (OOO0O00O000O0OOO0 )#line:56
    except Exception as OO00O000000OO0000 :#line:57
        O00OOOO00OOO00O00 =False #line:58
        O000O0O00O0OOO000 =OO00O000000OO0000 .args [0 ]#line:59
    return write (None ,O000O0O00O0OOO000 ,O00OOOO00OOO00O00 )#line:60
def get_tree (request ):#line:63
    ""#line:68
    O00OO0O00OOOOOO0O =get_permissions ()#line:69
    return write (O00OO0O00OOOOOO0O )#line:70
