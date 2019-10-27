from PySide2.QtCore import QFile, QObject, Qt
from PySide2.QtWidgets import QPushButton
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon
import PySide2.QtXml  # DO NOT REMOVE, needed by QUiLoader


class UIWindow(QObject):
    def __init__(self, ui_file, window_icon: str = None, parent=None, frameless: bool = False):
        super(UIWindow, self).__init__(parent)

        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        if window_icon: self.window.setWindowIcon(QIcon(window_icon))

        if frameless:
            self.window.setWindowFlags(Qt.FramelessWindowHint)

    def make_borderless(self):
        self.window.setWindowFlags(Qt.FramelessWindowHint)
        DragBar(self.window)
        self.window.show()

    def show(self):
        self.window.show()


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    from GUILib import DragBar
    import sys

    app = QApplication()
    main_form = UIWindow('examples/wizard.ui', "examples/icon.png")
    main_form.window.findChild(QPushButton, "button").clicked.connect(lambda: main_form.make_borderless())
    main_form.window.show()
    sys.exit(app.exec_())
