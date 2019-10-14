import logging
import time
from io import StringIO

import oyaml as yaml
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSlot, QModelIndex, pyqtSignal, QItemSelection
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QWidget, QTableView, QHeaderView, QFileDialog, QColorDialog
from pint import DimensionalityError

import kamzik3
from kamzik3 import DeviceError, DeviceUnknownError, units
from kamzik3.constants import *
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.templates.savedAttributesTemplate import Ui_Form
from kamzik3.snippets.snippetsUnits import device_units
from kamzik3.snippets.snippetsWidgets import show_error_message, show_question_dialog, show_prompt_dialog

# Example of file format
"""
Stages:
  columns:
  - !!python/tuple
    - Comment
    - ['', '']
  - !!python/tuple
    - Smaract_axis_0
    - [Position, Value]
  - !!python/tuple
    - Smaract_axis_1
    - [Position, Value]
  - !!python/tuple
    - Smaract_axis_2
    - [Position, Value]
  rows: []
"""


class ViewModel(QAbstractTableModel):

    def __init__(self, model_data, parent=None):
        self.model_data = model_data
        QAbstractTableModel.__init__(self, parent)

    def columnCount(self, parent=None, *args, **kwargs):
        columns = self.model_data.get("columns")
        if columns is None:
            return 0
        return len(columns)

    def rowCount(self, parent=None, *args, **kwargs):
        rows = self.model_data.get("rows")
        if rows is None:
            return 0
        return len(rows)

    def data(self, index, role=None):
        row, column = index.row(), index.column()

        if role == Qt.DisplayRole:
            return "{}".format(self.model_data["rows"][row][column + 2])
        elif role == Qt.BackgroundRole:
            return QBrush(QColor(self.model_data["rows"][row][0]))
        elif role == Qt.EditRole:
            current_value = self.model_data["rows"][index.row()][2]
            return current_value

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            data = self.model_data["columns"][p_int]
            header_text = "{} {}".format(data[0], data[1][-2])
            return header_text
        elif role == Qt.DisplayRole and Qt_Orientation == Qt.Vertical:
            return "{}".format(self.model_data["rows"][p_int][1])

    def setData(self, index, value, role=None):

        if role == Qt.EditRole and value != "":
            self.model_data["rows"][index.row()][2] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class SavedAttributesWidget(Ui_Form, DeviceWidget):
    default_row_color = "#ffffff"
    file_path = None
    sigUpdateData = pyqtSignal("PyQt_PyObject")

    def __init__(self, device=None, config=None, parent=None):
        if device is None:
            QWidget.__init__(self, parent)
        else:
            DeviceWidget.__init__(self, device, config=config, parent=parent)

        self.rows_selection_mode = False
        self.session = kamzik3.session
        self.current_data = {}
        self.preset_groups = {}
        self.current_preset_group = "Default"
        self.logger = logging.getLogger("Gui.Device.SavedAttributeWidget")

        self.manipulation_buttons = [self.button_set_value, self.button_change_color, self.button_move_top,
                                     self.button_move_up, self.button_move_down, self.button_move_bottom,
                                     self.button_remove]
        for button in self.manipulation_buttons:
            button.setDisabled(True)

        self.preset_group_buttons = (self.combo_preset, self.button_remove_preset_group, self.button_add_preset_group,
                                     self.button_add_preset_group_from_selected_rows)
        self.preset_rows_selection_buttons = (self.button_confirm_rows_selection, self.button_cancel_rows_selection)
        self.sigUpdateData.connect(self.update_data)
        self.tab_groups.currentChanged.connect(self.current_tab_changed)

        for button in self.preset_rows_selection_buttons:
            button.hide()

    def set_source_file(self, file_path):
        self.file_path = file_path
        with open(file_path, "r") as fp:
            self.current_data = yaml.load(fp, Loader=yaml.Loader)
            self.load_data(self.current_data)

    def set_source_file_device(self, file_sync_device):
        DeviceWidget.__init__(self, file_sync_device, self.parent(), setup_ui=False)
        self.file_path = None

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        if value in READY_DEVICE_STATUSES:
            self.slot_handle_configuration()
            file_content = self.device.get_value(ATTR_CONTENT)
            if file_content is not None:
                file_content = "".join(file_content)
                self.load_data(yaml.load(StringIO(file_content), Loader=yaml.Loader))

            self.device.attach_attribute_callback(ATTR_CONTENT, self.content_update)
            self.checkbox_synced_with_server.setChecked(True)
        elif value in (STATUS_DISCONNECTED, STATUS_DISCONNECTING):
            self.checkbox_synced_with_server.setChecked(False)

    def slot_handle_configuration(self):
        pass

    @pyqtSlot()
    def update_source(self):
        if self.device is not None:
            self.device.set_attribute((ATTR_CONTENT, VALUE), yaml.dump(self.preset_groups))
        elif self.file_path is not None:
            with open(self.file_path, "w") as fp:
                yaml.dump(self.preset_groups, fp, default_flow_style=False)

    @pyqtSlot()
    def content_update(self, key, value):
        if key == VALUE:
            self.sigUpdateData.emit(yaml.load(StringIO(value), Loader=yaml.Loader))

    @pyqtSlot("PyQt_PyObject")
    def load_data(self, data):
        while self.tab_groups.count() != 0:
            self.tab_groups.removeTab(0)

        self.preset_groups = data
        self.current_data = data["Preset groups"][self.current_preset_group]
        self.update_preset_groups(block_signals=True)

        for group_title, model_data in self.current_data.items():
            self.add_group(group_title, model_data)

    @pyqtSlot("PyQt_PyObject")
    def update_data(self, data):
        self.preset_groups = data
        self.current_data = self.preset_groups["Preset groups"][self.current_preset_group]
        self.update_preset_groups(block_signals=True)

        for index in range(self.tab_groups.count()):
            group_name = self.tab_groups.tabText(index)
            table = self.tab_groups.widget(index)
            table.model().model_data = self.current_data[group_name]
            table.model().layoutChanged.emit()

    def add_group(self, title, model_data):
        view_model = ViewModel(model_data)
        view_model.dataChanged.connect(self.data_changed)
        group_table = QTableView()
        group_table.setSelectionBehavior(group_table.SelectItems)
        group_table.setSelectionMode(group_table.SingleSelection)
        group_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        group_table.horizontalHeader().setStretchLastSection(True)
        group_table.setModel(view_model)
        group_table.doubleClicked.connect(self.on_double_click)
        group_table.selectionModel().selectionChanged.connect(self.current_selection_changed)
        self.tab_groups.addTab(group_table, title)
        return view_model

    @pyqtSlot(QModelIndex, QModelIndex)
    def data_changed(self, from_index, to_index):
        table = self.tab_groups.currentWidget()
        new_value = table.model().model_data["rows"][from_index.row()][from_index.column() + 2]
        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            table.model().model_data["rows"][from_index.row()][from_index.column() + 2] = new_value
            self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

        self.update_source()

    @pyqtSlot(int)
    def current_tab_changed(self, tab_index):
        table = self.tab_groups.currentWidget()
        if table:
            group_name = str(self.tab_groups.tabText(self.tab_groups.currentIndex()))
            table.model().model_data = self.current_data[group_name]
            table.model().layoutChanged.emit()

            for button in self.manipulation_buttons:
                button.setDisabled(True)

            table.selectionModel().clearSelection()

    @pyqtSlot(QItemSelection, QItemSelection)
    def current_selection_changed(self, selected, deselected):
        if self.rows_selection_mode:
            for button in self.manipulation_buttons + [self.button_add]:
                button.setDisabled(True)
        else:
            self.button_add.setDisabled(False)
            for button in self.manipulation_buttons:
                button.setDisabled(True if len(selected) == 0 else False)

            if len(selected) > 0:
                if selected[0].topLeft().column() == 0:
                    self.button_set_value.setDisabled(True)

    @pyqtSlot(QModelIndex)
    def on_double_click(self, index):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]

        if self.checkbox_allow_double_click.isChecked() and selected_index.column() > 0:
            self.set_attribute_value()

    @pyqtSlot()
    def move_rows_up(self):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]
        if selected_index.row() == 0:
            return
        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            row = table.model().model_data["rows"].pop(selected_index.row())
            table.model().model_data["rows"].insert(selected_index.row() - 1, row)
            table.model().layoutChanged.emit()
            table.setCurrentIndex(table.model().createIndex(selected_index.row() - 1, selected_index.column()))
            self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

        self.update_source()

    @pyqtSlot()
    def move_rows_down(self):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]
        if selected_index.row() == table.model().rowCount() - 1:
            return
        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            row = table.model().model_data["rows"].pop(selected_index.row())
            table.model().model_data["rows"].insert(selected_index.row() + 1, row)
            table.model().layoutChanged.emit()
            table.setCurrentIndex(table.model().createIndex(selected_index.row() + 1, selected_index.column()))
            self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

        self.update_source()

    @pyqtSlot()
    def move_rows_top(self):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]
        if selected_index.row() == 0:
            return
        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            row = table.model().model_data["rows"].pop(selected_index.row())
            table.model().model_data["rows"].insert(0, row)
            table.model().layoutChanged.emit()
            table.setCurrentIndex(table.model().createIndex(0, selected_index.column()))
            self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

        self.update_source()

    @pyqtSlot()
    def move_rows_bottom(self):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]
        if selected_index.row() == table.model().rowCount():
            return
        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            row = table.model().model_data["rows"].pop(selected_index.row())
            table.model().model_data["rows"].insert(table.model().rowCount(), row)
            table.model().layoutChanged.emit()
            table.setCurrentIndex(table.model().createIndex(table.model().rowCount() - 1, selected_index.column()))
            self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

        self.update_source()

    @pyqtSlot()
    def remove_rows(self):
        answer = show_question_dialog("Do You really want to remove selected row ?", "Remove row", self)
        if answer:
            table = self.tab_groups.currentWidget()
            selected_index = table.selectedIndexes()[0]
            for index in range(self.tab_groups.count()):
                table = self.tab_groups.widget(index)
                table.model().model_data["rows"].pop(selected_index.row())
                table.model().layoutChanged.emit()
                self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

            self.update_source()

    @pyqtSlot()
    def add_row(self):
        user_comment = show_prompt_dialog("Provide comment for new input:", "User comment", self)
        if user_comment:
            for index in range(self.tab_groups.count()):
                table = self.tab_groups.widget(index)
                saved_attributes = table.model().model_data["columns"]
                row = [self.default_row_color, time.strftime("%d-%m-%Y %H:%M:%S"), str(user_comment)]
                for device_id, attribute in saved_attributes[1:]:
                    device = self.session.get_device(device_id)
                    try:
                        if device.in_statuses(READY_DEVICE_STATUSES) and device.get_attribute(attribute) is not None:
                            value = device.get_attribute(attribute)
                            unit = device.get_attribute(attribute[:-1] + [UNIT])
                            user_unit = AttributeDeviceDisplayWidget.user_attribute_units.get(
                                (device_id, tuple(attribute[:-1])), None)
                            if user_unit is not None:
                                row.append("{:~}".format(units.Quantity(value, unit).to(user_unit)))
                            else:
                                row.append("{} {}".format(value, unit))
                        else:
                            row.append(u"None")
                    except DeviceUnknownError:
                        row.append(u"None")
                table.model().model_data["rows"].append(row)
                table.model().layoutChanged.emit()
                self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

            self.update_source()

    @pyqtSlot()
    def save(self):
        extension_filter = "SaveAttributes [*.att] (*.att)"
        file_path, _ = QFileDialog.getSaveFileName(self, 'Set save file', "./%s.att" % "attributeValues",
                                                   filter=extension_filter, initialFilter=extension_filter)
        if file_path != "":
            with open(file_path, "w") as fp:
                yaml.dump(self.current_data, fp)

    @pyqtSlot()
    def load(self):
        extension_filter = "SaveAttributes [*.att] (*.att)"
        file_path, _ = QFileDialog.getOpenFileName(self, 'Choose file to load', ".", filter=extension_filter,
                                                   initialFilter=extension_filter)
        if file_path != "":
            with open(file_path, "r") as fp:
                self.file_path = file_path

                if self.device is not None:
                    self.device.detach_observer(self)
                    self.device.detach_attribute_callback(ATTR_CONTENT, self.content_update)
                    self.device = None
                    self.checkbox_synced_with_server.setChecked(False)

                self.preset_groups = yaml.load(fp, Loader=yaml.Loader)
                self.current_data = self.preset_groups["Preset groups"][self.current_preset_group]
                self.load_data(self.current_data)

    @pyqtSlot()
    def reset(self):
        answer = show_question_dialog("Do You really want to remove all rows ?", "Reset all groups", self)
        if answer:
            table = self.tab_groups.currentWidget()
            table.model().model_data["rows"] = []
            table.model().layoutChanged.emit()

            for button in self.manipulation_buttons:
                button.setDisabled(True)

            self.update_source()

    @pyqtSlot()
    def reset_all(self):
        answer = show_question_dialog("Do You really want to remove all rows ?", "Reset group", self)
        if answer:
            for index in range(self.tab_groups.count()):
                table = self.tab_groups.widget(index)
                table.model().model_data["rows"] = []
                table.model().layoutChanged.emit()

            for button in self.manipulation_buttons:
                button.setDisabled(True)

            self.update_source()

    @pyqtSlot()
    def select_color(self):
        color = QColorDialog().getColor()
        if color is not None and color.name() != "#000000":
            table = self.tab_groups.currentWidget()
            selected_row = table.selectedIndexes()[0].row()

            for index in range(self.tab_groups.count()):
                table = self.tab_groups.widget(index)
                table.model().model_data["rows"][selected_row][0] = str(color.name())
                self.current_data[self.tab_groups.tabText(index)] = table.model().model_data

            self.update_source()

    @pyqtSlot()
    def set_attribute_value(self):
        table = self.tab_groups.currentWidget()
        selected_index = table.selectedIndexes()[0]

        attribute_value = table.model().model_data["rows"][selected_index.row()][selected_index.column() + 2]
        device_id, attribute = table.model().model_data["columns"][selected_index.column()]

        if attribute_value == "None":
            error_message = u"Cannot set attribute {} to value {}".format(attribute, attribute_value)
            show_error_message(error_message, self)
            self.logger.info(error_message)
            return
        else:
            self.logger.info(u"Set attribute {} to value {}".format(attribute, attribute_value))

        try:
            device = self.session.get_device(device_id)
            value_in_device_units = device_units(device, attribute[:-1], attribute_value)
            device.set_attribute(attribute, value_in_device_units.m, callback=self.sigErrorCheck.emit)
        except (DeviceError, DimensionalityError) as e:
            self.logger.exception(u"Set attribute error")
            show_error_message(e, self)

    @pyqtSlot()
    def add_preset_group(self):
        group_name = show_prompt_dialog("Set name of a new group", "New save group")
        if group_name and group_name != "":
            new_group = {}
            for key, value in self.preset_groups["Preset groups"][self.current_preset_group].items():
                new_group[key] = {
                    "columns": value["columns"],
                    "rows": []
                }
            self.preset_groups["Preset groups"][group_name] = new_group
            self.current_preset_group = group_name
            self.update_source()

    @pyqtSlot()
    def remove_preset_group(self):
        if show_question_dialog("Do You really want to remove current group?"):
            self.preset_groups["Preset groups"].pop(self.current_preset_group, None)
            self.combo_preset.removeItem(self.combo_preset.currentIndex())
            self.update_source()

    @pyqtSlot()
    def add_preset_group_from_selected(self):
        self.rows_selection_mode = True
        for button in self.manipulation_buttons + [self.button_add]:
            button.setDisabled(True)
        for button in self.preset_group_buttons:
            button.hide()
        for button in self.preset_rows_selection_buttons:
            button.show()

        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            table.setSelectionBehavior(table.SelectRows)
            table.setSelectionMode(table.MultiSelection)

    def update_preset_groups(self, block_signals):
        if block_signals:
            self.combo_preset.blockSignals(True)
        preset_groups = list(self.preset_groups["Preset groups"].keys())
        self.combo_preset.clear()
        self.combo_preset.insertItems(0, preset_groups)
        self.combo_preset.setCurrentIndex(preset_groups.index(self.current_preset_group))
        if block_signals:
            self.combo_preset.blockSignals(False)

    @pyqtSlot("QString")
    def preset_group_changed(self, preset_goup):
        self.current_preset_group = preset_goup
        if self.current_preset_group == "Default":
            self.button_remove_preset_group.setDisabled(True)
        else:
            self.button_remove_preset_group.setDisabled(False)
        self.load_data(self.preset_groups)

    @pyqtSlot()
    def confirm_rows_selection(self):
        group_name = show_prompt_dialog("Set name of a new group", "New save group")
        if group_name and group_name != "":
            table = self.tab_groups.currentWidget()
            new_group = {}
            for key, value in self.preset_groups["Preset groups"][self.current_preset_group].items():
                rows = []
                for index in table.selectionModel().selectedRows():
                    rows.append(value["rows"][index.row()])
                new_group[key] = {
                    "columns": value["columns"],
                    "rows": rows
                }
            self.preset_groups["Preset groups"][group_name] = new_group
            self.current_preset_group = group_name
            self.update_source()

        self.cancel_rows_selection()

    @pyqtSlot()
    def cancel_rows_selection(self):
        self.rows_selection_mode = False
        for button in self.preset_group_buttons:
            button.show()
        for button in self.preset_rows_selection_buttons:
            button.hide()

        for index in range(self.tab_groups.count()):
            table = self.tab_groups.widget(index)
            table.setSelectionBehavior(table.SelectItems)
            table.setSelectionMode(table.SingleSelection)
            table.clearSelection()
