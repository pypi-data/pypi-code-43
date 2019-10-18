from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from .diff_ui import Ui_Diff


class Diff(QWidget):
    """ Main window for the app """
    def __init__(self, reference_image, result_image, diff_image, parent=None):
        """
        :type reference_image: QPixmap
        :type result_image: QPixmap
        :type diff_image: QPixmap
        """
        super().__init__(parent)

        self._ui = Ui_Diff()
        self._ui.setupUi(self)

        self._ui.referenceImageLabel.setPixmap(reference_image)
        self._ui.resultImageLabel.setPixmap(result_image)

        self._result_image = result_image
        self._diff_image = diff_image

        self._ui.referenceScrollArea.verticalScrollBar().valueChanged.connect(
            self._ui.resultScrollArea.verticalScrollBar().setValue
        )
        self._ui.referenceScrollArea.horizontalScrollBar().valueChanged.connect(
            self._ui.resultScrollArea.horizontalScrollBar().setValue
        )
        self._ui.resultScrollArea.verticalScrollBar().valueChanged.connect(
            self._ui.referenceScrollArea.verticalScrollBar().setValue
        )
        self._ui.resultScrollArea.horizontalScrollBar().valueChanged.connect(
            self._ui.referenceScrollArea.horizontalScrollBar().setValue
        )


    @pyqtSlot()
    def swap_results(self):
        """ Shows/hides the differences highlighting """
        image = self._result_image
        if self._ui.highlightButton.isChecked():
            image = self._diff_image

        self._ui.resultImageLabel.setPixmap(image)
