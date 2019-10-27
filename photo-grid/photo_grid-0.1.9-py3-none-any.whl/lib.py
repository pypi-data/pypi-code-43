# basic imports
import numpy as np
import sys
import math
import os
import pickle
import statistics

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
from scipy.signal import convolve2d
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D


def doKMeans(img, k=3, features=[0]):
    """
    ----------
    Parameters
    ----------
    """

    # data type conversion for opencv
    ## select features
    img = img[:, :, features].copy()
    ## standardize
    img_max, img_min = img.max(axis=(0, 1)), img.min(axis=(0, 1))-(1e-8)
    img = (img-img_min)/(img_max-img_min)
    ## convert to float32
    img_z = img.reshape((-1, img.shape[2])).astype(np.float32)
    
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    param_k = dict(data=img_z,
                   K=k,
                   bestLabels=None,
                   criteria=criteria,
                   attempts=10,
                   flags=cv2.KMEANS_PP_CENTERS)
    
    # KMEANS_RANDOM_CENTERS
    _, img_k_temp, center = cv2.kmeans(**param_k)
    
    # Convert back
    img_k = img_k_temp.astype(np.uint8).reshape((img.shape[0], -1))
    
    # return
    return img_k, center

def blurImg(image, n, cutoff=0.5):
    image = smoothImg(image=image, n=n)
    return binarizeSmImg(image, cutoff=cutoff)

def smoothImg(image, n):
    """
    ----------
    Parameters
    ----------
    """

    kernel = np.array((
            [1, 4, 1],
            [4, 9, 4],
            [1, 4, 1]), dtype='int')/29
   
    for _ in range(n):
        image = convolve2d(image, kernel, mode='same')

    return image

def binarizeSmImg(image, cutoff=0.5):
    """
    ----------
    Parameters
    ----------
    """
    imgOut = image.copy()
    imgOut[image > cutoff] = 1
    imgOut[image <= cutoff] = 0

    return imgOut.astype(np.int)

def cropImg(img, pts):
    """
    ----------
    Parameters
    ----------
    img : str
          path to the image file 
    pts : list of 2-tuple
          each tuple is a coordinate (x, y)
    -------
    Returns
    -------
    npImg : 3-d ndarray encoded in UINT8

    """

    # convert to opencv cpmatitable
    pts = np.array(pts).astype(np.float32)
    # find four corners
    token = True
    while token:
        try:
            order_x = np.argsort([pts[i, 0] for i in range(4)])
            order_y = np.argsort([pts[i, 1] for i in range(4)])
            pt_NW = pts[order_x[:2][np.isin(order_x[:2], order_y[:2])][0]]
            pt_SW = pts[order_x[:2][np.isin(order_x[:2], order_y[2:])][0]]
            pt_NE = pts[order_x[2:][np.isin(order_x[2:], order_y[:2])][0]]
            pt_SE = pts[order_x[2:][np.isin(order_x[2:], order_y[2:])][0]]
            token = False
        except:
            pts = rotatePts(pts, 15)
    # generate sorted source point
    pts = np.array([pt_NW, pt_NE, pt_SW, pt_SE])
    # estimate output dimension
    img_W = (sum((pt_NE-pt_NW)**2)**(1/2)+sum((pt_SE-pt_SW)**2)**(1/2))/2
    img_H = (sum((pt_SE-pt_NE)**2)**(1/2)+sum((pt_SW-pt_NW)**2)**(1/2))/2
    while (img_W > 1500):
        img_W /= 2
        img_H /= 2
    shape = (int(img_W), int(img_H))
    # generate target point
    pts2 = np.float32(
        [[0, 0], [shape[0], 0], [0, shape[1]], [shape[0], shape[1]]])
    # transformation
    M = cv2.getPerspectiveTransform(pts, pts2)
    dst = cv2.warpPerspective(img, M, (shape[0], shape[1]))
    dst = np.array(dst).astype(np.uint8)

    return dst

def rotatePts(pts, angle):
    """
    ----------
    Parameters
    ----------
    """
    ptx = np.array([pts[i, 0] for i in range(len(pts))])
    pty = np.array([pts[i, 1] for i in range(len(pts))])
    qx = math.cos(math.radians(angle))*(ptx) - \
        math.sin(math.radians(angle))*(pty)
    qy = math.sin(math.radians(angle))*(ptx) + \
        math.cos(math.radians(angle))*(pty)
    qpts = [[qx[i], qy[i]] for i in range(len(pts))]
    return np.array(qpts)

# === === === === === GRID pickle === === === === ===

