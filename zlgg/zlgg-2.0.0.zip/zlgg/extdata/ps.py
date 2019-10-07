from bs4 import BeautifulSoup 
import re
import Levenshtein
from zlgg.core import to_arr,ismat
import Levenshtein 

import sys 

import time
import json 
import os 
from lmf.dbv2 import db_query,db_write ,db_command
import copy
import pandas as pd

from collections import OrderedDict

#现在无人能看懂这代码了，我自己也是
def pat(word,krr):
    words=re.split(":|：",word,1)
    if len(words)!=2:return 0
    #word1,word2=words[0],''.join(words[1:])
    word1,word2=words
    if word1=='' or word2=='':return 0
    return ismat(word1,krr)

def ps(page,krr):
    arr=to_arr(page)
    #data=OrderedDict({})
    data={}
    for i in range(len(arr)):
        for j in range(3):
            word=''.join(arr[i:i+j+1])
            if pat(word,krr):
                words=re.split(":|：",word)
                k,v=words[0],''.join(words[1:])
                #k=matwhat(k)
                if k not in data.keys():
                    data[k]=v
                else:
                    if not isinstance(data[k],list):
                        arr1=[copy.deepcopy(data[k]),v]
                        data[k]=arr1
                    else:
                        data[k].append(v)
                break
    return data
