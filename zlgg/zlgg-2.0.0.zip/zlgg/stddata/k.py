from zlgg.core import ismat 

def get_name(data1,name_list):
    if data1 is None:return None
    tbsxx,psxx=data1['tbs'],data1['ps']
    if tbsxx is not  None:
        for data in tbsxx:
            for  w in data.keys():

                if  isinstance(data[w],str):
                    if ismat(w,name_list) :return data[w]
                if  isinstance(data[w],list):

                    if ismat(w,name_list) and isinstance(data[w][0] ,str) :return data[w][0]
                    if isinstance(data[w][0] ,dict) :
                        for w2 in data[w][0].keys():
                            if  isinstance(data[w][0][w2],str): 
                                if ismat(w2,name_list): return data[w][0][w2]
                            if  isinstance(data[w][0][w2],list):
                                if ismat(w2,name_list):return data[w][0][w2][0]


                if  isinstance(data[w],dict):
                    for w1 in data[w].keys():
                        if  isinstance(data[w][w1],str): 
                            if ismat(w1,name_list): return data[w][w1]
                        if  isinstance(data[w][w1],list):
                            if ismat(w1,name_list):return data[w][w1][0]
    for w in psxx.keys():
            if  isinstance(psxx[w],str):
                if ismat(w,name_list) :return psxx[w]
            if  isinstance(psxx[w],list):
                if ismat(w,name_list) :return psxx[w][0]
    return None

def getsist(data,arrdict):
    if data is None:return {}
    result={}
    it=["xmmc","kzj","zhaobiaoren",'zbdl','zbfs','xmbh','zhongbiaoren','zhongbiaojia','xmjl','xmdz']
    for w in it:
        if w not in arrdict.keys():continue
        arr=arrdict[w]
        v=get_name(data,arr)
        if v is not None:result[w]=v
    return result



#def kstd(data,arrdict):
