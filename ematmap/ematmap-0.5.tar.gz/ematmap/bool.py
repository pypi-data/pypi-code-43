from ematmap.filter_udlr import xvfltrxy
from ematmap.utils import get_matsize

def locs(ele,m):
    cond_func = lambda x,y,ele:(m[x][y]==ele)
    locs = xvfltrxy(m,cond_func=cond_func)
    return(locs)

def exist(ele,m):
    locs = locs(ele,m)
    return(len(locs)>0)

def all(ele,m):
    size = get_matsize(m)
    locs = locs(ele,m)
    return(len(locs)==size)

def locs_not(ele,m):
    cond_func = lambda x,y,ele:not(m[x][y]==ele)
    locs = xvfltrxy(m,cond_func=cond_func)
    return(locs)

def exist_not(ele,m):
    locs = locs_not(ele,m)
    return(len(locs)>0)

def all_not(ele,m):
    size = get_matsize(m)
    locs = locs_not(ele,m)
    return(len(locs)==size)







