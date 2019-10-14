from PyQt5.QtCore import pyqtSlot

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.deviceNumAttributeTemplate import Ui_Form


class DeviceNumAttributeWidget(Ui_Form, DeviceWidget, StackableWidget):
    attribute = None
    input_value = None

    def __init__(self, device, attribute, model_image=None, config=None, parent=None):
        self.attribute = Attribute.list_attribute(attribute)
        self.value_controls = []
        DeviceWidget.__init__(self, device, model_image=model_image, config=config, parent=parent)
        if self.config.get("unit", None) is not None:
            AttributeDeviceDisplayWidget.user_attribute_units[(self.device_id, tuple(self.attribute))] = config["unit"]

        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)

    @pyqtSlot()
    def set_status_label(self, status):
        self.label_status.setText(status)
        self.label_status.setStyleSheet("QLabel {{background:{}}}".format(self.get_status_color(status)))

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        self.input_value = AttributeDeviceDisplayWidget(self.device_id, self.attribute, config=self.config)
        layout.insertWidget(4, self.input_value)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.value_controls = (
            self.button_minus_double, self.button_minus, self.button_plus, self.button_plus_double,
            self.input_value)

        self.input_value.attribute_widget.sig_unit_changed.connect(self.unit_changed)

    @pyqtSlot("QString", "QString")
    def unit_changed(self, old_units, new_units):
        if old_units is None or new_units is None:
            self.input_step_size.setValue(1)
        else:
            current_value = self.input_step_size.value()
            current_value = units.Quantity(current_value, old_units).to(new_units)
            self.input_step_size.setValue(current_value.m)

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.setEnabled(value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            self.setEnabled(True)
            if value == STATUS_BUSY:
                for widget in self.value_controls:
                    widget.setEnabled(False)
                self.button_stop.setEnabled(True)
            else:
                for widget in self.value_controls:
                    widget.setEnabled(True)
                self.button_stop.setEnabled(False)
        else:
            self.setEnabled(False)

        self.set_status_label(value)

    @pyqtSlot()
    def decrease_value(self):
        step_size = self.input_step_size.value()
        return self.input_value - units.Quantity(step_size, self.input_value.get_unit())

    @pyqtSlot()
    def decrease_value_double(self):
        step_size = self.input_step_size.value()
        return self.input_value - (units.Quantity(step_size, self.input_value.get_unit()) * 10)

    @pyqtSlot()
    def increase_value(self):
        step_size = self.input_step_size.value()
        return self.input_value + units.Quantity(step_size, self.input_value.get_unit())

    @pyqtSlot()
    def increase_value_double(self):
        step_size = self.input_step_size.value()
        return self.input_value + (units.Quantity(step_size, self.input_value.get_unit()) * 10)

    @pyqtSlot()
    def stop(self):
        self.device.stop()

    def close(self):
        self.input_value.close()
        self.input_value = None
        super(DeviceNumAttributeWidget, self).close()
