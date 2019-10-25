from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox
from pint import UndefinedUnitError

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.snippets.snippetsUnits import get_attribute_unit_range


class AttributeWidget(QWidget):
    input_widget = None
    unit_widget = None
    unit = None
    font_color = u"black"
    background_color = u"white"
    attribute = None
    attribute_type_cast = str
    sig_unit_changed = pyqtSignal("QString", "QString")

    def __init__(self, attribute, config=None, parent=None):
        assert isinstance(attribute, Attribute)
        self.attribute = attribute
        self.config = config
        if self.config is None:
            self.config = {}
        QWidget.__init__(self, parent=parent)
        self.setupUi()

    def _get_static_unit_widget(self):
        display_uint_name = self.attribute[UNIT]
        if display_uint_name == u"percent":
            display_uint_name = u"%"
        return QLabel(u" {}".format(display_uint_name))

    def _get_combox_unit_widget(self):
        unit_combobox = QComboBox()
        unit_combobox.addItems(
            get_attribute_unit_range(self.attribute)
        )

        def index_changed(_):
            self.set_unit(str(unit_combobox.currentText()))

        unit_combobox.currentIndexChanged.connect(index_changed)
        unit_combobox.wheelEvent = lambda *args: None
        index = unit_combobox.findText("{:~}".format(units.Unit(self.attribute[UNIT])))
        if index == -1:
            unit_combobox.setCurrentIndex(0)
        else:
            unit_combobox.setCurrentIndex(index)
        return unit_combobox

    def _set_unit_widget(self):
        self.unit = self.attribute[UNIT]
        if self.unit is not None:
            if self.unit in units.derived_units or self.config.get("static_unit", False):
                self.unit_widget = self._get_static_unit_widget()
            else:
                try:
                    self.unit_widget = self._get_combox_unit_widget()
                except (UndefinedUnitError, AttributeError, KeyError):
                    self.unit_widget = self._get_static_unit_widget()
        else:
            self.unit_widget = QLabel(u"")

    def set_tooltip(self, value=None):
        tooltip_value = self.attribute[DESCRIPTION]
        if tooltip_value is not None:
            tooltip_value += "\n" + value
        else:
            tooltip_value = value

        if tooltip_value is not None:
            self.input_widget.setToolTip(tooltip_value)

    def update_value(self):
        self.set_value(self.attribute.value())

    @pyqtSlot("PyQt_PyObject")
    def _set_input_widget(self):
        raise NotImplementedError("Has to be implemented")

    def get_attribute_value(self):
        raise NotImplementedError("Has to be implemented")

    def get_widget_value(self):
        raise NotImplementedError("Has to be implemented")

    def set_value(self, value):
        raise NotImplementedError("Has to be implemented")

    @pyqtSlot("QString")
    def set_unit(self, unit=None, reset=False):
        raise NotImplementedError("Has to be implemented")

    def get_unit(self):
        return self.unit

    def setDisabled(self, bool):
        self.input_widget.setDisabled(True)
        super().setDisabled(bool)

    def setupUi(self, parent=None):
        self.unit = self.attribute[UNIT]
        self._set_input_widget()
        self._set_unit_widget()

        if self.attribute[VALUE] is not None:
            self.set_value(self.attribute.value())

        if self.config is not None and self.config.get("unit") is not None:
            self.unit_widget.setCurrentText(self.config.get("unit"))
        self.input_widget.__dict__["update_value"] = self.update_value

    def close(self):
        if self.input_widget is not None:
            self.input_widget.setParent(None)
            del self.input_widget
        if self.unit_widget is not None:
            self.unit_widget.setParent(None)
            del self.unit_widget

        self.attribute = None
        self.config = None
        return super().close()
