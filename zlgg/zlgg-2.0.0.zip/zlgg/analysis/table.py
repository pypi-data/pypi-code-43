from bs4 import BeautifulSoup 
import re
import Levenshtein
from zlgg.core import to_arr
import Levenshtein 

import sys 
from zlgg.core import ismat
import time
import json 
import copy

from collections import OrderedDict
htmlparser="lxml"


def calsep(table,krr):
    soup=BeautifulSoup(table,htmlparser)
    table=soup.find('table')
    if table is None:return 0
    tdrr=[ td.text.strip() for tr in table.find_all('tr') for td in tr.find_all('td')  ]

    tdrr1=[ int(ismat(w,krr)) for w in tdrr]

    s=0
    #print(tdrr1)
    for  i in range(len(tdrr1)):
         if tdrr1[i]!=1:continue
         
         if i+1>=len(tdrr1):break 
         if tdrr1[i+1]==1:
            s+=1


    s1=tdrr1.count(1)-1 if tdrr1.count(1)-1>1 else 1

    v=s/s1 
    return v 


def fm(table):
    soup=BeautifulSoup(table,htmlparser)
    table=soup.find('table')
    x=[ len(tr.find_all('td'))  for tr in table.find_all('tr')]
    return x
