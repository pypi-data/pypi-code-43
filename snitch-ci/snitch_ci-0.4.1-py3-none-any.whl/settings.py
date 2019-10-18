from PyQt5.QtCore import QObject, pyqtSlot


class Settings(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.minimize_on_record = False

    @pyqtSlot(bool)
    def set_minimize_on_record(self, value):
        self.minimize_on_record = value

SETTINGS = Settings()
