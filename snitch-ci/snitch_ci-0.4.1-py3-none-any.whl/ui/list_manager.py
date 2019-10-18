from PyQt5.QtWidgets import QWidget

from .list_manager_ui import Ui_EventMgmtButtons

class EventMgmtButtons(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_EventMgmtButtons()
        self.ui.setupUi(self)
