import logging
import os

import oyaml as yaml
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QSpacerItem, QFileDialog, QListWidgetItem, QSizePolicy
from natsort import natsort
from pyqtgraph import GraphicsLayoutWidget
from yaml import Loader

import kamzik3
from kamzik3.constants import *
from kamzik3.gui.attributePlot import AttributePlot
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.macroStepWidget import MacroStepWidget
from kamzik3.gui.scanAttributeWidget import ScanAttributeWidget
from kamzik3.gui.templates.scanToolTemplate import Ui_Form
from kamzik3.macro.macro import Macro
from kamzik3.macro.scan import Scan
from kamzik3.snippets.snippetsGenerators import axis_name_generator
from kamzik3.snippets.snippetsWidgets import clear_layout, show_prompt_dialog, show_info_message, show_error_message, \
    show_question_dialog

CUSTOM_TEMPLATE = u"Custom"


class ScanToolWidget(Ui_Form, QWidget):
    scan_view = None
    vertical_spacer = None
    templates_directory_name = "scan_templates"
    templates_directory_path = None
    sig_update_progress = pyqtSignal("float")
    sig_update_macro_status = pyqtSignal("QString")
    current_macro = None
    return_back_macro = None

    def __init__(self, config=None, parent=None):
        self.config = config
        if self.config is None:
            self.config = {}
        self.iterative_widgets = []
        self.action_widgets = []
        self.plot_widgets = []
        self.loaded_templates = {}
        self.logger = logging.getLogger("Gui.ScanToolWidget")
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.plot_area = GraphicsLayoutWidget()
        self.plot_widget.layout().addWidget(self.plot_area)
        self.set_scan_templates_directory()
        self.read_scan_templates_directory()
        self._init_templates_list()
        self.button_pause_scan.hide()
        self.button_resume_scan.hide()
        self.button_import_template.hide()
        self.button_stop_scan.setDisabled(True)
        self.sig_update_progress.connect(self.set_scan_progress)
        self.sig_update_macro_status.connect(self.current_macro_status_changed)
        self.init_measurement_groups_list()

    def setupUi(self, Form):
        super().setupUi(Form)
        self.vertical_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)

    def set_scan_templates_directory(self):
        self.templates_directory_path = os.path.join(kamzik3.session.get_value(ATTR_RESOURCE_DIRECTORY),
                                                     self.templates_directory_name)
        if not os.path.exists(self.templates_directory_path):
            self.logger.info(u"Scan templates directory {} does not exists, trying to create it.".format(
                self.templates_directory_path))
            os.makedirs(self.templates_directory_path)

    def read_scan_templates_directory(self):
        self.loaded_templates = {}
        dir_path = self.templates_directory_path
        files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        for file_item in natsort.humansorted(files):
            with open(file_item, "r") as fp:
                template = yaml.load(fp, Loader=Loader)
                self.loaded_templates[template.get("title")] = (template, file_item)

    def _init_templates_list(self):
        self.combobox_template.clear()
        self.combobox_template.blockSignals(True)

        self.combobox_template.addItems(self.loaded_templates.keys())
        self.combobox_template.addItem(CUSTOM_TEMPLATE)

        self.combobox_template.blockSignals(False)
        self.template_selected(self.combobox_template.currentText())

    def template_selected(self, template_id):
        if template_id == CUSTOM_TEMPLATE:
            self.reset_template_input()
            self.init_measurement_groups_list()
            self.stackedWidget.setCurrentWidget(self.page_template_designer)
        else:
            self.reset_scan_input()
            self.stackedWidget.setCurrentWidget(self.page_scan_settings)
            self.generate_scan_layout(self.loaded_templates.get(template_id))

    @pyqtSlot("float")
    def set_scan_progress(self, progress):
        self.progress_bar_scan.setFormat("{0:.2f}%".format(progress))
        self.progress_bar_scan.setValue(progress)
        self.label_scan_step.setText(
            "  {} / {}  ".format(int(self.current_macro[ATTR_POINT_INDEX][VALUE]),
                                 int(self.current_macro[ATTR_POINTS_COUNT][VALUE])))
        self.label_running_time.setText("  {}  ".format(self.current_macro[ATTR_RUNNING_TIME][VALUE]))
        self.label_remaining_time.setText("  {}  ".format(self.current_macro[ATTR_REMAINING_TIME][VALUE]))
        self.label_estimated_finish.setText("  {}  ".format(self.current_macro[ATTR_ESTIMATED_END][VALUE]))

        if self.current_macro[ATTR_POINT_INDEX][VALUE] > 0:
            plot_widget = self.plot_widgets[self.current_macro[ATTR_CHAIN_LINK][VALUE]]
            if plot_widget is not None:
                plot_widget.update(int(self.current_macro[ATTR_POINT_INDEX][VALUE]))

    @pyqtSlot("QString")
    def current_macro_status_changed(self, status):
        if status == STATUS_BUSY:
            self.button_stop_scan.setDisabled(False)
            self.button_start_scan.setDisabled(True)
        elif status in (STATUS_IDLE, STATUS_ERROR):
            self.button_stop_scan.setDisabled(True)
            self.button_start_scan.setDisabled(False)

            if status == STATUS_ERROR:
                if self.current_macro is not None:
                    self.current_macro.stop()

                show_error_message("Scan error: {}".format(self.current_macro.error_message), self)
                if show_question_dialog(u"Scan leads to ERROR, do You want to return scan devices to initial values?"):
                    self.return_back_macro.start()

            elif status == STATUS_IDLE and self.current_macro.get_state() == DONE:
                self.return_back_macro.start()

        self.label_status.setText(status)
        self.label_status.setStyleSheet(
            "QLabel {{background:{}}}".format(DeviceWidget.status_colors.get(status, "blue")))

    def progress_update(self, key, value):
        if key == VALUE:
            self.sig_update_progress.emit(value)

    def status_update(self, key, value):
        if key == VALUE:
            self.sig_update_macro_status.emit(value)

    def reset_gui_from_previous_scan(self):

        if self.current_macro is not None:
            self.current_macro.detach_attribute_callback(ATTR_PROGRESS, self.progress_update)
            self.current_macro.detach_attribute_callback(ATTR_STATUS, self.status_update)
            for widget in self.plot_widgets:
                if widget is not None:
                    widget.close()
            self.current_macro.remove()
            self.current_macro = None
        if self.return_back_macro is not None:
            self.return_back_macro.remove()
            self.return_back_macro = None

        self.plot_widgets = []
        self.plot_area.clear()
        self.progress_bar_scan.setFormat("{0:.2f}%".format(0))
        self.progress_bar_scan.setValue(0)
        self.label_scan_step.setText("  0 / 0  ")
        self.label_running_time.setText("00:00:00")
        self.label_remaining_time.setText("00:00:00")
        self.label_estimated_finish.setText("00:00:00")
        self.input_output.setText("")

    def start_scan(self):
        self.reset_gui_from_previous_scan()
        self.current_macro = self.save()

        output_file, scan_index = self.current_macro.setup_output_file("scan-logs",
                                                                       kamzik3.session.get_value(ATTR_SCAN_PREFIX))
        current_template, _ = self.loaded_templates.get(self.combobox_template.currentText())
        header_lines = [
            u"Log version: {}".format("0.2"),
            u"Session ID: {}".format(kamzik3.session.device_id),
            u"Scan template: {}".format(self.combobox_template.currentText()),
            u"Scan prefix: {}".format(kamzik3.session.get_value(ATTR_SCAN_PREFIX)),
            u"Scan index: {}".format(scan_index),
            u"Scan comment: {}".format("None" if self.input_comment.text() == "" else self.input_comment.text()),
            u"Output file: {}".format(output_file),
            u"Points count: {}".format(self.current_macro.get_total_points_count()),
            u"Repeat count: {}".format(int(self.input_repeat_scan.value())),
            u"Measurement groups: {}".format(current_template.get("measurement_groups", None)),
            u"-" * 32,
        ]
        header_lines += self.current_macro.get_output_header()
        self.current_macro.macro_logger.preset_header = u"\n".join(u"# {0}".format(s) for s in header_lines) + u"\n"

        self.current_macro.attach_attribute_callback(ATTR_PROGRESS, self.progress_update)
        self.current_macro.attach_attribute_callback(ATTR_STATUS, self.status_update)

        # Create macro which returns all scan attributes to previous value
        self.return_back_macro = Macro("Return_back_macro")
        for chain_item in reversed(self.current_macro.chain):
            return_back_macro = chain_item.get_reset_step()
            if return_back_macro is not None:
                self.return_back_macro.add(return_back_macro)

        # Prepare macro for running
        for index, chain_item in enumerate(self.current_macro.chain):
            if isinstance(chain_item, Scan):
                device = kamzik3.session.get_device(chain_item.step_attributes["device_id"])
                plot_attribute = chain_item.step_attributes.get("output", chain_item.step_attributes["attribute"])
                attribute = device.get_attribute(plot_attribute)
                left_label = "{} - {}".format(chain_item.step_attributes["device_id"],
                                              plot_attribute)
                plot = self.plot_area.addPlot(index, 0)
                attribute_plot = AttributePlot(attribute, buffer_size=chain_item.points_count, left_label=left_label,
                                               plot=plot)
                self.plot_widgets.append(attribute_plot)
                for measurement_group in current_template.get("measurement_groups", []):
                    for device, attribute in kamzik3.session.measurement_groups[measurement_group]:
                        self.current_macro.add_output_attribute(device, attribute)

                self.current_macro.add_output_attribute(chain_item.step_attributes["device_id"], plot_attribute)
            else:
                self.plot_widgets.append(None)

        self.input_output.setText(output_file)
        self.current_macro.start()

    def save(self):
        current_template, template_filepath = self.loaded_templates.get(self.combobox_template.currentText())
        scan_layout = self.widget_scan.layout()

        # Check scan directory and update scan count
        scans_count = kamzik3.session.get_scan_count()
        # Create macro for current scan
        macro = Macro("Scan_{}".format(scans_count), repeat_count=self.input_repeat_scan.value())
        macro.set_value(ATTR_DESCRIPTION, self.input_comment.text())
        try:
            # Got thru current template and create all steps
            for index, item in enumerate(current_template["items"]):
                scan_item_widget = scan_layout.itemAt(index).widget()
                step = scan_item_widget.save()
                macro.add(step)
        except (ValueError, KeyError) as e:
            show_error_message(e, self)
            macro.remove()
            return None

        return macro

    def reset_scan_input(self):
        clear_layout(self.scroll_area_scan, self.widget_scan.layout())
        self.iterative_widgets = []
        self.action_widgets = []
        self.vertical_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def reset_template_input(self):
        clear_layout(self.scroll_area_custom_template, self.widget_custom_template.layout())
        self.iterative_widgets = []
        self.action_widgets = []
        self.vertical_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def generate_scan_layout(self, template):
        if template is None:
            return
        meta, file_path = template
        axis_names = axis_name_generator(meta["iterations"])

        for item in meta.get("items", []):
            if item["type"] == "iterative":
                iterative_widget = ScanAttributeWidget("{} {}".format(next(axis_names), item["attribute"]), config=item)
                self.iterative_widgets.append(iterative_widget)
                self.widget_scan.layout().addWidget(iterative_widget)
            elif item["type"] == "action":
                step_title = None
                if item["step"] == "Set attribute":
                    step_title = "{} {}".format(item["step"], item["attribute"])
                elif item["step"] == "Execute method":
                    step_title = "{} {}".format(item["step"], item["method"])
                action_widget = MacroStepWidget(step_title, config=item)
                self.action_widgets.append(action_widget)
                self.widget_scan.layout().addWidget(action_widget)

        self.widget_scan.layout().addItem(self.vertical_spacer)

    def pause_current_scan(self):
        # TODO: Implement scan pause
        pass

    def resume_current_scan(self):
        # TODO: Implement resume of current scan
        pass

    def stop_current_scan(self):
        """
        Stop current running scan.
        This method is called once user push stop button.
        :return:
        """
        self.current_macro.stop()

        if show_question_dialog(u"Scan was stopped, do You want to return scan devices to initial values?"):
            self.return_back_macro.start()

    def remove_template(self):
        """
        Remove currently selected template.
        :return:
        """
        current_template = self.combobox_template.currentText()
        if show_question_dialog("Do You want to remove template {} ?".format(current_template), u"Remove template",
                                self):
            try:
                template, file_item = self.loaded_templates.get(current_template, None)
                os.remove(file_item)
            except (FileNotFoundError, OSError) as e:
                error_message = "Template could not be removed: {}".format(e)
                self.logger.error(error_message)
                show_error_message(error_message, self)

            self.logger.info(u"Removing template {} at {}.".format(current_template, file_item))
            self.read_scan_templates_directory()
            self._init_templates_list()

    def export_template(self):
        """
        Export and save new created template.
        :return:
        """
        try:
            items = self.get_template_meta()
        except ValueError as e:
            self.logger.info(e)
            show_error_message(e, self)
            return

        template_title = show_prompt_dialog("Template title")
        if not template_title or template_title == "":
            return

        selected_measurement_groups = [item.text() for item in self.list_measurement_groups.selectedItems()]

        file_path = os.path.join(self.templates_directory_path, template_title.replace(" ", "_") + ".stpl")
        if file_path != "":
            with open(file_path, "w") as fp:
                data = {
                    "title": template_title,
                    "iterations": len(self.iterative_widgets),
                    "actions": len(self.action_widgets),
                    "items": items,
                    "measurement_groups": selected_measurement_groups
                }
                yaml.dump(data, fp)
                self.logger.info("New template {} saved.".format(file_path))
                show_info_message("New template {} saved.".format(file_path), self)

        self.read_scan_templates_directory()
        self._init_templates_list()

    def import_template(self):
        """
        Import template from other template file.
        :return:
        """
        #  TODO: Implement template importing feature
        extension_filter = "*.stpl"
        file_path, _ = QFileDialog.getOpenFileName(self, 'Import scan template', filter=extension_filter,
                                                   initialFilter=extension_filter)
        if file_path != "":
            print(file_path)

    def get_template_meta(self):
        """
        Go thru all widgets in template and export it's meta.
        :return: list of meta data describing template
        """
        meta = []
        layout = self.widget_custom_template.layout()
        for item in range(len(layout)):
            widget = layout.itemAt(item).widget()
            if widget is not None:
                meta.append(widget.get_template())
        return meta

    def add_action_step(self):
        """
        Add action step widget.
        Which is either set attribute or method.
        :return: None
        """
        self.widget_custom_template.layout().removeItem(self.vertical_spacer)
        step_widget = MacroStepWidget(config={CFG_TEMPLATE: True})
        self.action_widgets.append(step_widget)
        self.widget_custom_template.layout().addWidget(step_widget)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)
        self.update_template_view_step_titles()

    def add_iterative_step(self):
        """
        Add iterative step widget.
        This widget represents any scan over numerical value.
        :return: None
        """
        self.widget_custom_template.layout().removeItem(self.vertical_spacer)
        iterative_widget = ScanAttributeWidget(config={CFG_TEMPLATE: True})
        self.iterative_widgets.append(iterative_widget)
        self.widget_custom_template.layout().addWidget(iterative_widget)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)
        self.update_template_view_step_titles()

    def add_template(self):
        self.widget_custom_template.layout().removeItem(self.vertical_spacer)
        step_widget = MacroStepWidget(config={CFG_TEMPLATE: True})
        self.action_widgets.append(step_widget)
        self.widget_custom_template.layout().addWidget(step_widget)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)
        self.update_template_view_step_titles()

    def update_template_view_step_titles(self):
        """
        Since we are using different names for scan widgets like slow, fast scan...
        After adding
        :return:
        """
        axis_names = axis_name_generator(len(self.iterative_widgets))
        for widget in self.iterative_widgets:
            widget.set_title(next(axis_names))

    def init_measurement_groups_list(self):
        self.list_measurement_groups.clear()
        for title in kamzik3.session.measurement_groups.keys():
            self.list_measurement_groups.addItem(QListWidgetItem(title))
        self.list_measurement_groups.setCurrentRow(0)
