# basic imports
import numpy as np

# self imports
from .io import *
from .lib import *

class GImage():
    """
    """

    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """

        # images
        self.imgs = {
            'raw'    : None,
            'rawRs'  : None,
            'crop'   : None,
            'mean'   : None,
            'kmean'  : None,
            'binOrg' : None,
            'binTemp': None,
            'binSd'  : None,
            'binSm'  : None,
            'bin'    : None,
            'binSeg' : None,
            'visSeg' : None
        }

        # dimension
        self.width, self.height, self.depth = 0, 0, 0
        self.widthRs, self.heightRs = 0, 0
        self.shape = (self.height, self.width, self.depth)
        self.shapeRs = (self.heightRs, self.widthRs, self.depth) 

        # kmean param.
        self.paramKMs = {
            'k' : -1,
            'center': None,
            'features': [],
            'lsSelect' : [],
            'lsKTobin' : [],
            'valShad' : -1,
            'valSmth' : -1
        }

    def get(self, key):
        """
        ----------
        Parameters
        ----------
        """

        return self.imgs[key]

    def set(self, key, value):
        """
        ----------
        Parameters
        ----------
        """

        self.imgs[key] = value

    def load(self, pathImg):
        """
        ----------
        Parameters
        ----------
        """

        isLocalImg = pathImg.find("http://") + pathImg.find("https://") == -2

        # image
        if isLocalImg:
            imgInput = loadImg(pathImg)
        else:
            imgInput = loadImgWeb(pathImg)

        # assign
        self.set(key='raw', value=imgInput)
        self.setShape(shape=imgInput.shape, isRaw=True)

    def getParam(self, key):
        """
        ----------
        Parameters
        ----------
        """

        return self.paramKMs[key]

    def setParam(self, key, value):
        """
        ----------
        Parameters
        ----------
        """

        self.paramKMs[key] = value
    
    def resetParam(self):
        """
        ----------
        Parameters
        ----------
        """

        self.paramKMs = {
            'k': -1,
            'center': None,
            'features': [],
            'lsSelect': [],
            'lsKTobin': [],
            'valShad': -1,
            'valSmth': -1
        }

    def crop(self, pts=None):
        """
        ----------
        Parameters
        ----------
        """

        if pts is None:
            self.set(key='crop',
                     value=self.imgs['raw'])
            self.set(key='mean',
                     value=self.get('crop')[:, :, :3].mean(axis=2))
            self.setShape(shape=self.get(key='crop').shape)
        else:
            self.set(key='crop',
                     value=cropImg(self.imgs['raw'], pts))
            self.set(key='mean',
                     value=self.get('crop')[:, :, :3].mean(axis=2))
            self.setShape(shape=self.get(key='crop').shape)

        self.resetParam()

    def doKMeans(self, k=3, features=[0, 1, 2]):
        """
        ----------
        Parameters
        ----------
        """

        # Will skip if no updates on the params         
        if (k != self.paramKMs['k']) or (features != self.paramKMs['features']):            
            imgK, center = doKMeans(img=self.get('crop'),
                                    k=k,
                                    features=features)
            self.set(key='kmean', value=imgK)
            # update parameters
            self.paramKMs['center'] = center
            self.paramKMs['k'] = k
            self.paramKMs['features'] = features
        else:
            # skip
            print("skip kmean")

    def binarize(self, k=3, features=[0, 1, 2], lsSelect=[0]):
        """
        ----------
        Parameters
        ----------
        """

        if (k != self.paramKMs['k']) or (features != self.paramKMs['features']) or (lsSelect != self.paramKMs['lsSelect']):
            ratioK = [(self.paramKMs['center'][i, 0]-self.paramKMs['center'][i, 1])/self.paramKMs['center'][i, :].sum()
                      for i in range(self.paramKMs['center'].shape[0])]
            # rankK = np.flip(np.argsort(ratioK), 0) 
            rankK = np.argsort(ratioK)
            try:
                clusterSelected = rankK[lsSelect]
            except:
                clusterSelected = []
            self.set(key='binOrg', value=(
                (np.isin(self.get('kmean'), clusterSelected))*1).astype(np.int))
            self.set(key='binTemp', value=self.get('binOrg').copy())
            self.set(key='binSm', value=self.get('binOrg').copy())
            # udpate parameters
            self.paramKMs['k'] = k
            self.paramKMs['features'] = features
            self.paramKMs['lsSelect'] = lsSelect
            self.paramKMs['lsKToBin'] = clusterSelected
        else:
            # skip
            print("skip binarize")
       
    def smooth(self, value):
        """
        ----------
        Parameters
        ----------
        """

        if value != self.paramKMs['valSmth']:
            valSmthDiff = value - self.paramKMs['valSmth']
            if valSmthDiff > 0:
                valSmthReal = valSmthDiff
            else:
                valSmthReal = value
                self.set(key='binTemp', value=self.get(key='binOrg').copy())      
            self.set(key='binTemp', value=smoothImg(image=self.get(key='binTemp'), n=valSmthReal))
            self.set(key='binSm',   value=binarizeSmImg(self.get(key='binTemp')))
            # update parameters
            self.paramKMs['valSmth'] = value
        else:
            # skip
            print("skip smoothing")

    def deShadow(self, value):
        """
        ----------
        Parameters
        ----------
        """

        if value != self.paramKMs['valShad']:
            self.set(key='binSd', value=(self.get(key='mean')>=value)*1)
            # update parameter
            self.paramKMs['valShad'] = value
        else:
            # skip
            print("skip shadow")

    def finalized(self):
        """
        ----------
        Parameters
        ----------
        """

        self.set(key='bin', value=np.multiply(
            self.get('binSm'), self.get('binSd')))

    def readyForSeg(self):
        """
        ----------
        Parameters
        ----------
        """
        self.set(key='binSeg', value=blurImg(self.get('bin'),
                                             n=int(min(self.height, self.width)/100)))
        # compute the vis/seg image
        imgTemp = self.get("bin").reshape(self.heightRs, self.widthRs, 1)
        imgSeg = np.multiply(self.get('crop')[:, :, :3], imgTemp).copy()
        imgSeg[(imgSeg.mean(axis=2) == 0), :] = 255
        self.set(key='visSeg', value=imgSeg)

    def rotate(self, nRot):
        """
        ----------
        Parameters
        ----------
        """

        for key in self.imgs.keys():
            if key == 'raw' or key == 'rawRs': continue
            try:
                self.set(key=key, value=np.rot90(self.get(key=key), nRot))
            except Exception as e:
                None

    def setShape(self, shape, isRaw=False):
        """
        ----------
        Parameters
        ----------
        """
        if isRaw:
            try:
                self.height, self.width, self.depth = shape
            except:
                self.height, self.width = shape
                self.depth = 1
            self.shape = (self.height, self.width, self.depth)
        else:
            try:
                self.heightRs, self.widthRs, self.depth = shape
            except:
                self.heightRs, self.widthRs = shape
                self.depth = 1
            self.shapeRs = (self.heightRs, self.widthRs, self.depth)

    def getShape(self, is3D=False, isRaw=False):
        """
        ----------
        Parameters
        ----------
        """
        if is3D:
            return self.shape if isRaw else self.shapeRs
        else:
            return self.shape[:2] if isRaw else self.shapeRs[:2] 
