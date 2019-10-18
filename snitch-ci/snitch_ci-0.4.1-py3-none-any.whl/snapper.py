import time
import logging as log

from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal

class Snapper(QWidget):
    area_captured = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__(None, Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.begin = QPoint()
        self.end = QPoint()

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget = QtWidgets.QLabel('', self)
        self.layout.addWidget(self.widget)
        self.widget.setStyleSheet('background: rgba(0, 0, 0, .1);')
        self.setGeometry(30, 30, 800, 450)
        self.showFullScreen()


    def _reset(self):
        self.begin = QPoint()
        self.end = QPoint()

    # pylint: disable=unused-argument
    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(255, 192, 192, 60))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.close()

        x = min(self.begin.x(), self.end.x())
        y = min(self.begin.y(), self.end.y())
        w = abs(self.begin.x() - self.end.x())
        h = abs(self.begin.y() - self.end.y())

        time.sleep(.1)
        log.info('Area captured X=%d Y=%d %dx%d', x, y, w, h)
        self.area_captured.emit(x, y, w, h)
