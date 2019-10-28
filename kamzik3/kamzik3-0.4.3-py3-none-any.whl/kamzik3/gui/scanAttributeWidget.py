import math

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QButtonGroup

import kamzik3
from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.deviceDebugWidget import DeviceDebugWidget
from kamzik3.gui.general.lockButtonWidget import LockButton
from kamzik3.gui.general.macroWidget import MacroWidget
from kamzik3.gui.templates.scanAttributeTemplate import Ui_Form
from kamzik3.macro.scan import Scan
from kamzik3.macro.step import StepDeviceAttributeNumerical
from kamzik3.snippets.snippetsWidgets import show_error_message, show_centralized_top


class ScanAttributeWidget(Ui_Form, MacroWidget):
    device = None
    attribute = None
    debug_widget = None

    def __init__(self, title=None, config=None, parent=None):
        MacroWidget.__init__(self, parent)
        self.config = config
        if self.config is None:
            self.config = {}
        self.setupUi(self)
        self.button_settings.setEnabled(False)

        if self.config.get("input", "relative") == "relative":
            self.radio_relative_scan.setChecked(True)
        else:
            self.radio_absolute_scan.setChecked(True)

        self.end_point_lock_button = LockButton()
        self.end_point_set_widget = QWidget()
        lock_layout = QHBoxLayout(self.end_point_set_widget)
        lock_layout.setContentsMargins(0, 0, 0, 0)
        lock_layout.addWidget(self.end_point_lock_button)

        self.total_steps_lock_button = LockButton()
        self.total_steps_set_widget = QWidget()
        lock_layout = QHBoxLayout(self.total_steps_set_widget)
        lock_layout.setContentsMargins(0, 0, 0, 0)
        lock_layout.addWidget(self.total_steps_lock_button)

        self.step_size_lock_button = LockButton()
        self.step_size_set_widget = QWidget()
        lock_layout = QHBoxLayout(self.step_size_set_widget)
        lock_layout.setContentsMargins(0, 0, 0, 0)
        lock_layout.addWidget(self.step_size_lock_button)

        self.field_size_lock_button = LockButton()
        self.field_size_set_widget = QWidget()
        lock_layout = QHBoxLayout(self.field_size_set_widget)
        lock_layout.setContentsMargins(0, 0, 0, 0)
        lock_layout.addWidget(self.field_size_lock_button)

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        self.total_steps_lock_button.setDefault(True)
        self.total_steps_lock_button.setChecked(True)
        self.button_group.addButton(self.end_point_lock_button)
        self.button_group.addButton(self.total_steps_lock_button)
        self.button_group.addButton(self.step_size_lock_button)
        self.button_group.addButton(self.field_size_lock_button)

        self.spacer = self.gridLayout.itemAtPosition(5, 0)
        self.set_title(title)
        self._init_device_list()
        self._init_scanner_list()

        if self.config.get("attribute") is not None:
            self.label_attribute.hide()
            self.combobox_attribute.hide()

        self._init_template_settings()

    def _init_template_settings(self):
        if not self.config.get(CFG_TEMPLATE, False):
            self.label_settings.hide()
            self.widget_settings.hide()
            self.label_scanner.hide()
            self.combobox_scanner.hide()

    def _init_device_list(self):
        self.combobox_device.blockSignals(True)
        if self.config.get("attribute") is not None:
            attribute = self.config.get("attribute").split(u" # ")
            devices_list = list(kamzik3.session.get_devices(attribute_filter=attribute).keys())
        else:
            devices_list = list(kamzik3.session.get_devices().keys())

        self.combobox_device.addItems(["None"] + devices_list)
        self.combobox_device.blockSignals(False)

        if self.config.get("device_id") is not None:
            self.combobox_device.setCurrentText(self.config.get("device_id"))

    def _init_scanner_list(self):
        self.combobox_scanner.blockSignals(True)
        devices_list = list(kamzik3.session.get_devices(method_filter="get_scanner_macro").keys())

        self.combobox_scanner.addItems(["None"] + devices_list)
        self.combobox_scanner.blockSignals(False)

        if self.config.get("device_id") is not None:
            self.combobox_scanner.setCurrentText(self.config.get("device_id"))

    def _init_attribute_list(self, device):
        current_text = self.combobox_attribute.currentText()
        self.combobox_attribute.clear()
        self.combobox_attribute.blockSignals(True)
        if device is None:
            self.combobox_attribute.addItem("None")
        else:
            attribute_list = []
            self.get_scannable_attribute_list(device.attributes, attribute_list)
            if len(attribute_list) == 0:
                attribute_list.append("None")
            self.combobox_attribute.addItems(attribute_list)
        index = self.combobox_attribute.findText(current_text)
        if index == -1:
            self.combobox_attribute.setCurrentIndex(0)
        else:
            self.combobox_attribute.setCurrentIndex(index)
        self.combobox_attribute.blockSignals(False)
        self.attribute_selected(self.combobox_attribute.currentText())

    def get_scannable_attribute_list(self, attributes, output=[]):
        for k, v in attributes.items():
            if Attribute.is_attribute(v):
                if not v[READONLY] and v.numerical:
                    output.append(k)
            else:
                leaf = []
                self.get_scannable_attribute_list(v, leaf)
                output += map(lambda nk: "{} # {}".format(k, nk), leaf)

    def device_selected(self, device_id):
        if device_id == "None":
            self.device = None
            self._init_attribute_list(None)
            self.button_settings.setEnabled(False)
        else:
            self.button_settings.setEnabled(True)
            self.device = kamzik3.session.get_device(device_id)
            if self.config.get("attribute") is not None:
                self.attribute_selected(self.config.get("attribute"))
            else:
                self._init_attribute_list(self.device)

    def attribute_selected(self, attribute):
        if self.config.get(CFG_TEMPLATE, False):
            return

        for widget in self.macro_widgets:
            widget.close()
            widget.setParent(None)
        self.macro_widgets = []
        self.macro_inputs = {}

        # Remove all locked widgets
        self.end_point_set_widget.setParent(None)
        self.field_size_set_widget.setParent(None)
        self.step_size_set_widget.setParent(None)
        self.total_steps_set_widget.setParent(None)
        if attribute in ("", "None", None):
            # Don't show any widget if attribute is empty
            self.attribute = None
        else:
            attribute = attribute.split(u" # ")
            user_unit = AttributeDeviceDisplayWidget.user_attribute_units.get((self.device.device_id, tuple(attribute)),
                                                                              None)
            self.attribute = self.device.get_attribute(attribute)
            row = 3
            self.macro_widgets.append(self._show_total_steps_widget(row))
            row += 1
            self.macro_widgets.append(self._show_step_size_widget(row, user_unit))
            row += 1
            if self.radio_absolute_scan.isChecked():
                self.macro_widgets.append(self._show_start_point_widget(row, user_unit))
                row += 1
                self.macro_widgets.append(self._show_end_point_widget(row, user_unit))
            if self.radio_relative_scan.isChecked():
                row += 1
                self.macro_widgets.append(self._show_field_size_widget(row, user_unit))
            row += 1
            self.macro_widgets.append(self._show_negative_tolerance_widget(row, user_unit))
            row += 1
            self.macro_widgets.append(self._show_positive_tolerance_widget(row, user_unit))
            row += 1
            # self.macro_widgets.append(self._show_random_deviation_widget(row))
            # row += 1
            self.macro_widgets.append(self._show_wait_after_widget(row))
            row += 1
            self.macro_widgets.append(self._show_repeat_widget(row))
            row += 1
            self.macro_widgets.append(self._show_retry_widget(row))
            row += 1

            if self.config.get("scanner", "None") != "None":
                scanner = kamzik3.session.get_device(self.config["scanner"])
                scanner_attributes = scanner.get_scanner_attributes()
                for attribute in scanner_attributes:
                    self.macro_widgets.append(
                        self._show_method_attribute_widget(attribute, scanner.get_attribute(attribute).attribute_copy(),
                                                           row))
                    row += 1

            self.layout().removeItem(self.spacer)
            self.layout().addItem(self.spacer, row, 0)
            if self.radio_relative_scan.isChecked():
                self.signal_total_steps_changed(None)
            else:
                self.signal_absolute_total_steps_changed(None)

    """
    Signals and checks for absolute scan
    """

    def signal_start_end_changed(self, _):
        values = self.get_input_values()
        self.macro_inputs["step_size"].input_widget.blockSignals(True)
        self.macro_inputs["total_steps"].input_widget.blockSignals(True)
        field_size = values["end_point"] - values["start_point"]

        if self.step_size_lock_button.isChecked():
            try:
                self.macro_inputs["total_steps"].set_value(
                    units.Quantity(math.ceil(field_size / values["step_size"]))
                )
            except ZeroDivisionError:
                self.macro_inputs["total_steps"].set_value(units.Quantity(0))
        else:
            try:
                self.macro_inputs["step_size"].set_value(field_size / values["total_steps"])
            except ZeroDivisionError:
                self.macro_inputs["step_size"].set_value(units.Quantity(0, values["step_size"].u))

        self.macro_inputs["step_size"].input_widget.blockSignals(False)
        self.macro_inputs["total_steps"].input_widget.blockSignals(False)

    def signal_start_end_check_limits(self):
        values = self.get_input_values()
        if values["total_steps"] == 0 and values["step_size"] != 0:
            self.macro_inputs["end_point"].set_value(values["start_point"])

    def signal_absolute_step_size_changed(self, _):
        values = self.get_input_values()
        self.macro_inputs["end_point"].input_widget.blockSignals(True)
        self.macro_inputs["total_steps"].input_widget.blockSignals(True)
        field_size = values["end_point"] - values["start_point"]

        if self.total_steps_lock_button.isChecked():
            self.macro_inputs["end_point"].set_value(
                values["start_point"] + values["step_size"] * values["total_steps"])
        else:
            try:
                self.macro_inputs["total_steps"].set_value(
                    units.Quantity(math.ceil(field_size / values["step_size"]))
                )
            except ZeroDivisionError:
                self.macro_inputs["total_steps"].set_value(units.Quantity(0))

        self.macro_inputs["total_steps"].input_widget.blockSignals(False)
        self.macro_inputs["end_point"].input_widget.blockSignals(False)

    def signal_absolute_step_size_check_limits(self):
        values = self.get_input_values()
        field_size = values["end_point"] - values["start_point"]
        computed_end_point = values["start_point"] + (values["step_size"] * values["total_steps"])
        if abs(values["step_size"]) > abs(field_size):
            self.macro_inputs["step_size"].set_value(field_size)
        elif computed_end_point > (self.macro_inputs["end_point"].get_maximum() + values["step_size"]):
            try:
                self.macro_inputs["step_size"].set_value(
                    (self.macro_inputs["end_point"].get_maximum() - values["start_point"]) / values[
                        "total_steps"]
                )
            except ZeroDivisionError:
                self.macro_inputs["step_size"].set_value(units.Quantity(0, values["step_size"].u))
        elif computed_end_point == values["start_point"]:
            self.macro_inputs["step_size"].set_value(units.Quantity(0, values["step_size"].u))
        elif computed_end_point < (self.macro_inputs["end_point"].get_minimum() + values["step_size"]):
            self.macro_inputs["step_size"].set_value(field_size)

    def signal_absolute_total_steps_changed(self, _):
        values = self.get_input_values()
        self.macro_inputs["end_point"].input_widget.blockSignals(True)
        self.macro_inputs["step_size"].input_widget.blockSignals(True)
        field_size = values["end_point"] - values["start_point"]
        if self.step_size_lock_button.isChecked():
            self.macro_inputs["end_point"].set_value(
                values["start_point"] + values["step_size"] * values["total_steps"])
        else:
            try:
                self.macro_inputs["step_size"].set_value(field_size / values["total_steps"])
            except ZeroDivisionError:
                self.macro_inputs["step_size"].set_value(units.Quantity(0, values["step_size"].u))
        self.macro_inputs["step_size"].input_widget.blockSignals(False)
        self.macro_inputs["end_point"].input_widget.blockSignals(False)

    def signal_absolute_total_steps_check_limits(self):
        values = self.get_input_values()
        field_size = values["end_point"] - values["start_point"]
        if (values["total_steps"] * values["step_size"]) > self.macro_inputs["end_point"].get_maximum():
            self.macro_inputs["total_steps"].set_value(
                units.Quantity(math.ceil(field_size / values["step_size"]))
            )

    """
    Signals and checks for relative scan
    """

    def signal_field_size_changed(self, __):
        values = self.get_input_values()
        self.macro_inputs["step_size"].input_widget.blockSignals(True)
        self.macro_inputs["total_steps"].input_widget.blockSignals(True)
        if self.total_steps_lock_button.isChecked():
            try:
                self.macro_inputs["step_size"].set_value(
                    values["field_size"] / values["total_steps"]
                )
            except ZeroDivisionError:
                self.macro_inputs["step_size"].set_value(units.Quantity(0, self.attribute[UNIT]))
        else:
            try:
                self.macro_inputs["total_steps"].set_value(
                    units.Quantity(math.ceil(values["field_size"] / values["step_size"]))
                )
            except ZeroDivisionError:
                self.macro_inputs["total_steps"].set_value(units.Quantity(0))

        self.macro_inputs["step_size"].input_widget.blockSignals(False)
        self.macro_inputs["total_steps"].input_widget.blockSignals(False)

    def signal_field_size_check_limits(self):
        values = self.get_input_values()
        if values["field_size"] < values["step_size"]:
            self.macro_inputs["field_size"].set_value(values["step_size"])

    def signal_step_size_changed(self, __):
        values = self.get_input_values()
        self.macro_inputs["total_steps"].input_widget.blockSignals(True)
        self.macro_inputs["field_size"].input_widget.blockSignals(True)
        if self.field_size_lock_button.isChecked():
            try:
                self.macro_inputs["total_steps"].set_value(
                    units.Quantity(math.ceil(values["field_size"] / values["step_size"]))
                )
            except ZeroDivisionError:
                self.macro_inputs["total_steps"].set_value(units.Quantity(0))
        else:
            self.macro_inputs["field_size"].set_value(
                values["step_size"] * values["total_steps"]
            )
        self.macro_inputs["total_steps"].input_widget.blockSignals(False)
        self.macro_inputs["field_size"].input_widget.blockSignals(False)

    def signal_step_size_check_limits(self):
        values = self.get_input_values()
        if values["step_size"] > values["field_size"]:
            self.macro_inputs["step_size"].set_value(values["field_size"])
        elif (values["total_steps"] * values["step_size"]) > self.macro_inputs["field_size"].get_maximum():
            self.macro_inputs["step_size"].set_value(
                self.macro_inputs["field_size"].get_maximum() / values["total_steps"]
            )

    def signal_total_steps_changed(self, __):
        values = self.get_input_values()
        self.macro_inputs["step_size"].input_widget.blockSignals(True)
        self.macro_inputs["field_size"].input_widget.blockSignals(True)
        if self.step_size_lock_button.isChecked():
            self.macro_inputs["field_size"].set_value(
                values["total_steps"] * values["step_size"]
            )
        else:
            try:
                self.macro_inputs["step_size"].set_value(
                    values["field_size"] / values["total_steps"]
                )
            except ZeroDivisionError:
                self.macro_inputs["step_size"].set_value(units.Quantity(0, self.attribute[UNIT]))
        self.macro_inputs["step_size"].input_widget.blockSignals(False)
        self.macro_inputs["field_size"].input_widget.blockSignals(False)

    def signal_total_steps_check_limits(self):
        values = self.get_input_values()
        if values["field_size"] < values["step_size"]:
            self.macro_inputs["total_steps"].set_value(
                units.Quantity(1, values["step_size"].u)
            )
        if (values["total_steps"] * values["step_size"]) > self.macro_inputs["field_size"].get_maximum():
            self.macro_inputs["total_steps"].set_value(
                units.Quantity(math.ceil(self.macro_inputs["field_size"].get_maximum() / values["step_size"]))
            )

    def set_relative_scan(self, flag):
        if flag:
            if self.config.get("attribute") is not None:
                self.attribute_selected(self.config.get("attribute"))
            else:
                self.attribute_selected(self.combobox_attribute.currentText())

    def set_absolute_scan(self, flag):
        if flag:
            if self.config.get("attribute") is not None:
                self.attribute_selected(self.config.get("attribute"))
            else:
                self.attribute_selected(self.combobox_attribute.currentText())

    def save(self):
        values = self.get_input_values()
        try:
            if self.radio_relative_scan.isChecked():
                half_field_size = values["field_size"] / 2
                values["start_point"] = self.attribute.value() - half_field_size
                values["end_point"] = self.attribute.value() + half_field_size
            step_attributes = {
                "device_id": self.combobox_device.currentText(),
                "wait_after": values["wait_after"],
                "attribute": self.config.get("attribute").split(u" # "),
                "negative_tolerance": values["positive_tolerance"],
                "positive_tolerance": values["negative_tolerance"],
                "retry_count": int(values["retry_count"].m),
                "trigger_log": self.config.get("trigger_log", True)
            }
            if values["total_steps"] <= 0:
                raise ValueError("Total steps for {} has to be greater than zero.".format(self.title))

            scanner = self.config.get("scanner", "None")
            if scanner == "None":
                scanner = None
            scanner_attributes = {}
            if scanner is not None:
                scanner_device = kamzik3.session.get_device(scanner)
                for attribute in scanner_device.get_scanner_attributes():
                    scanner_attributes[attribute] = self.macro_inputs[attribute].get_attribute_value()
            if self.config.get("as_step", False):
                step_attributes["repeat_count"] = values["repeat"]
                scan = Scan("Scan", values["start_point"], values["end_point"], int(values["total_steps"].m),
                            step_class=StepDeviceAttributeNumerical, step_attributes=step_attributes, as_step=True,
                            bidirectional=self.config.get("bidirectional", False), scanner=scanner,
                            scanner_attributes=scanner_attributes, return_back=self.config.get("return_back", True))
            else:
                scan = Scan("Scan", values["start_point"], values["end_point"], int(values["total_steps"].m),
                            repeat_count=values["repeat"], step_class=StepDeviceAttributeNumerical,
                            step_attributes=step_attributes, as_step=False,
                            bidirectional=self.config.get("bidirectional", False), scanner=scanner,
                            scanner_attributes=scanner_attributes, return_back=self.config.get("return_back", True))
            return scan
        except KeyError:
            if self.combobox_device.currentText() == "None":
                raise KeyError("Device was not set for {}".format(self.title))
            else:
                raise KeyError("One of attributes for {} were not set".format(self.title))

    def get_template(self):
        if self.combobox_device.currentText() == "None":
            raise ValueError("Attribute cannot be set to None")
        if self.combobox_attribute.currentText() == "None":
            raise ValueError("Attribute cannot be set to None")

        return {
            "type": "iterative",
            "input": "relative" if self.radio_relative_scan.isChecked() else "absolute",
            "device_id": self.combobox_device.currentText(),
            "attribute": self.combobox_attribute.currentText(),
            "trigger_log": self.checkbox_log.isChecked(),
            "as_step": self.checkbox_as_step.isChecked(),
            "scanner": self.combobox_scanner.currentText(),
            "defaults": self.checkbox_defaults.isChecked(),
            "bidirectional": self.checkbox_bidirectional.isChecked(),
            "return_back": self.checkbox_return_back.isChecked()
        }

    def show_debug_widget(self):
        if self.device is None:
            show_error_message("No device selected", parent=self)
            return
        if self.debug_widget is None:
            self.debug_widget = DeviceDebugWidget(self.device)
        elif self.debug_widget.device != self.device:
            self.debug_widget.close()
            self.debug_widget.setParent(None)
            self.debug_widget.deleteLater()
            self.debug_widget = None
            self.debug_widget = DeviceDebugWidget(self.device)

        show_centralized_top(self.debug_widget)
