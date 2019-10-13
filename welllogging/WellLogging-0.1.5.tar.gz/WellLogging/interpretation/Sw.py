"饱和度的计算，内置西门度(Smd)方法和阿尔齐(Archie)方法"
import numpy

def Smd(Rt,Rw,P,Vsh,Rsh):
    "Rt:地层电阻率，Rw:地层水电阻率，P：孔隙度，Vsh:泥岩体积系数，Rsh:泥岩电阻率"
    Rt,Rw,P,Vsh,Rsh=list(map(numpy.array,[Rt,Rw,P,Vsh,Rsh]))
    c=(0.81*Rw/Rt-Vsh*Rw/(0.4*Rsh))
    return c

def Archie(Rt,Rw,P,a=1,b=1,m=2,n=2):
    "Rt:地层电阻率，Rw:地层水电阻率，P：孔隙度，a,b:岩性系数默认为1，m孔隙度指数默认为2，n饱和度指数默认为2"
    Rt,Rw,P,a,b,m,n=list(map(numpy.array,[Rt,Rw,P,a,b,m,n]))
    sw=(a*b*Rw/((P**m)*Rt))**(1/n)
    return sw

if __name__ =="__main__":
    p=Smd(1,2,3,5,5)
    d=Archie(1,2,3,5,4)
    print(p)
    print(d)
else:
    pass
