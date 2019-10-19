# basic imports
import numpy as np

# 3rd party imports 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..lib import *
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
            print(e)
        # '''rect'''
        # pen.setWidth(1)
        # pen.setColor(Qt.black)
        # painter.setPen(pen)
        # painter.setBrush(Qt.transparent)
        # painter.drawRect(self.rec_acr_c)
        # painter.drawRect(self.rec_acr_r)
 
    def updatePlots(self):
        print("update anchor")
        self.updateAnchor()
        print("update agent")
        self.updateAgents()
        print("done")

    def changeAngle(self, idx):
        print("ch angle %d" % idx)
        angle = self.dlAg[idx].value()*self.mtp
        angleOp = self.dlAg[1-idx].value()*self.mtp
        angleDiff = abs(angle-angleOp)
        if angleDiff!=0:
            if angleDiff > 90:
                value = min(angle+90, 90)/self.mtp if idx == 0 else max(-90, angle-90)/self.mtp
                self.dlAg[1-idx].setValue(int(value))
            self.grAg[idx].setTitle("Angle: %d degrees" % (angle))
            self.grid.updateCenters(idx, angle=angle)
            self.wgImg.make_bin_img(self.grid.map.imgs[idx])
            self.repaint()
    
    def changePeaks(self, idx):
        print("ch peak")
        nPeaks = self.spbNum[idx].value()
        self.grid.updateCenters(idx, nPeaks=nPeaks)
        self.wgImg.make_bin_img(self.grid.map.imgs[idx])
        self.repaint()

    def toggle(self, idx):
        print("ch toggle")
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
        idxCr = self.idxAx
        idxOp = int(not self.idxAx)
        agCr = self.grid.map.angles[idxCr]
        agOp = self.grid.map.angles[idxOp]
        agDiff = abs(agOp-agCr)

        imgH, imgW = self.grid.map.imgs[idxCr].shape
        qimgH, qimgW = self.wgImg.sizeImg.height(), self.wgImg.sizeImg.width()
        ratio = sum([qimgW/imgW, qimgH/imgH])/2
        print(ratio)

        # current axis
        self.wgImg.ptVLine = self.wgAxs.pts

        # another axis
        slp = 1/np.tan(np.pi/180*agDiff)
        sigs = self.grid.map.sigs[idxOp]
        if idxOp==1:
            self.wgImg.slp = slp
            X = (sigs/np.sin(np.pi/180*agDiff)) + \
                np.cos(np.pi/180*agDiff)*self.grid.map.imgHr[idxOp]
            self.wgImg.itcs = (qimgH - X*ratio)
        else:
            self.wgImg.slp = -slp
            segA = sigs/np.sin(np.pi/180*agDiff)
            segB = np.sin(np.pi/180*agDiff)*self.grid.map.imgWr[idxOp]
            self.wgImg.itcs = segA*ratio + (qimgW - segB*ratio)
        
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
        print(pos)
        print(self.recAxs)
        if self.recImg.contains(pos):
            print("img")
        if self.recAxs.contains(pos):
            self.ptX = self.getPtGui2Map(pos.x())
            self.idxAnc = np.abs(
                self.ptX-self.grid.map.sigs[self.idxAx]).argmin()
        if self.recRight.contains(pos):
            print("right")
    
    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.idxAnc != -1:
            self.ptX = self.getPtGui2Map(pos.x())
            print(self.recAxs)
            print("pos %d; ptX %d" % (pos.x(), self.ptX))
            self.grid.map.modAnchor(self.idxAx, self.idxAnc, self.ptX)
            self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        ptX = self.getPtGui2Map(pos.x())

        if self.idxAnc!= 1 and event.button()==Qt.RightButton:
            self.grid.map.delAnchor(self.idxAx, self.idxAnc)
        elif self.ptX==ptX and event.button()==Qt.LeftButton: 
            self.grid.map.addAnchor(self.idxAx, ptX)

        self.update()            
        self.ptX = -1
        self.idxAnc = -1

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
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
            pen.setWidth(5)
            painter.setPen(pen)
            for x in self.ptVLine:
                drawCross(x, y1+(x-x1)*self.slp, painter, size=5)

        print(self.itcs)
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

