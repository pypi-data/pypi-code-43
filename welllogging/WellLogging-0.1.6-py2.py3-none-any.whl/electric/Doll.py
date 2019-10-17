import numpy
import math
def gr(L,r):
    "横向微分几何因子，L：仪器探测源距 r:横向探测距离"
    L,r=list(map(numpy.array,[L,r]))
    n=r/L
    m=1/((4*n**2)+1)**0.5
    K=0
    E=0
    for i in range(158):
        K=K+(1/(1-m**2*(math.sin(i*0.01))**2)**0.5)*0.01
    for i in range(158):
        E=E+((1-m**2*(math.sin(i*0.01))**2)**0.5)*0.01
    g=2*n*m/L*((1-m**2)*K+(2*m**2-1)*E)
    return g 



def Gr(L,r):
    "横向积分几何因子，L：仪器探测源距 r:横向探测距离"
    L,r=list(map(numpy.array,[L,r]))
    n=r/L
    m=1/((4*n**2)+1)**0.5
    K=0
    E=0
    for i in range(158):
        K=K+(1/(1-m**2*(math.sin(i*0.01))**2)**0.5)*0.01
    for i in range(158):
        E=E+((1-m**2*(math.sin(i*0.01))**2)**0.5)*0.01
    G=1-(1+m**2)/(2*m)*E+(1-m**2)/(2*m)*K
    return G



def gz(L,z):
    "纵向微分几何因子，L：仪器探测源距 r:横向探测距离"
    if type(z)== int:
        if abs(z)<L/2:
            g=1/(2*L)
        else:
            g=L/(8*z**2)  
    else:
        z=numpy.array(z)
        g=[1/(2*L) if abs(i)<L/2  else L/(8*i**2) for i in z]
    return g

def Gz(L,z):
    "纵向积分几何因子，L：仪器探测源距 r:横向探测距离"
    if type(z)== int:
        if abs(z)<L/2:
            g=abs(z)/L
        else:
            g=1-L/(4*abs(z)) 
    else:
        z=numpy.array(z)
        g=[abs(i)/L if abs(i)<L/2 else 1-L/(4*abs(i)) for i in z]
    return g

if __name__=="__main__":
    print(gr(1,[0.1,2,5]))
    print(Gr(1,[0.1,5]))
    print(gz(1,1))
    print(Gz(1,[0.1,0.5]))