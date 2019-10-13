"渗透率计算公式,内置Timur和coates方法"
import numpy 

def Timur(P,Swi):
    "P孔隙度，Swi束缚水饱和度"
    P,Swi=list(map(numpy.array,[P,Swi]))
    c=(0.136*P**4.4)/Swi**2
    return c

def coates(P,Swi):
    "P孔隙度，Swi束缚水饱和度"
    P,Swi=list(map(numpy.array,[P,Swi]))
    c=((100*P**2)*(1-Swi)/Swi)**2
    return c



if __name__ =="__main__":
    p=Timur(1,2)
    print(p)
else:
    pass
