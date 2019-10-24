# -*- coding:utf-8 -*-
'''
@Author: lamborghini1993
@Date: 2019-10-16 15:43:53
@UpdateDate: 2019-10-24 20:53:50
@Description: UE4样式的Slider
1. 如果没有设置范围不显示百分比，设置了才会显示
2. 单机鼠标长按拖动可以调整数值，不可超过最大最小值，拖动时会隐藏鼠标箭头
3. 单机鼠标可以手动输入数值，手动输入时可超过设定范围
4. 无范围限制时会根据当前数值智能调整大小
对外接口：
    setRange/range
    setValue/value
    setSpeed
    setDecimals
    unlimit
对外信号:
    valueChanged
    editingFinished
'''

import sys
from PyQt5 import QtWidgets, QtCore, QtGui


def float_equal(a: float, b: float)->bool:
    if abs(a - b) < 1e-6:
        return True
    return False


class UE4Slider(QtWidgets.QWidget):
    MAX = 99999999
    valueChanged = QtCore.pyqtSignal(float)
    editingFinished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed = 1
        self.spin = None
        self.spinValue = 0
        self.spinRange = (-self.MAX, self.MAX)
        self.realRange = (-self.MAX, self.MAX)
        self.startpos = None
        self.bmove = False
        self.mousepos = None
        self.backcolor = QtCore.Qt.white
        self.frontcolor = QtGui.QColor(222, 111, 0)
        self._initSpin()
        self._init()

    def _init(self):
        self.resize(200, 30)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spin)

    def _initSpin(self):
        self.spin = QtWidgets.QDoubleSpinBox(self)
        self.spin.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spin.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.spin.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.spin.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spin.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.spin.setRange(*self.realRange)
        self.spin.editingFinished.connect(self.editingFinished.emit)

    def setRange(self, l, r):
        """设置滑动条范围"""
        self.spinRange = (l, r)

    def range(self):
        """获取滑动条范围"""
        return self.spinRange

    def setSpeed(self, speed):
        """设置滑动速度-灵敏度"""
        self.speed = speed

    def setValue(self, value):
        """设置值"""
        self.spinValue = value
        self.spin.setValue(value)
        self.valueChanged.emit(self.value())
        self.update()

    def value(self):
        """获取值"""
        return self.spinValue

    def setDecimals(self, prec: int):
        """设置精确到小数点位数"""
        self.spin.setDecimals(prec)

    def unlimit(self):
        """取消范围限制"""
        self.setRange(*self.realRange)

    def wheelEvent(self, wheelEvent):
        pass

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(QtCore.Qt.SizeHorCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setCursor(QtCore.Qt.ArrowCursor)

    def paintEvent(self, paintEvent):
        super().paintEvent(paintEvent)
        if self._is_not_limit():
            return
        painter = QtGui.QPainter(self)
        size = self.size()
        w, h = size.width(), size.height()
        minimum, maximum = self.spinRange
        w = (self.spinValue - minimum) * w / (maximum - minimum)
        pen = QtGui.QPen(self.frontcolor)
        brush = QtGui.QBrush(self.frontcolor)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(0, 0, w, h)
        painter.end()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.startpos = event.pos()
        self.mousepos = self.mapToGlobal(event.pos())
        self.bmove = False

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self.startpos:
            return
        self.setCursor(QtCore.Qt.BlankCursor)
        self.bmove = True
        pos = event.pos()
        movex = pos.x() - self.startpos.x()
        self._movex(movex)
        QtGui.QCursor.setPos(self.mousepos)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.startpos = None
        self.setCursor(QtCore.Qt.SizeHorCursor)
        if self.bmove:
            self.editingFinished.emit()
            return
        self.bmove = False
        self._start_editing()

    def _is_not_limit(self):
        minimum, maximum = self.spinRange
        if maximum <= minimum:
            return True
        if float_equal(-minimum, self.MAX) and float_equal(maximum, self.MAX):
            return True
        return False

    def _no_limit_add(self, x):
        value = abs(self.spinValue)
        base = 10
        if self.spinValue * x >= 0:
            result = value * x * self.speed / base
        else:
            result = value * x * self.speed / base / 2
        if float_equal(result, 0):
            result = self.speed * x / base / 10
        return result

    def _movex(self, x):
        minimum, maximum = self.spinRange
        if self._is_not_limit():    # 没有限制的情况下
            value = self.spinValue + self._no_limit_add(x)
        else:
            value = self.spinValue + (maximum - minimum) * x * self.speed / 100
        if value > maximum:
            value = maximum
        elif value < minimum:
            value = minimum
        self.setValue(value)

    def _start_editing(self):
        self.spin.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.spin.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.spin.editingFinished.connect(self._editing_finished)
        self.spin.setFocus()
        self.spin.selectAll()

    def _editing_finished(self):
        value = self.spin.value()
        self.spin.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spin.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.spin.editingFinished.disconnect(self._editing_finished)
        self.setFocus()
        self.setValue(value)


class SampleWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        hbox = QtWidgets.QVBoxLayout(self)
        self.min = QtWidgets.QLineEdit("0")
        self.max = QtWidgets.QLineEdit("0")
        self.slide = UE4Slider()
        self.slide.setDecimals(4)
        hbox.addWidget(self.slide)
        hbox.addWidget(self.min)
        hbox.addWidget(self.max)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.min.editingFinished.connect(self._Min)
        self.max.editingFinished.connect(self._Min)

    def _Min(self):
        minimum = float(self.min.text())
        maximum = float(self.max.text())
        if minimum < maximum:
            self.slide.setRange(minimum, maximum)
        else:
            self.slide.unlimit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    obj = SampleWidget()
    obj.show()
    sys.exit(app.exec_())