class ARCHIVE():
    def __init(self):
        # attribute
        # self.grid = grid

        # mouse
        self.idx_click = -1
        self.pos_temp = QPoint(0, 0)
        self.state_hand = False
        self.cursor = QCursor(Qt.ArrowCursor)

        # size/rec
        self.size_self = QSize(0, 0)
        self.size_imgPan = QSize(0, 0)
        self.size_img = QSize(0, 0)

        # anchor
        self.rec_acr_c = QRect(0, 0, 0, 0)
        self.rec_acr_r = QRect(0, 0, 0, 0)

        # image
        self.margin = 70
        self.space = 5
        self.rec_img = QRect(QPoint(0, 0), QSize(0, 0))

        # button
        self.gr_button = QGroupBox("Options")
        self.lo_button = QGridLayout()
        self.bt_evenH = QCheckBox("Evenly Distributed (X)")
        self.bt_evenV = QCheckBox("Evenly Distributed (Y)")
        self.bt_reset = QPushButton("Reset")

        # get plots from GRID
        self.grid.findPlots()

        # initialize UI
        self.initUI()

    def initUI(self):
        '''image'''
        self.qimg = getBinQImg(self.grid.imgs.get("bin"))
        '''button'''
        self.bt_reset.clicked.connect(self.reset_Anchors)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.bt_reset)
        box_bt = QHBoxLayout()
        box_bt.addStretch(1)
        box_bt.addLayout(vbox)
        self.setLayout(box_bt)
        self.show()

    def mousePressEvent(self, event):
        pos = event.pos()
        self.pos_temp = QPoint(pos.x(), pos.y())
        if self.rec_acr_c.contains(pos):
            self.idx_click = (np.abs(self.x_acr_c-pos.x())).argmin()
            if event.button() == Qt.RightButton:
                self.grid.map.delRatio(dim=1, index=self.idx_click)
        elif self.rec_acr_r.contains(pos):
            self.idx_click = (np.abs(self.y_acr_r-pos.y())).argmin()
            if event.button() == Qt.RightButton:
                self.grid.map.delRatio(dim=0, index=self.idx_click)
        elif event.button() == Qt.RightButton:
            # mag module
            self.zoom = (self.zoom+1)%3
            self.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        # add new anchors
        if (pos.x()==self.pos_temp.x())&(pos.y()==self.pos_temp.y())&(event.button()==Qt.LeftButton):
            if self.rec_acr_c.contains(pos):
                print("add")
                correct = 0 if self.is_fit_width else self.pt_st_img
                new_acr_c = (pos.x()-correct)/(self.size_img.width())
                self.grid.map.addRatio(dim=1, value=new_acr_c)
            elif self.rec_acr_r.contains(pos):
                print("add")
                correct = self.pt_st_img if self.is_fit_width else 0
                new_acr_r = (pos.y()-correct)/(self.size_img.height())
                self.grid.map.addRatio(dim=0, value=new_acr_r)
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        correctX = 0 if self.is_fit_width else self.pt_st_img
        correctY = self.pt_st_img if self.is_fit_width else 0
        if event.buttons() == Qt.LeftButton:
            if self.rec_acr_c.contains(pos):
                self.grid.map.modRatio(dim=1, index=self.idx_click, value=(
                    pos.x()-correctX)/self.size_img.width())
            elif self.rec_acr_r.contains(pos):
                self.grid.map.modRatio(dim=0, index=self.idx_click, value=(
                    pos.y()-correctY)/self.size_img.height())
            self.update()
        if (self.rec_acr_c.contains(pos)) or (self.rec_acr_r.contains(pos)):
            self.cursor = QCursor(Qt.PointingHandCursor)
            self.setCursor(self.cursor)
        elif self.rec_img.contains(pos):
            # mag module
            if self.zoom!=0:
                magnifying_glass(self, pos, area=200, zoom=self.zoom*1.5)
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def evenH(self):
        if self.bt_evenH.isChecked():
            size = len(self.acr_c)
            space = 0.02
            length = 1-(space*2)
            self.acr_c = np.arange(space, 1-space, length/size)
        else:
            self.acr_c = self.acr_c_raw
        self.update()

    def evenV(self):
        if self.bt_evenV.isChecked():
            size = len(self.acr_r)
            space = 0.02
            length = 1-(space*2)
            self.acr_r = np.arange(space, 1-space, length/size)
        else:
            self.acr_r = self.acr_r_raw
        self.update()

    def reset_Anchors(self):
        self.grid.map.resetRatio()
        self.update()

    def paintEvent(self, paint_event):
        '''painter'''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.red)
        '''sort array'''
        self.acr_c, self.acr_r = self.grid.map.getRatio()
        '''size info'''
        self.size_self = self.rect().size()
        self.size_imgPan = QSize(self.size_self.width()-self.margin, self.size_self.height()-self.margin)
        self.size_img = self.qimg.size().scaled(self.size_imgPan, Qt.KeepAspectRatio)
        '''Check the image side'''
        if self.size_img.width()==self.size_imgPan.width():
            '''image'''
            self.is_fit_width = True
            self.pt_st_img = int((self.size_imgPan.height()-self.size_img.height())/2)
            painter.drawPixmap(0, self.pt_st_img, self.size_img.width(), self.size_img.height(), self.qimg)
            '''anchor X'''
            self.x_acr_c = (self.acr_c*self.size_img.width()).astype(np.int)
            self.y_acr_c = self.pt_st_img+self.size_img.height()+(self.margin/5)
            '''anchor Y'''
            self.x_acr_r = self.size_self.width()-(self.margin*4/5)
            self.y_acr_r = (self.acr_r*self.size_img.height()+self.pt_st_img).astype(np.int)
            '''rect'''
            self.rec_acr_c = QRect(0, self.pt_st_img+self.size_img.height()+self.space, self.size_img.width(), self.margin)
            self.rec_acr_r = QRect(self.size_img.width()+self.space, self.pt_st_img, self.margin, self.size_img.height())
            self.rec_img = QRect(QPoint(0, self.pt_st_img), self.size_img)
        elif self.size_img.height()==self.size_imgPan.height():
            '''image'''
            self.is_fit_width = False
            self.pt_st_img = int((self.size_imgPan.width()-self.size_img.width())/2)
            painter.drawPixmap(self.pt_st_img, 0, self.size_img.width(), self.size_img.height(), self.qimg)
            '''anchor X'''
            self.x_acr_c = (self.acr_c*self.size_img.width()+self.pt_st_img).astype(np.int)
            self.y_acr_c = self.size_self.height()-(self.margin*4/5)
            '''anchor Y'''
            self.x_acr_r = self.pt_st_img+self.size_img.width()+(self.margin/5)
            self.y_acr_r = (self.acr_r*self.size_img.height()).astype(np.int)
            '''rect'''
            self.rec_acr_c = QRect(self.pt_st_img, self.size_img.height()+self.space, self.size_img.width(), self.margin-5)
            self.rec_acr_r = QRect(self.pt_st_img+self.size_img.width()+self.space, 0, self.margin-5, self.size_img.height())
            self.rec_img = QRect(QPoint(self.pt_st_img, 0), self.size_img)
        '''anchor'''
        # side
        for posX in self.x_acr_c:
            draw_triangle(posX, self.y_acr_c+self.space, "North", painter)
        for posY in self.y_acr_r:
            draw_triangle(self.x_acr_r+self.space, posY, "West", painter)
        # image
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        for posX in self.x_acr_c:
            for posY in self.y_acr_r:
                draw_cross(posX, posY, painter)
        '''rect'''
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rec_acr_c)
        painter.drawRect(self.rec_acr_r)
