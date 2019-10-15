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
    OO0OOOO0O0OOO0O00 =request .POST .get ('action')#line:14
    O0OO00O000O00O000 ={'tree':get_tree ,'save':save ,'get_detail':get_detail }#line:20
    return O0OO00O000O00O000 .get (OO0OOOO0O0OOO0O00 )(request )#line:22
def get_detail (request ):#line:25
    O0OO0000000OO0O00 =request .POST .get ('id')#line:26
    O00OOOOO0O0O0OOOO =Group .objects .filter (id =O0OO0000000OO0O00 ).first ()#line:27
    O0OO0OOOOO0OO00O0 =[]#line:28
    if O00OOOOO0O0O0OOOO :#line:29
        OO0O0OO00O0O0000O =O00OOOOO0O0O0OOOO .permissions .all ()#line:30
        for OO0OOOOOO00OOO0OO in OO0O0OO00O0O0000O :#line:31
            O0OO0OOOOO0OO00O0 .append (OO0OOOOOO00OOO0OO .id )#line:32
    return write (O0OO0OOOOO0OO00O0 )#line:34
def save (request ):#line:37
    OO00OO000OOOO00O0 =True #line:38
    O0OOOOO0OO0O0OOO0 ="ok"#line:39
    try :#line:40
        O000OO00OO0O00000 =request .POST .get ('name')#line:41
        OOOOO0O000O00OOO0 =request .POST .get ('ids')#line:42
        O0O000OO00OOOOOOO =request .POST .get ('id')#line:43
        if O0O000OO00OOOOOOO and O0O000OO00OOOOOOO !='':#line:46
            OOO0O0O00O0O00O00 =Group .objects .get (id =O0O000OO00OOOOOOO )#line:47
            OOO0O0O00O0O00O00 .permissions .clear ()#line:49
        else :#line:50
            OOO0O0O00O0O00O00 =Group .objects .create (name =O000OO00OO0O00000 )#line:51
        if OOOOO0O000O00OOO0 and OOOOO0O000O00OOO0 !='':#line:52
            OOOOO0O000O00OOO0 =OOOOO0O000O00OOO0 .split (',')#line:53
            for OO0000000O00OO000 in OOOOO0O000O00OOO0 :#line:54
                OOO0O0O00O0O00O00 .permissions .add (OO0000000O00OO000 )#line:56
    except Exception as OO0000OO0O0OOO0O0 :#line:57
        OO00OO000OOOO00O0 =False #line:58
        O0OOOOO0OO0O0OOO0 =OO0000OO0O0OOO0O0 .args [0 ]#line:59
    return write (None ,O0OOOOO0OO0O0OOO0 ,OO00OO000OOOO00O0 )#line:60
def get_tree (request ):#line:63
    ""#line:68
    O00OOOO0OO00OO0O0 =get_permissions ()#line:69
    return write (O00OOOO0OO00OO0O0 )#line:70
