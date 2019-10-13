"含水泥质砂岩孔隙度"
import numpy 
def PEG(b,ma,f,sh,Vsh):
    "b:测试点响应值，ma:砂岩响应值，f：流体响应值，sh:泥岩响应值，Vsh:泥岩体积系数"
    b,ma,f,sh,Vsh=list(map(numpy.array,[b,ma,f,sh,Vsh]))
    c=(ma-b)/(ma-f)-Vsh*(ma-sh)/(ma-f)
    return c

if __name__ =="__main__":
    p=PEG(1,2,3,5,8)
    print(p)
else:
    pass