import elist.elist as elel

def parr(arr):
    for i in range(arr.__len__()):
        print(arr[i])

def pl2path(pl,*args):
    p = elel.join(pl,"/")
    p = "/" +p 
    args = list(args)
    lngth = args.__len__()
    if(args.__len__()==0):
        pass
    elif(args.__len__()==1):
        p = p+"/"+str(args[0])
    else:
        p = p+"/"+dtr(args[0])+"."+str(args[1])
    return(p)

def arguments_whiches(lngth,*args,**kwargs):
    args = list(args)
    if(args.__len__() == 0):
        if('start' in kwargs):
            start = kwargs['start']
        else:
            start = 0
        if('end' in kwargs):
            end = kwargs['end']
        else:
            end = lngth
        whiches = elel.init_range(start,end,1)
    else:
        if(isinstance(args[0],list)):
            whiches = args[0]
        else:
            whiches = args
    whiches.sort()
    return(whiches)

def arguments_levels(*args,**kwargs):
    args = list(args)
    if(args.__len__() == 0):
        if('start' in kwargs):
            start = kwargs['start']
        else:
            start = 0
        if('end' in kwargs):
            end = kwargs['end']
        else:
            end = 2**32
    elif(args.__len__() == 1):
        start = args[0]
        if('end' in kwargs):
            end = kwargs['end']
        else:
            end = 2**32
    else:
        start = args[0]
        end = args[1]
    if('rel' in kwargs):
        rel = kwargs['rel']
    else:
        rel = False
    return((start,end,rel))

