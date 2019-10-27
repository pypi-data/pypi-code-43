# basic imports
import numpy as np
import pandas as pd

# self imports
from .io import *
from .lib import *

class GMap():
    """
    """
    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """
        
        # constant var
        self._degRot = range(-75, 90+1, 15)

        # map file
        self.pdMap = None
        self.isMap = False
        self.countNames = 0

        # dimension
        self.nAxs = [0, 0]
        self.nRow = 0
        self.nCol = 0
        self.img = None
        self.imgH = 0
        self.imgW = 0

        # axes
        self.angles = []
        self.slps = []  # 0 and 90 degrees for common images
        self.sigs = []
        self.itcs = []
        self.imgHr = []
        self.imgWr = []
        self.slpsReset = []
        self.itcsReset = []

        # iamges for two axes
        self.imgs = []

        # output
        self.dt = None

    def load(self, pathMap):
        """
        ----------
        Parameters
        ----------
        """

        self.pdMap = loadMap(pathMap)

        # if self.pdMap is not None:
        #     self.nRow, self.nCol = self.pdMap.shape
        #     self.isMap = True

    def findPlots(self, img, nRow=0, nCol=0, nSmooth=100):
        """
        ----------
        Parameters
        ----------
        """

        # get image info
        self.img = img
        self.imgH, self.imgW = img.shape[:2]
        isDimAssigned = (nRow != 0 and nCol != 0)
        
        # if dim is assigned regardless have map or not, force changning nR and nC 
        if isDimAssigned:
            self.nAxs = [nRow, nCol]

        # find angles and slopes
        self.angles = self.detectAngles(img=img, rangeAngle=self._degRot)

        # find intercepts and make centers as pandas DT
        self.locateCenters(img, nSmooth)

    def detectAngles(self, img, rangeAngle):
        # evaluate each angle
        sc = []
        for angle in rangeAngle:
            imgR = rotateBinNdArray(img, angle)
            sig = imgR.mean(axis=0)
            sigFour = getFourierTransform(sig)
            sc.append(max(sigFour))

        # angle with maximum score win
        scSort = sc.copy()
        scSort.sort()
        idxMax = [i for i in range(len(sc)) if (sc[i] in scSort[-2:])]
        angles = [rangeAngle[idx] for idx in idxMax]

        # return 
        return angles

    def locateCenters(self, img, nSmooth=100):
        self.slps = [1/np.tan(np.pi/180*angle) for angle in self.angles]
        # find intercepts given 2 angles
        self.itcs = self.getIntercepts(img, self.angles, self.nAxs, nSmooth)
        # get pandas data table
        self.dt = self.getDfCoordinate(img, self.angles, self.slps, self.itcs)

    def getIntercepts(self, img, angles, nSigs, nSmooth):   
        intercepts = []
        imgs = []
        sigs = []
        imghr = []
        imgwr = []
        for i in range(2):
            imgR, sig, intercept = self.cpuIntercept(
                img, angles[i], nSigs[i], nSmooth)
            sigs.append(sig)
            intercepts.append(intercept) 
            imgs.append(imgR)
            imghr.append(imgR.shape[0])
            imgwr.append(imgR.shape[1])
        
        self.imgs = np.array(imgs)
        self.sigs = np.array(sigs)
        self.imgHr = np.array(imghr)
        self.imgWr = np.array(imgwr)
        # return 
        return np.array(intercepts)

    def cpuIntercept(self, img, angle, nSig, nSmooth):
        imgR = rotateBinNdArray(img, angle)
        sig = findPeaks(img=imgR, nPeaks=nSig, nSmooth=nSmooth)[0]
        intercept = getCardIntercept(sig, angle, self.imgH)
        return imgR, sig, intercept


    def getDfCoordinate(self, img, angles, slopes, intercepts):
        """
        ----------
        Parameters
        ----------
        """
        imgH, imgW = img.shape
        tol = 0.025
        bdN, bdS = -imgH*tol, imgH*(1+tol)
        bdW, bdE = -imgW*tol, imgW*(1+tol)

        idxCol = 0 if abs(slopes[0]) > abs(slopes[1]) else 1
        idxRow = 1-idxCol
        idxMaj = 0 if getClosedTo0or90(angles[0]) <= getClosedTo0or90(angles[1]) else 1
        idxMin = 1-idxMaj

        for i in range(2):
            intercepts[i].sort()

        plotsMaj = []
        plotsMin = []
        pts = []

        pMaj = 0
        for itcMaj in intercepts[idxMaj]:  # columns
            pMin = 0
            for itcMin in intercepts[idxMin]:  # rows
                ptX, ptY = solveLines(
                    slopes[idxMaj], itcMaj, slopes[idxMin], itcMin)
                if ptX >= bdW and ptX <= bdE and ptY >= bdN and ptY <= bdS:
                    # outside the frame but within tolerant range
                    if ptX < 0:
                        ptX = 0
                    elif ptX >= imgW:
                        ptX = imgW-1
                    if ptY < 0:
                        ptY = 0
                    elif ptY >= imgH:
                        ptY = imgH-1
                    plotsMaj.append(pMaj)
                    plotsMin.append(pMin)
                    pts.append((ptX, ptY))
                    pMin += 1
            pMaj += 1
        
        if idxCol==idxMaj:
            dataframe = pd.DataFrame(
                {"row": plotsMin, "col": plotsMaj, "pt": pts})
        elif idxCol==idxMin:
            dataframe = pd.DataFrame(
                {"row": plotsMaj, "col": plotsMin, "pt": pts})

        self.nRow, self.nCol = dataframe['row'].max()+1, dataframe['col'].max()+1
        
        # update map names
        ctNA = 0
        names = []
        for _, entry in dataframe.iterrows():
            row = entry.row
            col = entry.col
            try:
                names.append(self.pdMap[row, col])
            except:
                names.append("NA_%d" % (ctNA))
                ctNA += 1
        dataframe['name'] = names

        # return
        return dataframe

    def getCoordinate(self, row, col):
        """
        ----------
        Parameters
        ----------
        """
        dt = self.dt
        return dt[(dt.row == row) & (dt.col==col)]['pt'].values[0]

    def getName(self, row, col):
        """
        ----------
        Parameters
        ----------
        """
        dt = self.dt
        return dt[(dt.row == row) & (dt.col == col)]['name'].values[0]

    def delAnchor(self, axis, index):
        # since numpy array required elements in same length if they were
        temp = self.sigs.tolist()
        try:
            temp[axis].remove(temp[axis][index])
        except:
            temp[axis] = np.delete(temp[axis], index)
        self.sigs = np.array(temp)
        temp = self.itcs.tolist()
        temp[axis] = getCardIntercept(
            self.sigs[axis], self.angles[axis], self.imgH)
        self.itcs = np.array(temp)
        self.dt = self.getDfCoordinate(self.img, self.angles, self.slps, self.itcs)

    def addAnchor(self, axis, value):        
        temp = self.sigs.tolist()
        try:
            temp[axis].append(value)
        except:
            temp[axis] = np.append(temp[axis], value)
        self.sigs = np.array(temp)
        temp = self.itcs.tolist()
        temp[axis] = getCardIntercept(
            self.sigs[axis], self.angles[axis], self.imgH)
        self.itcs = np.array(temp)
        self.dt = self.getDfCoordinate(self.img, self.angles, self.slps, self.itcs)

    def modAnchor(self, axis, index, value):
        self.sigs[axis][index] = value
        self.itcs[axis] = getCardIntercept(
            self.sigs[axis], self.angles[axis], self.imgH)
        self.dt = self.getDfCoordinate(
            self.img, self.angles, self.slps, self.itcs)

def getClosedTo0or90(x):
    s1 = abs(abs(x)-90)
    s2 = abs(abs(x))
    return min(s1, s2)

def scaleTo0and1(array, length):
    array = np.array(array)
    return array/length


def scaleToOrg(array, length):
    array = np.array(array)
    return array*length
