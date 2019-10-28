# 线性变换
def MaxMinNormal(I,out_min, out_max):
    '''
    input: 
        I: this vector to be scaled
        out_min : the minimun of out vector
        out_max : the maximun of out vector
    output:
        Scale param I to range [out_min, out_max] 
    '''
    Imax = I.max()
    Imin = I.min()
    out = out_min + (out_max - out_min)/(Imax - Imin) * (I-Imin)
    return out

# 伽马变换
def Gamma_trans(I, I_max, gamma):
    '''
    param:
        gamma: if your intersted region is too bright, set gamma > 1 decreasing contrast.
           and if your intersted region is too dark, set 1> gamma > 0 to increase contrast.
        I_max: is the maximun of the channel of I.
    return:
        the map of I
    '''
    fI = I/I_max
    out = np.power(fI, gamma)
    out = out*I_max
    return out