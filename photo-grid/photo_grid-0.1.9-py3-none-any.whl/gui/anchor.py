# basic imports
import numpy as np

# 3rd party imports 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from .customQt import *

class PnAnchor(QWidget):
    """
    """

    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        # compute
        self.grid.findPlots()

        # major 
        self.layout = QGridLayout()
        self.grRight = QGroupBox()
        self.wgImg = WidgetAnchor(grid)
        self.wgAxs = WidgetAxis()

        self.recImg = QRect(0, 0, 0, 0)
        self.recAxs = QRect(0, 0, 0, 0)
        self.recRight = QRect(0, 0, 0, 0)

        
        # Right Panel
        self.loRight = QVBoxLayout()
        
        # 2 axes
        self.grAxis = [QGroupBox("Axis 1"), QGroupBox("Axis 2")]
        self.loAxis = [QVBoxLayout(), QVBoxLayout()]
        self.grAg = [QGroupBox(), QGroupBox()]
        self.loAg = [QVBoxLayout(), QVBoxLayout()]
        self.dlAg = [QDial(), QDial()]
        self.grNum = [QGroupBox(), QGroupBox()]
        self.loNum = [QHBoxLayout(), QHBoxLayout()]
        self.lbNum = [QLabel("# of peaks"), QLabel("# of peaks")]
        self.spbNum = [QSpinBox(), QSpinBox()]

        self.mtp = 5 # for slider
        self.idxAx = 0

        # reset
        self.btReset = QPushButton("Reset")

        # mouse event
        self.idxAnc = -1
        self.ptX = -1

        # UI
        self.switch = True
        self.initUI()

        # show
        self.show()
        self.grAxis[0].setFocus(True)
        self.wgImg.updateDim()

    def initUI(self):

        # RIGHT: 2 axes
        for i in [0, 1]:
            # config
            angle = self.grid.map.angles[i]
            self.grAg[i].setTitle("Angle: %d degrees" % (angle))
            self.dlAg[i].setRange(-18, 18)
            self.dlAg[i].setValue(int(angle/5))
            self.dlAg[i].setPageStep(3)
            self.dlAg[i].setNotchesVisible(True)
            self.dlAg[i].setNotchTarget(5)
            self.spbNum[i].setValue(len(self.grid.map.itcs[i]))

            # assemble
            self.loAg[i].addWidget(self.dlAg[i])
            self.grAg[i].setLayout(self.loAg[i])
            
            self.loNum[i].addWidget(self.lbNum[i])
            self.loNum[i].addWidget(self.spbNum[i])
            self.grNum[i].setLayout(self.loNum[i])

            self.loAxis[i].addWidget(self.grAg[i])
            self.loAxis[i].addWidget(self.grNum[i])
            self.grAxis[i].setLayout(self.loAxis[i])
            self.grAxis[i].setCheckable(True)

            self.loRight.addWidget(self.grAxis[i])

        self.grAxis[0].setChecked(True)
        self.grAxis[1].setChecked(False)

        # RIGHT: functions  
        self.grAxis[0].clicked.connect(lambda: self.toggle(idx=0))
        self.grAxis[1].clicked.connect(lambda: self.toggle(idx=1))
        self.dlAg[0].valueChanged.connect(lambda: self.changeAngle(idx=0))
        self.dlAg[1].valueChanged.connect(lambda: self.changeAngle(idx=1))
        self.spbNum[0].valueChanged.connect(lambda: self.changePeaks(idx=0))
        self.spbNum[1].valueChanged.connect(lambda: self.changePeaks(idx=1))

        # RIGHT: comp
        self.loRight.addWidget(self.btReset)
        self.grRight.setLayout(self.loRight)

        # LEFT IMG: mouse tracking
        # self.wgImg.setMouseTracking(True)

        # Main
        policyRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyRight.setHorizontalStretch(1)
        self.grRight.setSizePolicy(policyRight)

        policyLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policyLeft.setHorizontalStretch(3)
        self.wgImg.setSizePolicy(policyLeft)
        self.wgAxs.setSizePolicy(policyLeft)

        sizeAxis = 9
        self.layout.addWidget(self.wgImg, 0, 0, sizeAxis, 1)
        self.layout.addWidget(self.wgAxs, sizeAxis, 0, 1, 1)
        self.layout.addWidget(self.grRight, 0, 1, sizeAxis+1, 1)

        self.setLayout(self.layout)
        # self.resize(1440, 1080)

    def paintEvent(self, event):
        try:
            self.updatePlots()
        except Exception as e:
            bugmsg(e)
        # '''rect'''
        # pen.setWidth(1)
        # pen.setColor(Qt.black)
        # painter.setPen(pen)
        # painter.setBrush(Qt.transparent)
        # painter.drawRect(self.rec_acr_c)
        # painter.drawRect(self.rec_acr_r)
 
    def updatePlots(self):
        bugmsg("update anchor")
        self.updateAnchor()
        bugmsg("update agent")
        self.updateAgents()
        bugmsg("done")

    def changeAngle(self, idx):
        bugmsg("ch angle %d" % idx)
        angle = self.dlAg[idx].value()*self.mtp
        angleOp = self.dlAg[1-idx].value()*self.mtp
        angleDiff = abs(angle-angleOp)
        if angleDiff!=0:
            if angleDiff > 90:
                value = min(angle+90, 90)/self.mtp if idx == 0 else max(-90, angle-90)/self.mtp
                self.dlAg[1-idx].setValue(int(value))
            elif angle*angleOp>0:
                angle = 0
                self.dlAg[idx].setValue(0)
            self.grAg[idx].setTitle("Angle: %d degrees" % (angle))
            self.grid.updateCenters(idx, angle=angle)
            self.switch = False
            self.spbNum[idx].setValue(len(self.grid.map.itcs[idx]))
            self.spbNum[1-idx].setValue(len(self.grid.map.itcs[1-idx]))
            self.switch = True
            self.wgImg.make_bin_img(self.grid.map.imgs[idx])
            self.repaint()
    
    def changePeaks(self, idx):
        if self.switch:
            bugmsg("ch peak")
            nPeaks = self.spbNum[idx].value()
            self.grid.updateCenters(idx, nPeaks=nPeaks)
            self.wgImg.make_bin_img(self.grid.map.imgs[idx])
            self.repaint()

    def toggle(self, idx):
        bugmsg("ch toggle")
        self.idxAx = idx
        self.wgImg.make_bin_img(self.grid.map.imgs[idx])
        self.grAxis[idx].setChecked(True)
        self.grAxis[int(not idx)].setChecked(False)
        self.repaint()

    def updateAnchor(self):
        ptsRaw = self.grid.map.sigs[self.idxAx]
        rgSrc = (0, self.grid.map.imgWr[self.idxAx])
        rgDst = self.wgImg.rgX
        pts = rescale(ptsRaw, rgSrc, rgDst)
        self.wgAxs.setPoints(pts)

    def updateAgents(self):
        # fetch info
        gmap = self.grid.map
        idxCr = self.idxAx
        idxOp = 1 - idxCr
        agCr = gmap.angles[idxCr]
        agOp = gmap.angles[idxOp]
        agDiff = agOp-agCr
        agAbs = abs(agDiff)
        
        imgH, imgW = gmap.imgs[idxCr].shape
        qimgH, qimgW = self.wgImg.sizeImg.height(), self.wgImg.sizeImg.width()
        ratio = sum([qimgW/imgW, qimgH/imgH])/2
        bugmsg(ratio)

        # current axis
        self.wgImg.ptVLine = self.wgAxs.pts

        # another axis
        self.wgImg.slp = 1 / np.tan(np.pi/180*agDiff)
        sigs = gmap.sigs[idxOp]

        if agCr % 90 == 0:
            bugmsg("case 1")
            itc = getCardIntercept(sigs, agDiff, imgH)
        elif agOp % 90 == 0:
            itc = np.cos(np.pi/180*agAbs)*gmap.imgHr[idxOp] + \
                    sigs/np.sin(np.pi/180*agAbs)
            if agDiff < 0:
                bugmsg("case 2")     
            else:
                bugmsg("case 3")
                itc = gmap.imgHr[idxCr] - itc
        else:
            seg1 = gmap.imgH*np.cos(np.pi/180*abs(agCr))
            seg2 = (sigs - gmap.imgH * np.sin(np.pi/180*abs(agOp))) / \
                np.sin(np.pi/180*(abs(agOp)+abs(agCr)))
            itc = seg1 + seg2
            if agCr > 0:
                bugmsg("case 4")
            else:
                bugmsg("case 5")
                itc = gmap.imgHr[idxCr] - itc

        self.wgImg.itcs = itc*ratio

        # slp = -1/np.tan(np.pi/180*agAbs) if agAbs < 0 else 1/np.tan(np.pi/180*agAbs)
        # sigs = self.grid.map.sigs[idxOp]
        # if idxOp==1:
        #     self.wgImg.slp = slp
        #     X = (sigs/np.sin(np.pi/180*agAbs)) + \
        #         np.cos(np.pi/180*agAbs)*self.grid.map.imgHr[idxOp]
        #     self.wgImg.itcs = (qimgH - X*ratio)
        # else:
        #     self.wgImg.slp = -slp
        #     segA = sigs/np.sin(np.pi/180*agAbs)
        #     segB = np.sin(np.pi/180*agAbs)*self.grid.map.imgWr[idxOp]
        #     self.wgImg.itcs = segA*ratio + (qimgW - segB*ratio)
        
    def updateDim(self):
        self.recImg = self.wgImg.geometry()
        self.recAxs = self.wgAxs.geometry()
        self.recRight = self.grRight.geometry()

    def getPtGui2Map(self, ptX):
        rgWg = self.wgImg.getImgRange()[0]
        rgMap = (0, self.grid.map.imgWr[self.idxAx]-1)
        return rescale(ptX-self.recAxs.x(), rgWg, rgMap)
        
    def mousePressEvent(self, event):
        pos = event.pos()
        self.updateDim()
        bugmsg(pos)
        bugmsg(self.recAxs)
        if self.recImg.contains(pos):
            bugmsg("img")
        if self.recAxs.contains(pos):
            self.ptX = self.getPtGui2Map(pos.x())
            self.idxAnc = np.abs(
                self.ptX-self.grid.map.sigs[self.idxAx]).argmin()
        if self.recRight.contains(pos):
            bugmsg("right")
    
    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.idxAnc != -1:
            if pos.x() > self.wgImg.rgX[0] and pos.x() < self.wgImg.rgX[1]:
                self.ptX = self.getPtGui2Map(pos.x())
            elif pos.x() <= self.wgImg.rgX[0]:
                self.ptX = 0
            elif pos.x() >= self.wgImg.rgX[1]:
                self.ptX = self.grid.map.imgW - 1
            self.grid.map.modAnchor(self.idxAx, self.idxAnc, self.ptX)
            self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        ptX = self.getPtGui2Map(pos.x())
        sig = np.array(self.grid.map.sigs[self.idxAx])
        if self.idxAnc != -1 and event.button() == Qt.RightButton and self.spbNum[self.idxAx].value() > 1:
            self.grid.map.delAnchor(self.idxAx, self.idxAnc)
            value = self.spbNum[self.idxAx].value() - 1
            self.switch = False
            self.spbNum[self.idxAx].setValue(value)
            self.switch = True
        elif self.ptX == ptX and event.button() == Qt.LeftButton and abs(sig-ptX).min() > sig.std()/20:
            self.grid.map.addAnchor(self.idxAx, ptX)
            value = self.spbNum[self.idxAx].value() + 1
            self.switch = False
            self.spbNum[self.idxAx].setValue(value)
            self.switch = True

        self.update()            
        self.ptX = -1
        self.idxAnc = -1
    
    def run(self):
        self.grid.agents.setup(gmap=self.grid.map, img=self.grid.imgs.get('binSeg'))