def pickleGRID(obj, path):
    with open(path, "wb") as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)

def getPickledGRID(path):
    with open(path, "rb") as file:
        obj = pickle.load(file)
    
    return obj

# === === === === === rank === === === === ===


def getRank(array):
    """
    ----------
    Results
    ----------
    [1,3,6,2,4] -> [4,2,0,3,1]
    """
    sort = np.array(array).argsort()
    rank = np.zeros(len(sort), dtype=np.int)
    rank[sort] = np.flip(np.arange(len(array)), axis=0)
    return rank
# === === === === === peak searching === === === === ===

def rotateBinNdArray(img, angle):
    # create border for the image
    img[:, 0:2] = 1
    img[0:2, :] = 1
    img[:, -2:] = 1
    img[-2:, :] = 1

    # padding
    sizePad = max(img.shape)
    imgP = np.pad(img, [sizePad, sizePad], 'constant')

    # rotate
    pivot = tuple((np.array(imgP.shape[:2])/2).astype(np.int))
    matRot = cv2.getRotationMatrix2D(pivot, -angle, 1.0)
    imgR = cv2.warpAffine(
        imgP.astype(np.float32), matRot, imgP.shape, flags=cv2.INTER_LINEAR).astype(np.int8)

    # crop
    sigX = np.where(imgR.sum(axis=0) != 0)[0]
    sigY = np.where(imgR.sum(axis=1) != 0)[0]
    imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

    # return
    return imgC

def rotateVec(vec, angle):
    deg = np.pi/180
    x, y = vec[0], vec[1]
    xp = np.cos(deg*angle)*x - np.sin(deg*angle)*y
    yp = np.sin(deg*angle)*x + np.cos(deg*angle)*y
    return (xp, yp)

def getFourierTransform(sig):
    sigf = abs(np.fft.fft(sig)/len(sig))
    return sigf[2:int(len(sigf)/2)]
    # return sigf[2:25]

def getCardIntercept(lsValues, angle, imgH=0):
    if angle == 0:
        return lsValues*1
    else:
        coef = 1/np.sin(np.pi/180*abs(angle))
        if angle < 0:
            return lsValues*coef
        else:
            return imgH-lsValues*coef

def getLineABC(slope, intercept):
    if np.isinf(slope):
        A = 1
        B = 0
        C = intercept
    else:
        A = slope
        B = -1
        C = -intercept
    return A, B, C

def solveLines(slope1, intercept1, slope2, intercept2):
    A1, B1, C1 = getLineABC(slope1, intercept1)
    A2, B2, C2 = getLineABC(slope2, intercept2)
    D = A1*B2-A2*B1
    Dx = C1*B2-B1*C2
    Dy = A1*C2-C1*A2
    if D != 0:
        x, y = Dx/D, Dy/D
        return int(x), int(y)
    else:
        return False, False

def findPeaks(img, nPeaks=0, axis=1, nSmooth=100):
    """
    ----------
    Parameters
    ----------
    """
    
    # compute 1-D signal
    signal = img.mean(axis=(not axis)*1) # 0:nrow
    
    # ignore signals from iamge frame
    signal[0] = 0
    signal[-1] = 0

    # gaussian smooth 
    for _ in range(int(len(signal)/30)):
        signal = np.convolve(
            np.array([1, 2, 4, 2, 1])/10, signal, mode='same')

    # find primary peaks
    peaks, _ = find_peaks(signal)
    lsDiff = np.diff(peaks)
    medSig = statistics.median(signal[peaks])
    stdSig = np.array(signal[peaks]).std()
    medDiff = statistics.median(lsDiff)
    stdDiff = np.array(lsDiff).std()

    # get finalized peaks with distance constrain
    peaks, _ = find_peaks(signal, distance=medDiff-stdDiff/2, prominence=(0.01, None))
    if nPeaks != 0:
        if len(peaks) > nPeaks:
            while len(peaks) > nPeaks:
                ls_diff = np.diff(peaks)
                idx_diff = np.argmin(ls_diff)
                idx_kick = idx_diff if (
                    signal[peaks[idx_diff]] < signal[peaks[idx_diff+1]]) else (idx_diff+1)
                peaks = np.delete(peaks, idx_kick)
        elif len(peaks) < nPeaks:
            while len(peaks) < nPeaks:
                ls_diff = np.diff(peaks)
                idx_diff = np.argmax(ls_diff)
                peak_insert = (peaks[idx_diff]+peaks[idx_diff+1])/2
                peaks = np.sort(np.append(peaks, int(peak_insert)))

    return peaks, signal


