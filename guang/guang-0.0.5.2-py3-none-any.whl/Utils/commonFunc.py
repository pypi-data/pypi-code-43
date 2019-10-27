def gaussian(x,sigma,miu):
    """
    标准高斯函数
    x可以是标量或者矢量
    """
    a = 1/np.sqrt(2*np.pi*sigma**2)
    return a* np.exp(-(x-miu)**2/(2*sigma**2))

def gauss2d(U, V, sigma, miu):
    '''
    This function will map x to Gaussian curve.
    input: 
        x is a 2D numpy Array. 
        sigma and miu are be used to discribe the shape of Normal distribution.
    output:
        The map of x
    '''
    a = 1/np.sqrt(2*np.pi*sigma**2) 
    res_max = a* np.exp(-((0-miu)**2+(0-miu)**2)/(2*sigma**2))#For normalization
    res = a* np.exp(-((U-miu)**2+(V-miu)**2)/(2*sigma**2))
    return res/res_max # Normalized

def butter(U,V,n,m):
    '''
    input:
        n the order of butterwith. range: 1~10
        m range: 1~100
    '''
    return 1/(1+(np.sqrt(U**2+V**2)/m)**(2*n))

def sawtooth(n,x):
    '''
    锯齿函数sawtooth的傅里叶级数为 sin(nx)/n ,n从一累加到无穷 
    '''
    S=np.zeros(x.shape)
    for i in range(1,n+1):
        s=np.sin(i*x)/i
        S+=s

    return S