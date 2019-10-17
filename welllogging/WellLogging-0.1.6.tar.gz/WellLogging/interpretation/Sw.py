"饱和度的计算，内置西门度(Smd)方法和阿尔齐(Archie)方程，以及Waxman-Smits方程。"
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

def WX(Rt,Rw,P,B,Qv,m=2,n=2,e=0.05,sw=0.5):
    "Rw为地层水电阻率，Rt为地层电阻率，P为孔隙度，n为饱和度指数，m为胶结指数，QV为每单位孔隙体积阳离子交换能力，B为交换阳离子的当量电导，m为孔隙度指数默认1.5，n为饱和度指数默认1.5，e为迭代精度默认0.05，sw为初始迭代含水饱和度默认为0.5"
    Rt,Rw,P,B,Qv,m,n,e,sw=list(map(numpy.array,[Rt,Rw,P,B,Qv,m,n,e,sw]))
    A=Rw*B*Qv
    print(A)
    C=(P**(-m))/Rt
    print(C)
    E=1
    while E>e:
        s1=sw-(sw*(A+sw)-C*sw**(2-n))/(n*sw+A*(n-1))
        E=abs(sw-s1)
        sw=s1
    return sw
    



if __name__ =="__main__":
    p=Smd(1,2,3,5,5)
    d=Archie(1,2,3,5,4)
    k=WX(10,1,0.3,30,20)
    print(p)
    print(d)
    print(k)
else:
    pass
