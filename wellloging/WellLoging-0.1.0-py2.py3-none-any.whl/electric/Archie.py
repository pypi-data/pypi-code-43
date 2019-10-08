import numpy
def Rt(Rw,P,Sw,a=1,b=1,m=2,n=2 ):
    Rw,P,Sw,a,b,m,n=list(map(numpy.array,[Rw,P,Sw,a,b,m,n]))
    rt=a*b*Rw/((P**m)*(Sw**n))
    return rt

def Rw(Rt,P,Sw,a=1,b=1,m=2,n=2 ):
    Rt,P,Sw,a,b,m,n=list(map(numpy.array,[Rt,P,Sw,a,b,m,n]))
    rw=(P**m)*(Sw**n)*Rt/(a*b)
    return rw

def P(Rt,Rw,Sw,a=1,b=1,m=2,n=2 ):
    Rt,Rw,Sw,a,b,m,n=list(map(numpy.array,[Rt,Rw,Sw,a,b,m,n]))
    p=(a*b*Rw/((Sw**n)*Rt))**(1/m)
    return p

def Sw(Rt,Rw,P,a=1,b=1,m=2,n=2 ):
    Rt,Rw,P,a,b,m,n=list(map(numpy.array,[Rt,Rw,P,a,b,m,n]))
    sw=(a*b*Rw/((P**m)*Rt))**(1/n)
    return sw

