from PySide2.QtWidgets import QLabel, QWidget


class DragBar(QLabel):
    def __init__(self, parent: QWidget, height=25):
        super().__init__(parent=parent)
        self.setFixedWidth(parent.size().width())
        self.setFixedHeight(height)
        self.move(0, 0)
        self.setStyleSheet("background-color : rgba(0,0,0,0)")
        self.__start_pos = None

    def mousePressEvent(self, ev):
        self.__start_pos = ev.pos()

    def mouseMoveEvent(self, ev):
        pos = self.mapToGlobal(ev.pos()) - self.__start_pos
        self.parent().move(pos.x(), pos.y())
