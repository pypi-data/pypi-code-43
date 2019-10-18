from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QPushButton, QSizePolicy, QLineEdit

from kamzik3 import DeviceError, units
from kamzik3.constants import *
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.deviceMethodTemplate import Ui_Form
from kamzik3.snippets.snippetsWidgets import show_error_message


class DeviceMethodWidget(Ui_Form, DeviceWidget, StackableWidget):
    attribute = None
    input_value = None

    def __init__(self, device, method, model_image=None, config=None, parent=None):
        self.method = method
        self.value_controls = ()
        DeviceWidget.__init__(self, device, model_image=model_image, config=config, parent=parent)
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
        self.input_value = self.method_widget()
        layout.insertWidget(2, self.input_value)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.value_controls = (self.input_value,)

    def method_widget(self):
        device_methods = self.device.exposed_methods
        method_widget = QWidget()

        def exec_method(method_name, argument_inputs=None):
            kwargs = {}
            for argument_input in argument_inputs:
                if isinstance(argument_input, AttributeDisplayWidget):
                    value = argument_input.get_attribute_value()
                    if isinstance(value, units.Quantity):
                        kwargs[argument_input.name] = "{:~}".format(value)
                    else:
                        kwargs[argument_input.name] = value
            try:
                getattr(self.device, method_name)(**kwargs)
            except DeviceError as e:
                show_error_message(e, parent=self)

        layout = QHBoxLayout(method_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for row, (method_name, method_attributes) in enumerate(device_methods):
            if method_name == self.method:
                method_label = QLabel(method_name + " (")
                method_label.setAlignment(Qt.AlignCenter | Qt.AlignRight)
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label)
                method_execute_button = QPushButton("< Call >")
                method_execute_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                argument_inputs = []
                if method_attributes:
                    inputs_widget = QWidget()
                    inputs_layout = QHBoxLayout()
                    inputs_widget.setLayout(inputs_layout)
                    for attribute_title, attribute_type in method_attributes.items():
                        device_attribute = self.device.get_attribute(attribute_type)
                        if device_attribute is None:
                            inputs_layout.addWidget(QLabel("{}".format(attribute_title)))
                            input_value = QLineEdit()
                            input_value.setPlaceholderText(attribute_type)
                            input_value.name = attribute_title
                            inputs_layout.addWidget(input_value)
                            argument_inputs.append(input_value)
                        else:
                            attribute_widget = AttributeDisplayWidget(attribute_title, device_attribute)
                            attribute_widget.name = attribute_title
                            inputs_layout.addWidget(attribute_widget.label_widget)
                            inputs_layout.addWidget(attribute_widget.input_widget)
                            inputs_layout.addWidget(attribute_widget.unit_widget)
                            argument_inputs.append(attribute_widget)
                    layout.addWidget(inputs_widget)
                else:
                    label = QLabel("None")
                    label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
                    label.setStyleSheet("QLabel {font-weight:bold}")
                    layout.addWidget(label)

                method_execute_button.released.connect(
                    lambda method_name=method_name, argument_inputs=argument_inputs: exec_method(method_name,
                                                                                                 argument_inputs))
                method_label = QLabel(")")
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label)
                layout.addWidget(method_execute_button)
                break

        return method_widget

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
    def stop(self):
        self.device.stop()

    def close(self):
        self.input_value.close()
        self.input_value = None
        super(DeviceMethodWidget, self).close()

class DeviceSimpleMethodsListWidget(DeviceMethodWidget):

    def __init__(self, device, methods_list, model_image=None, config=None, parent=None):
        self.methods_list = methods_list
        self.value_controls = []
        self.input_values = []
        DeviceWidget.__init__(self, device, model_image=model_image, config=config, parent=parent)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        layout.insertStretch(2)
        for required_method in reversed(self.methods_list):
            input_value = self.method_widget(required_method)
            layout.insertWidget(2, input_value)
            self.set_status_label(self.device.get_value(ATTR_STATUS))
            self.value_controls.append(input_value)
            self.input_values.append(input_value)


    def method_widget(self, required_method_name):
        device_methods = self.device.exposed_methods
        method_widget = QWidget()

        def exec_method(method_name, argument_inputs=None):
            kwargs = {}
            for argument_input in argument_inputs:
                if isinstance(argument_input, AttributeDisplayWidget):
                    value = argument_input.get_attribute_value()
                    if isinstance(value, units.Quantity):
                        kwargs[argument_input.name] = "{:~}".format(value)
                    else:
                        kwargs[argument_input.name] = value
            try:
                getattr(self.device, method_name)(**kwargs)
            except DeviceError as e:
                show_error_message(e, parent=self)

        layout = QHBoxLayout(method_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for row, (method_name, method_attributes) in enumerate(device_methods):
            if method_name == required_method_name:
                method_execute_button = QPushButton(method_name)
                method_execute_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                argument_inputs = []

                method_execute_button.released.connect(
                    lambda method_name=method_name, argument_inputs=argument_inputs: exec_method(method_name,
                                                                                                 argument_inputs))
                layout.addWidget(method_execute_button)
                break

        return method_widget

    def close(self):
        for input in self.input_values:
            input.close()
        self.input_values = None
        super(DeviceMethodWidget, self).close()