class WidgetAnchor(Widget_Img):
    def __init__(self, grid):
        super().__init__()
        self.ptVLine = []
        self.itcs = []
        self.slp = 0
        self.make_bin_img(grid.map.imgs[0])
    
    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        # vertical lines
        for pt in self.ptVLine:
            painter.drawLine(pt, self.rgY[0], pt, self.rgY[1])

        # lines from another axis
        for itc in self.itcs:
            x1, x2 = self.rgX 
            y1 = self.rgY[0] + itc
            y2 = y1 + (x2-x1)*self.slp
            pen.setWidth(1)
            pen.setStyle(Qt.DotLine) 
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
            pen.setWidth(5)
            painter.setPen(pen)
            for x in self.ptVLine:
                drawCross(x, y1+(x-x1)*self.slp, painter, size=5)

        bugmsg(self.itcs)
        painter.end()

class WidgetAxis(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.pts = []
    
    def setPoints(self, pts):
        self.pts = pts

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.red)
        # plot triangle 
        ptY = int(self.height()/2)
        for ptX in self.pts:
            drawTriangle(ptX, ptY, "North", painter)
        
        painter.end()


def rescale(values, scaleSrc=(0, 1), scaleDst=(0, 256)):
    values = np.array(values)
    return (values-scaleSrc[0])*(scaleDst[1]-scaleDst[0])/(scaleSrc[1]-scaleSrc[0])+scaleDst[0]
