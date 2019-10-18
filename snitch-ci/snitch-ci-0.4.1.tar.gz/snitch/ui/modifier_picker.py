from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from .modifier_picker_ui import Ui_ModifierCheckboxes

MODIFIERS = ('ctrl', 'shift', 'alt', 'alt_gr')

class ModifierCheckboxes(QWidget):
    """ A widget with 4 checkboxes for each of the 4 keyboard modifiers """
    values_changed = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_ModifierCheckboxes()
        self.ui.setupUi(self)

    def _get_values(self):
        """
        :return: A list of four bool in the same order than MODIFIERS showing
                 the check state of the matching QCheckBox
        """
        return [chkbx.isChecked() for chkbx in self._get_checkbox_list()]

    def _get_checkbox_list(self):
        """
        :return: The list of QCheckBoxes of this widget, in the same order
                 than MODIFIERS
        """
        return [getattr(self.ui, name+'CheckBox') for name in MODIFIERS]

    def values(self):
        """ :retrun: The subset of MODIFIERS which are actually checked """
        return [MODIFIERS[i] for i in range(len(MODIFIERS)) if self._get_values()[i]]

    def set_values(self, values):
        """ :type values: list of str to pick in MODIFIERS """
        original_values = self._get_values()
        for m, widget in zip(MODIFIERS, self._get_checkbox_list()):
            widget.setChecked(m in values)

        if original_values != self._get_values():
            self.values_changed.emit()
