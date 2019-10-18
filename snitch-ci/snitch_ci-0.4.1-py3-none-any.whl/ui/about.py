from PyQt5.QtWidgets import QDialog

from .about_ui import Ui_AboutDialog

class AboutDialog(QDialog):
    """ Information dialog """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)
