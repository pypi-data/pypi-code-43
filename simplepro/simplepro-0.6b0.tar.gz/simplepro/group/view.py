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
    O000O0OOOOO00000O =request .POST .get ('action')#line:14
    OOOOO0OOOO0O00OOO ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return OOOOO0OOOO0O00OOO .get (O000O0OOOOO00000O )(request )#line:22
def get_detail (request ):#line:25
    O00OO0OO0OOO0000O =request .POST .get ('id')#line:26
    O0O00OOO0O0OO0OOO =Group .objects .filter (id =O00OO0OO0OOO0000O ).first ()#line:27
    O0OO0OO0OOO00O0OO =[]#line:28
    if O0O00OOO0O0OO0OOO :#line:29
        OOO0O00OO0OO00O00 =O0O00OOO0O0OO0OOO .permissions .all ()#line:30
        for O0O0O0000O0O000OO in OOO0O00OO0OO00O00 :#line:31
            O0OO0OO0OOO00O0OO .append (O0O0O0000O0O000OO .id )#line:32
    return write (O0OO0OO0OOO00O0OO )#line:34
def save (request ):#line:37
    O0O000000O0O00OOO =True #line:38
    O00OO0OOO00OO0OOO ="ok"#line:39
    try :#line:40
        O0OOO00O000O00OO0 =request .POST .get ('name')#line:41
        O000OOO000OOOO00O =request .POST .get ('ids')#line:42
        O00O0OOO0O00000O0 =request .POST .get ('id')#line:43
        if O00O0OOO0O00000O0 and O00O0OOO0O00000O0 !='':#line:46
            OO00OO00OOO0O0OO0 =Group .objects .get (id =O00O0OOO0O00000O0 )#line:47
            OO00OO00OOO0O0OO0 .permissions .clear ()#line:49
        else :#line:50
            OO00OO00OOO0O0OO0 =Group .objects .create (name =O0OOO00O000O00OO0 )#line:51
        if O000OOO000OOOO00O and O000OOO000OOOO00O !='':#line:52
            O000OOO000OOOO00O =O000OOO000OOOO00O .split (',')#line:53
            for OO0O0OOOO0OO0OOOO in O000OOO000OOOO00O :#line:54
                OO00OO00OOO0O0OO0 .permissions .add (OO0O0OOOO0OO0OOOO )#line:56
    except Exception as OO000OO0O00000O00 :#line:57
        O0O000000O0O00OOO =False #line:58
        O00OO0OOO00OO0OOO =OO000OO0O00000O00 .args [0 ]#line:59
    return write (None ,O00OO0OOO00OO0OOO ,O0O000000O0O00OOO )#line:60
def get_tree (request ):#line:63
    ""#line:68
    OOOO0OO0OOO00000O =get_permissions ()#line:69
    return write (OOOO0OO0OOO00000O )#line:70