# === === === === === Plotting === === === === ===

def pltCross(x, y, size=3, width=1, color="red"):
    pt1X = [x-size, x+size]
    pt1Y = [y-size, y+size]
    line1 = Line2D(pt1X, pt1Y, linewidth=width, color=color)
    pt2X = [x-size, x+size]
    pt2Y = [y+size, y-size]
    line2 = Line2D(pt2X, pt2Y, linewidth=width, color=color)    
    return line1, line2


def pltImShow(img, path=None, prefix="GRID", filename=".png"):
    if path is None:
        ax = plt.subplot(111)
        ax.imshow(img)
        plt.show()
    else:
        file = os.path.join(path, prefix+filename)
        if img.max()==1:
            qimg = getBinQImg(img)
        elif img.max() < 100:
            qimg = getIdx8QImg(img, img.max()+1)
        else:
            qimg = getRGBQImg(img)

        qimg.save(file, "PNG")


def pltSegPlot(agents, plotBase, isRect=False, path=None, prefix="GRID", filename=".png"):
    if path is None:
        ax = plt.subplot(111)
        ax.imshow(plotBase)
        for row in range(agents.nRow):
            for col in range(agents.nCol):
                agent = agents.get(row=row, col=col)
                if not agent:
                    continue
                recAg = agent.getQRect()
                line1, line2 = pltCross(agent.x, agent.y, width=1)
                ax.add_line(line1)
                ax.add_line(line2)
                if isRect:
                    rect = patches.Rectangle(
                        (recAg.x(), recAg.y()), recAg.width(), recAg.height(),
                        linewidth=1, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)
        plt.show()
    else:
        file = os.path.join(path, prefix+filename)
        qimg = getBinQImg(plotBase) if plotBase.max() == 1 else getRGBQImg(plotBase)

        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter = QPainter(qimg)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        for row in range(agents.nRow):
            for col in range(agents.nCol):
                agent = agents.get(row, col)
                rect = agent.getQRect()
                painter.drawRect(rect)
        painter.end()
        qimg.save(file, "PNG")

def pltImShowMulti(imgs, titles=None, vertical=False):
    nImgs = len(imgs)
    idxImg = 100 if vertical else 10
    idxLyt = 20 if vertical else 200

    plt.figure()
    for i in range(nImgs):
        idxPlot = idxImg*round(nImgs/2) + idxLyt + (i+1)
        plt.subplot(idxPlot)
        plt.imshow(imgs[i])
        try:
            plt.title(titles[i])
        except:
            None

    plt.show()

def pltLinesPlot(gmap, agents, img):
    itcs = gmap.itcs
    slps = gmap.slps
    # plotting
    _, ax = plt.subplots()
    ax.imshow(img)
    for i in range(2):
        for intercept in itcs[i]:
            plotLine(ax, slps[i], intercept)
    for cAgents in agents:
        for agent in cAgents:
            line1, line2 = pltCross(agent.x, agent.y, width=2)
            ax.add_line(line1)
            ax.add_line(line2)

    plt.show()

def plotLine(axes, slope, intercept):
    if abs(slope) > 1e+9:
        # vertical line
        y_vals = np.array(axes.get_ylim())
        x_vals = np.repeat(intercept, len(y_vals))
    else:
        # usual line
        x_vals = np.array(axes.get_xlim())
        y_vals = intercept + slope * x_vals
    axes.plot(x_vals, y_vals, '--', color="red")

def bugmsg(msg, title="DEBUG"):
    if "--test" in sys.argv:
        print("======%s=====" % title)
        print(msg)


# for GUI

def getRGBQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*3, QImage.Format_RGB888)
    return QPixmap(qImg)
    

def getBinQImg(img):
     h, w = img.shape[0], img.shape[1]
     qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Indexed8)
     qImg.setColor(0, qRgb(0, 0, 0))
     qImg.setColor(1, qRgb(241, 225, 29))
     return QPixmap(qImg)


def getIdx8QImg(img, k):
    colormap = [qRgb(228, 26, 28),
                qRgb(55, 126, 184),
                qRgb(77, 175, 74),
                qRgb(152, 78, 163),
                qRgb(255, 127, 0),
                qRgb(255, 255, 51),
                qRgb(166, 86, 40),
                qRgb(247, 129, 191),
                qRgb(153, 153, 153)]
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Indexed8)
    for i in range(k):
        qImg.setColor(i, colormap[i])
    return QPixmap(qImg)


def getGrayQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Grayscale8)
    return QPixmap(qImg)
