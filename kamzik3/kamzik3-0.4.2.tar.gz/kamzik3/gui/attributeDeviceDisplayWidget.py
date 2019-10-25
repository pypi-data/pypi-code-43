import time
from collections import deque

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox

from kamzik3 import units, DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.snippets.snippetsWidgets import show_error_message


class AttributeDeviceDisplayWidget(DeviceWidget, AttributeDisplayWidget):
    sigAttributeChanged = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    attribute = None
    # Global history for every device display attribute
    setpoints_history = deque(maxlen=100)
    # Global dictionary for last device, attribute unit
    user_attribute_units = {}

    def __init__(self, device, attribute, config=None, parent=None):
        self.initial_attribute = Attribute.list_attribute(attribute)
        self.config = config
        if self.config is None:
            self.config = {}
        self.title = self.initial_attribute[-1]

        if isinstance(device, Device):
            self.attribute_device_key = (device.device_id, tuple(self.initial_attribute))
        else:
            self.attribute_device_key = (device, tuple(self.initial_attribute))

        DeviceWidget.__init__(self, device, config=config, parent=parent)
        self.sigAttributeChanged.connect(self.slot_attribute_changed)

    def setupUi(self, parent=None):
        return

    def on_attribute_changed(self, key, value):
        self.sigAttributeChanged.emit(key, value)

    def get_current_user_unit(self):
        return AttributeDeviceDisplayWidget.user_attribute_units.get(self.attribute_device_key, None)

    @pyqtSlot("QString")
    def on_user_unit_changed(self, unit):
        AttributeDeviceDisplayWidget.user_attribute_units[self.attribute_device_key] = unit

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.input_widget.setEnabled(value)
        self.setEnabled(value)

    @pyqtSlot()
    def slot_observing_start(self):
        if self.device is not None:
            self.device.attach_attribute_callback(self.initial_attribute, self.on_attribute_changed,
                                                  self.config.get("max_update_rate"))
            self.device.attach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)
            self.setEnabled(self.device.get_value(ATTR_ENABLED))
            self.update_value()

    @pyqtSlot()
    def slot_observing_stop(self):
        if self.device is not None:
            self.device.detach_attribute_callback(self.initial_attribute, self.on_attribute_changed)
            self.device.detach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.attribute = self.device.get_attribute(self.initial_attribute)
        AttributeDisplayWidget.setupUi(self)

        if isinstance(self.unit_widget, QComboBox):
            current_user_unit = self.get_current_user_unit()
            if current_user_unit is not None:
                self.set_unit(current_user_unit)
            self.unit_widget.currentTextChanged.connect(self.on_user_unit_changed)

        self.input_widget.reset_on_blur = True
        self.slot_observing_start()

    def update_value(self):
        if self.attribute is not None:
            self.set_value(self.attribute.value())

    def hideEvent(self, hide_event):
        self.slot_observing_stop()
        DeviceWidget.hideEvent(self, hide_event)

    def showEvent(self, show_event):
        self.slot_observing_start()
        DeviceWidget.showEvent(self, show_event)

    def _add_in_setpoint_history(self, value):
        """
        Add setpoint into setpoint setpoints_history list.
        Each input is in format (epoch time, device ID, attribute name, previous value, current setpoint)
        :param value:
        :return:
        """
        previous_value = self.attribute.value()
        if previous_value is not None:
            previous_value = previous_value.to(self.get_unit())
        self.setpoints_history.append(
            (time.time(), self.device_id, self.initial_attribute, previous_value, value))

    def on_value_set(self, value):
        if isinstance(value, units.Quantity):
            self._add_in_setpoint_history(value)
            value = value.to(self.attribute[UNIT])
            self.logger.debug(u"Set {} to {}".format(self.initial_attribute, value))
            value = value.m
        elif self.attribute.numerical and self.get_unit() is not None:
            try:
                value = units.Quantity(value, self.get_unit())
                self._add_in_setpoint_history(value)
                self.logger.debug(u"Set {} to {}".format(self.initial_attribute, value))
                value = value.to(self.attribute[UNIT]).m
            except AttributeError:
                pass
        elif self.attribute[TYPE] == TYPE_LIST:
            value = self.get_widget_value()

        try:
            self.device.set_attribute(self.initial_attribute + [VALUE],
                                      self.attribute_widget.attribute_type_cast(value),
                                      callback=self.sigErrorCheck.emit)
        except DeviceError as e:
            show_error_message(e, parent=self)

        self.input_widget.setFocus()
        self.input_widget.clearFocus()
        self.parent().clearFocus()

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)
        if not self.isVisible():
            return
        elif value in READY_DEVICE_STATUSES:
            self.setEnabled(self.device.get_value(ATTR_ENABLED))
        elif value in (STATUS_DISCONNECTED, STATUS_DISCONNECTING):
            self.setDisabled(True)

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def slot_attribute_changed(self, key, value):
        if self.attribute is None:
            return
        if key == VALUE:
            if self.input_widget is not None and self.input_widget.hasFocus() or value is None:
                return
            if self.attribute.numerical:
                try:
                    self.set_value(units.Quantity(value, self.attribute[UNIT]))
                except AttributeError:
                    self.set_value(units.Quantity(value))
            else:
                self.set_value(value)
        elif key == UNIT:
            self.set_unit(value, reset=True)
        elif key == MIN:
            self.set_minimum(units.Quantity(value, self.attribute[UNIT]))
        elif key == MAX:
            self.set_maximum(units.Quantity(value, self.attribute[UNIT]))

    def close(self):
        self.sigAttributeChanged.disconnect()
        try:
            self.device.detach_attribute_callback(self.initial_attribute, self.on_attribute_changed)
            self.device.detach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)
        except:
            pass
        self.initial_attribute = None
        self.config = None
        DeviceWidget.close(self)
        AttributeDisplayWidget.close(self)
