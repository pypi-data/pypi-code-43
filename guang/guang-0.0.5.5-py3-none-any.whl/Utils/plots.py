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