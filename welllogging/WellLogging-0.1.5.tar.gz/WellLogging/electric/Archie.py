"阿尔齐公式,内置岩石电阻率(Rt),地层水电阻率(Rw),饱和度(Sw),孔隙度(P)正演计算公式"
import numpy
def Rt(Rw,P,Sw,a=1,b=1,m=2,n=2 ):
    "Rw:地层水电阻率，P：孔隙度，Sw:地层水饱和度，a,b:岩性系数默认为1，m孔隙度指数默认为2，n饱和度指数默认为2"
    Rw,P,Sw,a,b,m,n=list(map(numpy.array,[Rw,P,Sw,a,b,m,n]))
    rt=a*b*Rw/((P**m)*(Sw**n))
    return rt

def Rw(Rt,P,Sw,a=1,b=1,m=2,n=2 ):
    "Rt:地层电阻率，P：孔隙度，Sw:地层水饱和度，a,b:岩性系数默认为1，m孔隙度指数默认为2，n饱和度指数默认为2"
    Rt,P,Sw,a,b,m,n=list(map(numpy.array,[Rt,P,Sw,a,b,m,n]))
    rw=(P**m)*(Sw**n)*Rt/(a*b)
    return rw

def P(Rt,Rw,Sw,a=1,b=1,m=2,n=2 ):
    "Rt:地层电阻率，Rw:地层水电阻率，Sw:地层水饱和度，a,b:岩性系数默认为1，m孔隙度指数默认为2，n饱和度指数默认为2"    
    Rt,Rw,Sw,a,b,m,n=list(map(numpy.array,[Rt,Rw,Sw,a,b,m,n]))
    p=(a*b*Rw/((Sw**n)*Rt))**(1/m)
    return p

def Sw(Rt,Rw,P,a=1,b=1,m=2,n=2 ):
    "Rt:地层电阻率，Rw:地层水电阻率，P孔隙度，a,b:岩性系数默认为1，m孔隙度指数默认为2，n饱和度指数默认为2" 
    Rt,Rw,P,a,b,m,n=list(map(numpy.array,[Rt,Rw,P,a,b,m,n]))
    sw=(a*b*Rw/((P**m)*Rt))**(1/n)
    return sw

