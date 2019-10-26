import numpy as np 
'''
vec1 = np.array([1,1,1]).reshape(3,1)
vec2 = np.array([2,3,4]).reshape(3,1)
'''

class Dist:
    
    '''input: vec1 , vec2 均为列向量'''
    
    @staticmethod
    def euclidean_dist(vec1, vec2):
        """欧氏距离:
        我们现实所说的直线距离"""
        assert vec1.shape == vec2.shape 
        return np.sqrt((vec2-vec1).T @ (vec2-vec1))
    
    @staticmethod
    def manhattan_dist(vec1, vec2):
        """曼哈顿距离:
        城市距离"""
        return sum(abs(vec1 - vec2))
    
    @staticmethod
    def chebyshev_dist(vec1, vec2):
        """切比雪夫距离:
        国际象棋距离
        """
        return abs(vec1 - vec2).max()
    @staticmethod
    def minkowski_dist(vec1, vec2, p=2):
        """闵可夫斯基距离:
        应该说它其实是一组距离的定义: 
        inputParam: p
        return distance,
        while p=1: dist = manhattan_dist
        while p=2: dist = euclidean_dist
        while p=inf: dist = chebyshev_dist
        """
        s = np.sum(np.power(vec2 - vec1, p))
        return np.power(s,1/p)
    
    @staticmethod
    def cosine_dist(vec1, vec2):
        """夹角余弦"""
        # np.linalg.norm(vec, ord=1) 计算p=1范数,默认p=2
        return (vec1.T @ vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    @staticmethod
    def hamming_dist():
        pass
    
    @staticmethod
    def jaccard_simil_coef():
        pass
        
def is_similarity(vec1, vec2, dist_choise=2, tolerance=0.3):
    '''inputParam:
    dist_choise: 选择哪种距离, 1:P1范数(曼哈顿距离), 2: P2范数(欧氏距离), 3: P_inf范数(切比雪夫距离)
    tolerance: 相似度小于该值时会被判断为同类别,并 return True
    '''
    if dist_choise == 1:
        distance = Dist.manhattan_dist
    elif dist_choise == 2:
        distance = Dist.euclidean_dist
    elif dist_choise == 3:
        distance = Dist.chebyshev_dist
    else:
        raise 'dist_choise is a bad number'
        
    # 判断相似度:
    if distance(vec1, vec2) < tolerance:
        return True
    else:
        return False

def find_simil_idx(Vec_list, VEC,dist_choise=2, tolerance=0.3):
    '''
    Vec_list中每一个向量将与VEC向量比较, 最后返回所有与VEC相似向量下标列表
    '''
    IDX = []
    for idx, vec in enumerate(Vec_list):
        if is_similarity(vec, VEC,dist_choise, tolerance):
            IDX.append(idx)
    return IDX

def sort_count(lis):
    '''
    返回lis的由大到小排序好的元素列表
    Example:
    l = np.array([2,2,2,2,5,5,3,9,9])
    sort_count(l) : [(2, 4), (5, 2), (9, 2), (3, 1)]
    return [2, 5, 9,3], [4, 2, 2, 1]
    '''
    a = {}
    for i in lis:
        if i in a:
            a[i] = a[i] + 1
        else:
            a[i] = 1
    # 使用sorted对字典进行排序
    b = sorted(a.items(),key=lambda item:item[1],reverse=True)
    # idx, counts = [b[i][0] for i in range(len(b))], [b[i][1] for i in range(len(b))]
    return b




def simil_score(V1, w1, V2, w2, dist_choise=2, lamb=5, sigma=1):
    '''
    V1,w1对应Key color
    V2,w2对应待分类color
    可调节参数:
    lamb: 取值建议1~10,值越大表示颜色百分比所占权重越大
    sigma: 取值建议0~1.7, 值越小表示相似距离变大(小)时，相似度权重下降(上升)越快, 它的取值与 dist_choise相关:P1(0~3),P2(0~1.7),P3(0~1)
    output: 0~1之间的相似分数
    '''
    if dist_choise == 1:
        distance = Dist.manhattan_dist
    elif dist_choise == 2:
        distance = Dist.euclidean_dist
    elif dist_choise == 3:
        distance = Dist.chebyshev_dist
    else:
        raise 'dist_choise is a bad number'
    dis = 0
    Dis = 0
    for i1, v1 in enumerate(V1):
        for i2, v2 in enumerate(V2):
            dis_weight = 2.2 * gaussian(distance(v1, v2), sigma=sigma, miu=0)
            # if i1 == 0 and i2 == 0:
            #      print(f'第一个色块的相似度为{dis_weight}')

            W1, W2 = np.exp(lamb * w1[i1]), np.exp(lamb * w2[i2])
            dis += (W1 * W2) * dis_weight

            Dis_weight = 2.2 * gaussian(distance(v1, v1), sigma=sigma, miu=0)  # v1是key_color
            Dis += (W1 * W2) * Dis_weight
    #     m = (i1+1)*(i2+1)
    #     print(dis, Dis)
    return dis / Dis

def is_Centers_same(V1,w1,V2,w2,yourScore = 0.75, dist_choise=2,lamb = 5,sigma=1, **dic):
    '''
    V1,w1对应Key color, V通常是一个多Center的列表
    V2,w2对应待分类color
    可调节参数:
    lamb: 取值建议1~10,值越大表示颜色百分比所占权重越大
    sigma: 取值建议0~1.7, 值越小表示相似距离变大(小)时，相似度权重下降(上升)越快, 它的取值与 dist_choise相关:P1(0~3),P2(0~1.7),P3(0~1)
    output: 达到分数返回True 否则返回False
    '''
    # default Para
    printScore = 0

    if 'printScore' in dic:
        printSore = dic['printScore']

    score = simil_score(V1,w1,V2,w2,dist_choise=dist_choise,lamb = lamb,sigma=sigma)
    if printSore == 1:
        print(score)
    # 判断相似度:
    if score >= yourScore:
        return True
    else:
        return False


def find_centers_simil_idx(Centers1,Centers2,yourScore = 0.75, dist_choise=2,lamb = 5,sigma=1, **dic):
    '''
    Centers1将与每一个Centers2向量比较, 最后返回所有与Centers2相似向量下标列表
    '''
    # default Para
    printScore = 0

    if 'printScore' in dic:
        printScore = dic['printScore']

    V1,w1 = Centers1[0], Centers1[1]
    IDX=[]
    for idx,centers in enumerate(Centers2):
        V2,w2 = centers[0],centers[1]
        if is_Centers_same(V1, w1, V2, w2, yourScore=yourScore, dist_choise=dist_choise, lamb=lamb, sigma=sigma,printScore=printScore):
            IDX.append(idx)
    return IDX


def cvtBlackWhite(fileName):
    '''
    convert image's black color to white and meanwhile convert white to black.
    '''
    img = cv2.imread(fileName, 0)
    img = 255-img
    cv2.imwrite('convert_'+fileName, img)
    
def cvt2rgb(img,channel = 'bgr'):
    '''it can convert image channel BGR,BGRA,HLS,HSV to RGB'''
    if channel=='bgr' or channel=='BGR' or channel=='BGRA':
        print('bgr',img.shape)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif channel=='HLS' or channel=='hls':
        img = cv2.cvtColor(img, cv2.COLOR_HLS2RGB)
    elif channel=='HSV' or channel=='hsv':
        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    else:
        return 'bad channel'
    return img
    
def myplot(img,channel='bgr'):
    ''' can show image channel BGR,BGRA,HLS,HSV.
    if RGB, set channel = 0'''
    if channel:
        img = cvt2rgb(img, channel)
    plt.figure(figsize=(7,7))
    plt.imshow(img)
    plt.show()

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
    return out.astype('uint8')

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

# 查看图像HSV直方图
def get_img_hist(imgName):
    '''
    :param: imgName: the path of image
    :return: 
    '''
    img = cv2.imread(imgName)

    img = cv2.resize(img,(100,100),interpolation=cv2.INTER_CUBIC)
    H,S,V = cv2.split(cv2.cvtColor(img,cv2.COLOR_BGR2HSV))

    hist_h = np.bincount(H.ravel(), minlength=180) 
    hist_s = np.bincount(S.ravel(), minlength=256) 
    hist_v = np.bincount(V.ravel(), minlength=256) 
    
    hist_h = hist_h/ np.sum(hist_h) # normalization
    hist_s = hist_s/ np.sum(hist_s) # normalization
    hist_v = hist_v/ np.sum(hist_v) # normalization

    plt.figure(figsize=(9,9))
    plt.subplot(3,1,1); plt.plot(hist_h); plt.title('H')
    plt.subplot(3,1,2); plt.plot(hist_s); plt.title('S')
    plt.subplot(3,1,3); plt.plot(hist_v); plt.title('V')
    plt.show()