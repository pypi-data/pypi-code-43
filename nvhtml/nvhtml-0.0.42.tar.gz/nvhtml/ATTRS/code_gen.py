import elist.elist as elel
import edict.edict as eded

def w3c_fmt(s):
    arr = s.split("\n")
    arr = elel.mapv(arr,lambda ele:ele.split("\t"))
    kl = elel.mapv(arr,lambda ele:ele[0].strip(" "))
    vl = elel.mapv(arr,lambda ele:ele[1].strip(" "))
    d = eded.kvlist2d(kl,vl)
    return(d)


