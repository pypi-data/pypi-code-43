# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..lib import *
from ..grid import *
from .customQt import * 

class PnCropper(QGroupBox):
    """
    """

    def __init__(self, grid):
        """
        """

        super().__init__("Image Correction: Please click on the image to assign four anchors")
        self.setStyleSheet("""
        QGroupBox::title{
            subcontrol-origin: margin;
            subcontrol-position: top center;
        }
        """)

        # attr.
        self.grid = grid
        self.layout = QVBoxLayout()
        self.wgImg = Widget_ViewCrop(self.grid.imgs.get('raw'))
        self.initUI()

    def initUI(self):
        """
        """

        self.layout.addWidget(self.wgImg)
        self.setLayout(self.layout)
        self.show()

    def run(self):
        """
        """
        self.grid.cropImg(pts=self.wgImg.getPinnedPoints())

class Widget_ViewCrop(Widget_Img):

    def __init__(self, img):
        super().__init__()
        self.setMouseTracking(True)
        self.img_vis = img
        self.pos = None
        self.zoom = 1
        self.ratio = 1
        self.marks = []
        self.n_marks = 0
        self.imgH, self.imgW = img.shape[0], img.shape[1]
        self.initUI()

    def initUI(self):
        super().make_rgb_img(self.img_vis)
        self.show()

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        for pos in self.marks:
            drawCross(pos.x(), pos.y(), painter, 5)
        # coordinate
        # if self.pos is not None:
        #     painter.setFont(QFont("Trebuchet MS",14))
        #     painter.drawText(self.pos.x()-20, self.pos.y()+20, "(%d, %d)" %(self.pos.x(), self.pos.y()))
        painter.end()
        
    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.pos = pos
        magArea = int(min(self.rgX[1]-self.rgX[0], self.rgY[1]-self.rgY[0])/5)
        if self.zoom!=0:
            magnifying_glass(self, pos, area=magArea, zoom=self.zoom*1.5)
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.zoom = (self.zoom+1)%3
            self.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pt_mouse = event.pos()
        # determine the image boundary
        if event.button() == Qt.LeftButton:
            if self.isFitWidth:
                pt_1d = pt_mouse.y()
                bd_pos = self.rgY[0] + self.sizeImg.height()
                bd_neg = self.rgY[0]
            else:
                pt_1d = pt_mouse.x()
                bd_pos = self.rgX[0] + self.sizeImg.width()
                bd_neg = self.rgX[0]
            # if the click is in the image
            if (pt_1d >= bd_neg) & (pt_1d <= bd_pos):
                if self.n_marks<4:
                    self.marks.append(pt_mouse)
                    self.n_marks += 1
                else:
                    self.marks = []
                    self.n_marks = 0
            # bugmsg('(x:%d, y:%d)' % (pt_mouse.x()*(self.ratio), pt_mouse.y()*(self.ratio)))
            # bugmsg("ratio: %.2f" % (self.ratio))
            self.update()
        self.mouseMoveEvent(event)
        self.pos = None

    def getPinnedPoints(self):
        self.ratio = (self.imgW)/(self.width()) if self.isFitWidth else (self.imgH)/(self.height())
        pts = [[(pt.x()-self.rgX[0])*(self.ratio),
                (pt.y()-self.rgY[0])*(self.ratio)] for pt in self.marks]
        if len(pts)<4:
            pts = [[0, 0], [0, self.imgH], [self.imgW, 0], [self.imgW, self.imgH]]
        return pts
