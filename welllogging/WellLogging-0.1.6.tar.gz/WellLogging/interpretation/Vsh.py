"泥质含量的计算,适用于自然伽马和自然电位测井"
import numpy
def Vsh(rmin,rmax,r,GCUR=2):
    "rmin:最小读数，rmax：最大读数，r:当前岩层值，GCUR：经验系数，默认为2"
    rmin,rmax,r,GCUR=list(map(numpy.array,[rmin,rmax,r,GCUR]))
    shi=(r-rmin)/(rmax-rmin)
    v=(2**(GCUR*shi)-1)/(2**(GCUR)-1)
    return v



if __name__ =="__main__":
    p=Vsh(1,2,3,3.7)
    print(p)
else:
    pass