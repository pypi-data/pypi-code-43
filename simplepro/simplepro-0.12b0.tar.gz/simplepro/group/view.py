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
    OOOOO00O00O0O0O00 =request .POST .get ('action')#line:14
    O00OOOOO0O0000000 ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O00OOOOO0O0000000 .get (OOOOO00O00O0O0O00 )(request )#line:22
def get_detail (request ):#line:25
    OOO0OOOOO000O0O0O =request .POST .get ('id')#line:26
    O0OOO00000O0O00O0 =Group .objects .filter (id =OOO0OOOOO000O0O0O ).first ()#line:27
    OO000O0O0O0O0O00O =[]#line:28
    if O0OOO00000O0O00O0 :#line:29
        OOO0O0O000000O00O =O0OOO00000O0O00O0 .permissions .all ()#line:30
        for OOOOO0OOOOOO00OOO in OOO0O0O000000O00O :#line:31
            OO000O0O0O0O0O00O .append (OOOOO0OOOOOO00OOO .id )#line:32
    return write (OO000O0O0O0O0O00O )#line:34
def save (request ):#line:37
    O000OO0OOOOOO000O =True #line:38
    O0OO000000OOO000O ="ok"#line:39
    try :#line:40
        OO0O00OO0000OO0OO =request .POST .get ('name')#line:41
        O0OOOO0OOOO00O0O0 =request .POST .get ('ids')#line:42
        OO0OO0O0O0OO0O00O =request .POST .get ('id')#line:43
        if OO0OO0O0O0OO0O00O and OO0OO0O0O0OO0O00O !='':#line:46
            O000OO0O000O0O0O0 =Group .objects .get (id =OO0OO0O0O0OO0O00O )#line:47
            O000OO0O000O0O0O0 .permissions .clear ()#line:49
        else :#line:50
            O000OO0O000O0O0O0 =Group .objects .create (name =OO0O00OO0000OO0OO )#line:51
        if O0OOOO0OOOO00O0O0 and O0OOOO0OOOO00O0O0 !='':#line:52
            O0OOOO0OOOO00O0O0 =O0OOOO0OOOO00O0O0 .split (',')#line:53
            for OOOOOOOO0000OO00O in O0OOOO0OOOO00O0O0 :#line:54
                O000OO0O000O0O0O0 .permissions .add (OOOOOOOO0000OO00O )#line:56
    except Exception as OOOOOOOOOOOOOOOO0 :#line:57
        O000OO0OOOOOO000O =False #line:58
        O0OO000000OOO000O =OOOOOOOOOOOOOOOO0 .args [0 ]#line:59
    return write (None ,O0OO000000OOO000O ,O000OO0OOOOOO000O )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OOOOOO00OOOOO0O00 =get_permissions ()#line:69
    return write (OOOOOO00OOOOO0O00 )#line:70
