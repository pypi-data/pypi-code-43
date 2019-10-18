from qtpy.QtWidgets import *
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QProcess
from PyQt5 import QtCore as Core
from qtpy import QtGui
import numpy as np
import yaml
from qtpy import QtCore
import sys
from random import randint
from cicada.preprocessing.utils import get_subfiles, get_subdirs
from abc import ABC, abstractmethod
from cicada.gui.cicada_all_group import AllGroups
from cicada.gui.cicada_analysis_overview import AnalysisOverview, AnalysisState, ResultsButton
from qtpy.QtCore import QThread
import os
from time import time
from functools import partial



class ParameterWidgetModel(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_value(self):
        """
        Return the value of the widget
        Returns:

        """
        return None

    @abstractmethod
    def set_value(self, value):
        """
        Set the widget value to the value passed
        Returns:

        """
        pass

    @abstractmethod
    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        pass


class MyQFrame(QFrame):

    def __init__(self, analysis_arg=None, parent=None, with_description=True):
        """

        Args:
            analysis_arg:
            parent:
            with_description: if True, will add a description at the top of the widget
             based on a description arg if it exists
        """
        QFrame.__init__(self, parent=parent)

        self.analysis_arg = analysis_arg
        self.description = ''
        self.long_description = None
        self.v_box = QVBoxLayout()

        self.h_box = QHBoxLayout()
        if self.analysis_arg is not None:
            self.long_description = self.analysis_arg.get_long_description()

        self.q_label_empty = None
        # Trick to keep description in the middle even if help_button exists
        if with_description or (self.long_description is not None):
            self.q_label_empty = QLabel("  ")
            self.q_label_empty.setAlignment(Qt.AlignCenter)
            self.q_label_empty.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.q_label_empty.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.h_box.addWidget(self.q_label_empty)
            self.h_box.addStretch(1)

        if with_description:
            if self.analysis_arg is not None:
                self.description = self.analysis_arg.get_short_description()
            if self.description:

                self.q_label_description = QLabel(self.description)
                self.q_label_description.setAlignment(Qt.AlignCenter)
                self.q_label_description.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                self.q_label_description.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                self.h_box.addWidget(self.q_label_description)
            else:
                self.h_box.addStretch(1)
        if self.long_description:
            self.help_button = QPushButton()
            my_path = os.path.abspath(os.path.dirname(__file__))
            self.help_button.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/question-mark.svg')))

            self.help_button.setIconSize(Core.QSize(10, 10))
            self.help_button.setToolTip(self.long_description)
            self.help_button.clicked.connect(self.help_click_event)

            self.h_box.addStretch(1)
            self.h_box.addWidget(self.help_button)
        elif self.q_label_empty is not None:
            self.h_box.addStretch(1)
            self.h_box.addWidget(self.q_label_empty)

        if with_description or (self.long_description is not None):
            self.v_box.addLayout(self.h_box)

        self.v_box.addStretch(1)

        if with_description or (self.long_description is not None):
            self.v_box.addLayout(self.h_box)

        self.setLayout(self.v_box)

        if self.analysis_arg is not None:
            self.mandatory = self.analysis_arg.is_mandatory()
        else:
            self.mandatory = False
        self.setProperty("is_mandatory", str(self.mandatory))

    def change_mandatory_property(self, value):
        """
        Changing the property allowing to change the style sheet depending on the mandatory aspect of the argument
        Args:
            value:

        Returns:

        """
        self.setProperty("is_mandatory", value)
        self.style().unpolish(self)
        self.style().polish(self)

    def help_click_event(self):
        self.help_box = QMessageBox(self)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.help_box.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))
        self.help_box.setIcon(QMessageBox.Information)
        if self.description:
            self.help_box.setWindowTitle(self.description)
        self.help_box.setAttribute(Qt.WA_DeleteOnClose)
        self.help_box.setStandardButtons(QMessageBox.Ok)
        self.help_box.setText(self.long_description)
        self.help_box.setModal(False)
        self.help_box.show()

    def get_layout(self):
        return self.v_box

    def set_property_to_missing(self):
        """
        Allows the change the stylesheet and indicate the user that a
        Returns:

        """
        self.setProperty("something_is_missing", "True")


# to resolve: TypeError: metaclass conflict: the metaclass of a derived class
# must be a (non-strict) subclass of the metaclasses of all its bases
# might not be a good idea to do multiple-heritage with a Qclass
# solution from: https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
# http://www.phyast.pitt.edu/~micheles/python/metatype.html
class FinalMeta(type(ParameterWidgetModel), type(QWidget)):
    pass


# TODO: some of the widgets to add
#  - choose directory
#  - choose a color
#  -

class SameFamilyWidgetsContainer(MyQFrame):
    """
    A QFrame used to group widgets that belongs to a same group. Just useful for visual purposes
    """

    def __init__(self, widgets, parent=None):
        MyQFrame.__init__(self, analysis_arg=None, parent=parent, with_description=False)

        # to_stretch
        index_widget = 0
        while index_widget < len(widgets):
            gui_widget = widgets[index_widget]
            next_widget = None
            if index_widget < (len(widgets) - 1):
                next_widget = widgets[index_widget + 1]
            if next_widget is None:
                # we add to the VBoxLayout
                self.v_box.addWidget(gui_widget)
                # end of the loop anyway, so let's break
                break

            # otherwise, we have to decide if we put both in HBoxLayout
            if (not gui_widget.to_stretch()) and (not next_widget.to_stretch()):
                h_box = QHBoxLayout()
                h_box.addWidget(gui_widget)
                h_box.addWidget(next_widget)
                self.v_box.addLayout(h_box)
                index_widget += 2
            else:
                self.v_box.addWidget(gui_widget)
                index_widget += 1

        self.v_box.addStretch(1)

        self.setProperty("is_mandatory", "FamilyWidget")

        # for widget in widgets:
        #     self.v_box.addWidget(widget)

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return True

# QColorDialog
class ColorDialogWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Widget used to select a color
    """
    # ShowAlphaChannel
    # TODO: add option so a different color can be chosen for each session, adding for exemple a sessions arg
    def __init__(self, analysis_arg, show_alpha_channel, parent=None):
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.color = Qt.white
        default_value = self.analysis_arg.get_default_value()
        if default_value is not None and (isinstance(default_value, list) or isinstance(default_value, tuple)):
            color = QtGui.QColor()
            color.setRgbF(*default_value)
            self.color = color
        self.show_alpha_channel = show_alpha_channel

        h_box = QHBoxLayout()
        self.select_button = QPushButton("Select color", self)
        self.select_button.setToolTip("Select color")
        self.update_button_color()

        self.select_button.clicked.connect(self.open_dialog)
        h_box.addStretch(1)
        h_box.addWidget(self.select_button)
        h_box.addStretch(1)
        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

    def open_dialog(self):
        """
        Open the color dialog
        Returns:

        """
        initial = Qt.white
        if self.color is not None:
            initial = self.color
        options = QColorDialog.ColorDialogOption()
        if self.show_alpha_channel:
            options |= QColorDialog.ShowAlphaChannel
        color = QColorDialog.getColor(initial=initial, options=options)

        if color.isValid():
            self.color = color
            self.update_button_color()

    def update_button_color(self):
        """

        Returns:

        """
        if self.color is not None:
            rgb_values = [1 - color_code for color_code in self.color.getRgbF()]
            # the foreground color will be the invert of the selected color, which will be the background of the button
            fg_color = QtGui.QColor()
            fg_color.setRgbF(*rgb_values[:3])
            self.select_button.setStyleSheet(f"background-color:{self.color.name()}; color:{fg_color.name()};")

    def set_value(self, value):
        """

        Args:
            value: a list or tuple of 3 or 4 float between 0.0 to 1.0, RGB or RGBA values, the A representing the alpha

        Returns:

        """

        if value is not None:
            color = QtGui.QColor()
            color.setRgbF(*value)
            self.color = color
            self.update_button_color()

    def get_value(self):
        """

        Returns: a tuple of 4 floats representing RGBA with values from 0.0 to 1.0

        """
        return self.color.getRgbF()

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return False

class MyFileDialogQButton(QPushButton):
    """
    Special button for opening file dialog
    """

    def __init__(self, key_name, file_dialog, file_dialogs_dict, parent=None):
        QPushButton.__init__(self, key_name, parent)
        self.key_name = key_name
        self.file_dialog = file_dialog
        self.file_dialogs_dict = file_dialogs_dict

        self.clicked.connect(self.open_dialog)

    def open_dialog(self):
        """
                Open the QFileDialog
                Args:
                    key_name:

                Returns:

        """
        q_label_path = self.file_dialogs_dict[self.key_name]
        if self.file_dialog.exec_() == QDialog.Accepted:
            path = self.file_dialog.selectedFiles()[0]  # returns a list
            # file_dialog.setDirectory(path)
            q_label_path.setText(path)
            # if self.mandatory:
            #     self.change_mandatory_property(value="False")


class FileDialogWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Create a widget that will contain a button to open a FileDialog and a label to display the file or directory choosen
    A label will also explain what this parameter do
    """

    def __init__(self, analysis_arg, directory_only, extensions=None, parent=None):
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)
        # both are booleans
        # self.save_file_dialog = save_file_dialog
        self.directory_only = directory_only
        self.extensions = extensions

        description = self.analysis_arg.get_short_description()
        if description is None:
            if directory_only:
                description = "Choose directory"
            else:
                description = "Choose a file or a directory"
        self.q_label_description.setText(description)

        # getting the key_names, if not None, means we will put as many file selector as they are key
        # the key_name will be the button label
        key_names = getattr(self.analysis_arg, "key_names", None)
        self.default_button_text = "Select"
        if key_names is None:
            key_names = [self.default_button_text]
        if isinstance(key_names, str):
            key_names = [key_names]
        self.key_names = key_names

        # each key will be one of the key_names and each value will be a list with first element being the QFileDialog
        # and the second element the qlabel
        self.file_dialogs_dict = dict()

        self.file_dialog = QFileDialog(self, description)

        # setting options
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        self.file_dialog.setOptions(options)

        # ARE WE TALKING ABOUT FILES OR FOLDERS
        if directory_only:
            self.file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        else:
            self.file_dialog.setFileMode(QFileDialog.AnyFile)

        # OPENING OR SAVING
        # self.file_dialog.setAcceptMode(QFileDialog.AcceptOpen) if forOpen else \
        #     self.file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        # self.file_dialog.setSidebarUrls([QtCore.QUrl.fromLocalFile(place)])

        # SET THE STARTING DIRECTORY
        default_value = self.analysis_arg.get_default_value()
        if default_value is not None and isinstance(default_value, str):
            self.file_dialog.setDirectory(default_value)
        # else:
        #     self.file_dialog.setDirectory(str(ROOT_DIR))

        # SET FORMAT, IF SPECIFIED
        if (self.extensions is not None) and (not directory_only):
            if isinstance(self.extensions, str):
                self.extensions = [self.extensions]
            self.file_dialog.setDefaultSuffix(self.extensions[0])
            self.file_dialog.setNameFilters([f'{file_extension} (*.{file_extension})'
                                             for file_extension in self.extensions])

        if len(key_names) > 1:
            # then we create a button all for one that allows to select the same files for all
            one_for_all_layout = QHBoxLayout()
            self.one_for_all_button = QPushButton("One for all", self)
            self.one_for_all_button.clicked.connect(self.one_for_all)
            one_for_all_layout.addStretch(1)
            one_for_all_layout.addWidget(self.one_for_all_button)
            one_for_all_layout.addStretch(1)
            self.v_box.addLayout(one_for_all_layout)

        h_box = QHBoxLayout()
        v_box_buttons = QVBoxLayout()
        v_box_labels = QVBoxLayout()
        for key_name in key_names:
            select_button = MyFileDialogQButton(key_name=key_name, parent=self, file_dialog=self.file_dialog,
                                                file_dialogs_dict=self.file_dialogs_dict)
            # h_box.addStretch(1)
            v_box_buttons.addWidget(select_button)
            # h_box.addStretch(1)

            label_text = ""
            if default_value is not None and isinstance(default_value, str):
                label_text = default_value
            q_label_path = QLabel(label_text)
            q_label_path.setAlignment(Qt.AlignCenter)
            q_label_path.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label_path.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            scrollArea = QScrollArea()
            # ScrollBarAlwaysOff = 1
            # ScrollBarAlwaysOn = 2
            # ScrollBarAsNeeded = 0
            scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scrollArea.setWidgetResizable(True)
            scrollArea.setProperty("label_path", "True")
            scrollArea.setWidget(q_label_path)
            v_box_labels.addWidget(scrollArea)

            self.file_dialogs_dict[key_name] = q_label_path

        h_box.addLayout(v_box_buttons)
        h_box.addLayout(v_box_labels)
        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

        # def openFileNameDialog(self):
        #     options = QFileDialog.Options()
        #     setFileMode(QFileDialog.Directory)
        #     options |= QFileDialog.DontUseNativeDialog
        #     fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                               "All Files (*);;Python Files (*.py)", options=options)
        #     if fileName:
        #         print(fileName)


        #
        # def openFileNamesDialog(self):
        #     options = QFileDialog.Options()
        #     options |= QFileDialog.DontUseNativeDialog
        #     files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
        #                                             "All Files (*);;Python Files (*.py)", options=options)
        #     if files:
        #         print(files)
        #
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
        #                                           "All Files (*);;Text Files (*.txt)", options=options)
        # if fileName:
        #     print(fileName)


        # # directory only
        # fileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        # # just list mode is quite sufficient for choosing a diectory
        # fileDialog.setViewMode(QtWidgets.QFileDialog.List)
        # # only want to to show directories
        # fileDialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        # # native dialog, at least under Ubuntu GNOME is a bit naff for choosing a directory
        # # (shows files but greyed out), so going for Qt's own cross-plaform chooser
        # fileDialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        # # get rid of (or at least grey out) file-types selector
        # fileDialog.setOption(QtWidgets.QFileDialog.HideNameFilterDetails)
        # # DontResolveSymlinks seemingly recommended by http://doc.qt.io/qt-5/qfiledialog.html#getExistingDirectory
        # # but I found it didn't make any difference (symlinks resolved anyway)
        # # fileDialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks)

    def one_for_all(self):
        """
        Allows to select the same dir of files for all session
        Returns:

        """
        if self.file_dialog.exec_() == QDialog.Accepted:
            path = self.file_dialog.selectedFiles()[0]  # returns a list
            for q_label_path in self.file_dialogs_dict.values():
                q_label_path.setText(path)

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return True

    def get_value(self):
        """
        Return the argument

        Returns:
            result_dict (dict): Dictionary with the set value
        """
        if len(self.key_names) == 1 and (self.key_names[0] == self.default_button_text):
            q_label_path = self.file_dialogs_dict[self.key_names[0]]
            text = q_label_path.text()
            if text == "":
                return None
            return text

        result_dict = dict()
        for key_name, q_label_path in self.file_dialogs_dict.items():
            text = q_label_path.text()
            if text == "":
                result_dict[key_name] = None
            else:
                result_dict[key_name] = text

        return result_dict

    def set_value(self, value):
        """
        Set the value
        Args:
            value: either None, either a string or etiher a dictionary

        Returns:

        """
        if value is None:
            # if self.mandatory:
            #     self.change_mandatory_property(value="True")
            for q_label_path in self.file_dialogs_dict.values():
                q_label_path.setText('')
            return
        if isinstance(value, str):
            if len(self.file_dialogs_dict) != 1:
                # not the same number of elements, so we don't change anything
                return
            # make it a dict
            value = {list(self.file_dialogs_dict.keys())[0]: value}

        if len(value) != len(self.file_dialogs_dict):
            # not the same number of elements, so we don't change anything
            return

        for key_name, path_name in value.items():
            if key_name not in self.file_dialogs_dict:
                continue
            if path_name is None:
                q_label_path = self.file_dialogs_dict[key_name]
                q_label_path.setText('')
                continue
            # then we checks if it exists
            if os.path.exists(path_name):
                # if self.analysis_arg.is_mandatory():
                #     self.change_mandatory_property(value="True")
                q_label_path = self.file_dialogs_dict[key_name]
                q_label_path.setText(path_name)
                # self.file_dialog.setDirectory(value)


class ListCheckboxWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
       Allows multiple choices
    """

    def __init__(self, analysis_arg, choices_attr_name, parent=None):
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.list_widgets = dict()
        # QListWidget()

        # self.list_widget.setProperty("param", "True")

        # self.v_box.addStretch(1)

        choices = getattr(self.analysis_arg, choices_attr_name, None)
        default_value = self.analysis_arg.get_default_value()
        if isinstance(default_value, str):
            default_value = [default_value]
        if choices is not None:
            self.apply_to_all_sessions = False
            # if list, means the choices apply to all sessions
            if isinstance(choices, list):
                self.apply_to_all_sessions = True
                choices = {"toto": choices}
            # else it is a dict then it means each key of the dict represent the session_id
            # and the value a list of choices
            n_sessions = len(choices)
            session_index = 0
            for session_id, list_choices in choices.items():
                self.list_widgets[session_id] = QListWidget()
                # property is used to have a specificy stylesheet for this QList
                self.list_widgets[session_id].setProperty("param", "True")
                for choice in list_choices:
                    item = QListWidgetItem()
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    # need to be specified to display the checkbox
                    item.setCheckState(QtCore.Qt.Unchecked)
                    if (not self.apply_to_all_sessions) and isinstance(default_value, dict):
                        if default_value and (choice in default_value):
                            item.setCheckState(QtCore.Qt.Checked)
                        else:
                            item.setCheckState(QtCore.Qt.Unchecked)
                    elif self.apply_to_all_sessions:
                        if default_value and (choice in default_value):
                            item.setCheckState(QtCore.Qt.Checked)
                        else:
                            item.setCheckState(QtCore.Qt.Unchecked)

                    item.setText(str(choice))
                    self.list_widgets[session_id].addItem(item)
                self.list_widgets[session_id].setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

                h_box = QHBoxLayout()
                if not self.apply_to_all_sessions:
                    # if more than one session_id, we display the name of the session
                    q_label = QLabel(session_id)
                    # q_label.setAlignment(Qt.AlignCenter)
                    q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                    q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                    h_box.addWidget(q_label)

                # h_box.addStretch(1)
                h_box.addWidget(self.list_widgets[session_id])
                self.v_box.addLayout(h_box)

                # Adding a line to separate QList
                if session_index < (n_sessions - 1):
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    self.v_box.addWidget(line)

                session_index += 1

        self.v_box.addStretch(1)
        # self.list_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        if not self.apply_to_all_sessions:
            # means we're adding the name of sessions as QLabel
            return True
        return False

    def set_value(self, value):
        """
        Set the value.
        Args:
            value: value is either a string or integer or float, or a list. If a list, then item whose value matches
            one of the elements in the list will be checkeds
        Returns: None

        """
        if value is None:
            return

        for session_id, list_widget in self.list_widgets.items():

            if isinstance(value, dict):
                if session_id in value:
                    values = value[session_id]
                else:
                    continue
            elif not isinstance(value, list):
                values = [value]
            else:
                values = value

            # first we uncheck them all
            for i in np.arange(list_widget.count()):
                item = list_widget.item(i)
                item.setCheckState(QtCore.Qt.Unchecked)

            # then we find the items that match the values and checked them
            for item_content in values:
                items = list_widget.findItems(item_content, Qt.MatchExactly)
                for item in items:
                    item.setCheckState(QtCore.Qt.Checked)

    def get_value(self):
        """

        Returns:

        """
        result_dict = dict()
        for session_id, list_widget in self.list_widgets.items():
            checked_items = []
            for index in range(list_widget.count()):
                if list_widget.item(index).checkState() == 2:
                    checked_items.append(list_widget.item(index).text())

            if self.analysis_arg.get_default_value() and (len(checked_items) == 0):
                # then we put the default value as results
                default_value = self.analysis_arg.get_default_value()
                if isinstance(default_value, dict):
                    checked_items.append(default_value[session_id])
                elif default_value is not None:
                    checked_items.append(default_value)

            if self.apply_to_all_sessions:
                # then it should be only one element in the dict,that applies to all session
                return checked_items
            result_dict[session_id] = checked_items

        return result_dict


class LineEditWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        MyQFrame.__init__(self, analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.line_edit = QLineEdit()

        if self.analysis_arg.get_default_value():
            self.line_edit.setText(self.analysis_arg.get_default_value())

        h_box = QHBoxLayout()
        h_box.addWidget(self.line_edit)
        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

    def set_value(self, value):
        if value is not None:
            self.line_edit.setText(value)

    def get_value(self):
        return self.line_edit.text()

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return True


class MyQComboBox(QComboBox):
    """
    Special instance of ComboBox allowing to handle change so that it is connected to other combo_boxes
    """
    def __init__(self):
        """
        init
        """
        QComboBox.__init__(self)
        self.next_combo_box = None
        # each key represent a content to put in the list and the value could be either None, either
        #             another dict whose keys will be the content of the next ComboBox etc...
        self.choices_dict = None
        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self, index):
        """
        Called if the selection is changed either by the user or by the code
        Args:
            index:

        Returns:

        """
        # TODO: find data with multiple choices to test this code
        if self.next_combo_box is None:
            return

        # it should not be empty
        if self.count() == 0:
            return

        current_text = self.currentText()
        if current_text not in self.choices_dict:
            return

        content_next_combo_box = self.choices_dict[current_text]
        # removing previous items
        self.next_combo_box.clear()
        # adding new ones
        for choice_id in content_next_combo_box.keys():
            # need to put 2 arguments, in order to be able to find it using findData
            self.next_combo_box.addItem(str(choice_id), str(choice_id))
        # to make combo_box following the next ones will be updated according to the content at the index 0
        self.next_combo_box.setCurrentIndex(0)


class ComboBoxWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):

    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
            parent:
        """
        MyQFrame.__init__(self, analysis_arg=analysis_arg, parent=parent)

        ParameterWidgetModel.__init__(self)

        self.combo_boxes = dict()

        default_value = self.analysis_arg.get_default_value()
        # legends: List of String, will be displayed as tooltip over the ComboBox
        if hasattr(self.analysis_arg, "legends"):
            legends = self.analysis_arg.legends
            # if isinstance(legends, str):
            #     legends = [legends]
        else:
            legends = None

        if self.analysis_arg.choices is not None:

            # two cases, either choices is a list
            # then we're displaying option valid for all sessions
            if isinstance(self.analysis_arg.choices, list):
                # we put "toto", but it doesn't matter, if there is only one element
                # then the key won't be displayed
                self.combo_boxes["toto"] = [MyQComboBox()]
                if legends is not None:
                    self.combo_boxes["toto"][0].setToolTip(legends)
                index = 0
                for choice in self.analysis_arg.choices:
                    # need to put 2 arguments, in order to be able to find it using findData
                    self.combo_boxes["toto"][0].addItem(str(choice), str(choice))
                    if default_value:
                        if choice == default_value:
                            self.combo_boxes["toto"][0].setCurrentIndex(index)
                    index += 1
            elif isinstance(self.analysis_arg.choices, dict):
                # then each key represent a session_id and the value could be:
                # either a list of choices
                # either another dict, meaning will have more than one QCombotWidget
                index = 0
                for session_id, choices in self.analysis_arg.choices.items():
                    if isinstance(choices, str):
                        choices = [choices]

                    if isinstance(choices, list) or isinstance(choices, tuple):
                        self.combo_boxes[session_id] = [MyQComboBox()]
                        if legends is not None:
                            self.combo_boxes[session_id][0].setToolTip(legends)
                        for choice in choices:
                            # need to put 2 arguments, in order to be able to find it using findData
                            self.combo_boxes[session_id][0].addItem(str(choice), str(choice))
                            # TODO: implement default_value, see how make it practical
                            # if default_value:
                            #     if choice == default_value:
                            #         self.combo_box.setCurrentIndex(index)
                            index += 1
                    elif isinstance(choices, dict):
                        self.combo_boxes[session_id] = []
                        self.add_multiple_combo_boxes(session_id=session_id, choices_dict=choices, legends=legends,
                                                      index=0)
        h_box = QHBoxLayout()
        # first we determine how many combo_box max
        n_boxes_max = 0
        v_box_session_id = QVBoxLayout()
        for session_id, combo_box_list in self.combo_boxes.items():
            n_boxes_max = max(n_boxes_max, len(combo_box_list))
            if len(self.combo_boxes) > 1:
                # if more than one session_id, we display the name of the session
                q_label = QLabel(session_id)
                # q_label.setAlignment(Qt.AlignCenter)
                q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                v_box_session_id.addWidget(q_label)
        if len(self.combo_boxes) > 1:
            h_box.addLayout(v_box_session_id)

        v_box_list = []
        for i in np.arange(n_boxes_max):
            v_box_list.append(QVBoxLayout())

        for session_id, combo_box_list in self.combo_boxes.items():
            for index_combo, combo_box in enumerate(combo_box_list):
                v_box_list[index_combo].addWidget(combo_box)

        for v_box in v_box_list:
            h_box.addLayout(v_box)

        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return True

    def add_multiple_combo_boxes(self, session_id, choices_dict, legends, index):
        """
        Allows to add multiple combo boxes, each changing the content of the next one for on given session_id
        Args:
            session_id:
            choices_dict: each key represent a content to put in the list and the value could be either None, either
            another dict which keys will be the content of the next ComboBox etc... or instead of a dict as value it
            could be a list that will define the content.
            legends:
            index:

        Returns:

        """
        combo_box = MyQComboBox()
        self.combo_boxes[session_id].append(combo_box)
        if legends is not None:
            if isinstance(legends, str):
                combo_box.setToolTip(legends)
            else:
                combo_box.setToolTip(legends[index])

        index_loop_for = 0
        # combo_box following this one
        next_combo_box = None
        for choice_id, choice_content in choices_dict.items():
            # need to put 2 arguments, in order to be able to find it using findData
            combo_box.addItem(str(choice_id), str(choice_id))
            if choice_content is None:
                continue
            elif isinstance(choice_content, dict) and (index_loop_for == 0):
                next_combo_box = self.add_multiple_combo_boxes(session_id=session_id, choices_dict=choice_content,
                                                               legends=legends,
                                              index=index+1)
            elif isinstance(choice_content, list):
                next_combo_box = MyQComboBox()
                self.combo_boxes[session_id].append(next_combo_box)
                if legends is not None:
                    next_combo_box.setToolTip(legends[index+1])
                for next_choice_id in choice_content:
                    next_combo_box.addItem(str(next_choice_id), str(next_choice_id))

            index_loop_for += 1
        combo_box.choices_dict = choices_dict
        combo_box.next_combo_box = next_combo_box
        return combo_box

    def set_value(self, value):
        """
        Set a new value.
        Either value is None and nothing will happen
        If value is a list instance,
        Args:
            value:

        Returns:

        """
        if value is None:
            return

        if isinstance(value, dict):
            # means each key represent the session_id and the value the default value or values
            for session_id, value_to_set in value.items():
                # first checking is the session exists
                if session_id not in self.combo_boxes:
                    continue
                combo_box_list = self.combo_boxes[session_id]
                if not isinstance(value_to_set, list):
                    value_to_set = [value_to_set]
                if len(combo_box_list) != len(value_to_set):
                    # not compatible
                    continue
                for index_combo, combo_box in enumerate(combo_box_list):
                    index = combo_box.findData(value_to_set[index_combo])
                    # -1 for not found
                    if index != -1:
                        combo_box.setCurrentIndex(index)
        else:
            # otherwise we look for the value in each of the combo_box
            for combo_box_list in self.combo_boxes.values():
                if not isinstance(value, list):
                    value = [value]
                if len(combo_box_list) != len(value):
                    # not compatible
                    continue
                for index_combo, combo_box in enumerate(combo_box_list):
                    index = combo_box.findData(value[index_combo])
                    # -1 for not found
                    if index != -1:
                        combo_box.setCurrentIndex(index)

    def get_value(self):
        """

        Returns:

        """
        if len(self.combo_boxes) == 1:
            for combo_box_list in self.combo_boxes.values():
                results = []
                for combo_box in combo_box_list:
                    results.append(combo_box.currentText())
                if len(results) == 1:
                    results = results[0]
                return results
        result_dict = dict()
        for session_id, combo_box_list in self.combo_boxes.items():
            results = []
            for combo_box in combo_box_list:
                results.append(combo_box.currentText())
            if len(results) == 1:
                results = results[0]
            result_dict[session_id] = results
        return result_dict


class CheckBoxWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Used to set a boolean value
    """
    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        MyQFrame.__init__(self, analysis_arg=analysis_arg, parent=parent, with_description=False)
        ParameterWidgetModel.__init__(self)

        self.check_box = QCheckBox()

        # False by default otherwise
        if self.analysis_arg.get_default_value() is not None:
            # using setCheckState make it a triState
            self.check_box.setChecked(self.analysis_arg.get_default_value())

        description = self.analysis_arg.get_short_description()
        if description:
            self.check_box.setText(description)

        h_box = QHBoxLayout()
        h_box.addWidget(self.check_box)
        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def set_value(self, value):
        if value is None:
            value = False
        self.check_box.setChecked(value)

    def get_value(self):
        return self.check_box.isChecked()

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return False


class SliderWidget(MyQFrame, ParameterWidgetModel, metaclass=FinalMeta):
    """
    Used to set a numerical value
    """
    def __init__(self, analysis_arg, parent=None):
        """

        Args:
            analysis_arg: instance of AnalysisArgument
        """
        MyQFrame.__init__(self, analysis_arg=analysis_arg, parent=parent)
        ParameterWidgetModel.__init__(self)

        self.analysis_arg = analysis_arg
        self.slider = QSlider(Qt.Horizontal)

        self.spin_box = QSpinBox()

        if (self.analysis_arg.max_value is not None) and (self.analysis_arg.min_value is not None):
            self.slider.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)
            self.spin_box.setRange(self.analysis_arg.min_value, self.analysis_arg.max_value)

        if self.analysis_arg.get_default_value():
            self.slider.setValue(self.analysis_arg.get_default_value())
            self.spin_box.setValue(self.analysis_arg.get_default_value())

        self.spin_box.valueChanged.connect(self.spin_box_value_changed)

        self.slider.valueChanged.connect(self.slider_value_changed)

        h_box = QHBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.spin_box)
        self.v_box.addLayout(h_box)
        self.v_box.addStretch(1)

        is_mandatory = self.analysis_arg.is_mandatory()
        self.setProperty("is_mandatory", str(is_mandatory))

    def slider_value_changed(self, value):
        self.spin_box.setValue(value)
        # self.analysis_arg.set_argument_value(value)

    def spin_box_value_changed(self, value):
        self.slider.setValue(value)
        # self.analysis_arg.set_argument_value(value)

    def set_value(self, value):
        if value is not None:
            self.spin_box.setValue(value)

    def get_value(self):
        return self.slider.value()

    def to_stretch(self):
        """
        Indicate if the widget should take all the space of a horizontal layout how might share the space
        with another widget
        Returns: Boolean

        """
        return False


class AnalysisParametersApp(QWidget):
    """Class containing the parameters widgets"""
    def __init__(self, thread_name, progress_bar, analysis_name, config_handler, parent=None):
        QWidget.__init__(self)
        self.name = thread_name
        self.parent = parent
        self.config_handler = config_handler
        self.thread_list = []
        self.analysis_name = analysis_name
        self.progress_bar = progress_bar

        self.special_background_on = False

        self.cicada_analysis = None
        self.dataView = None
        self.analysis_tree_model = None
        # will be initialize when the param section will have been created
        self.param_section_widget = None
        self.analysis_arguments_handler = None

        # Add the scroll bar
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        # ScrollBarAlwaysOff = 1
        # ScrollBarAlwaysOn = 2
        # ScrollBarAsNeeded = 0
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)

        self.run_analysis_button = QPushButton("Run analysis", self)
        self.run_analysis_button.setEnabled(False)
        self.run_analysis_button.clicked.connect(self.run_analysis)

        self.load_arguments_button = QPushButton("Load a set of parameters", self)
        self.load_arguments_button.setEnabled(True)
        self.load_arguments_button.clicked.connect(self.load_arguments)

        self.see_all_yaml = QPushButton("Choose parameter files with keywords")
        self.see_all_yaml.setEnabled(True)
        self.see_all_yaml.clicked.connect(self.open_all_group)

        self.reset_arguments_button = QPushButton("Reset parameters to default value", self)
        self.reset_arguments_button.setEnabled(True)
        self.reset_arguments_button.clicked.connect(self.reset_arguments)
        # self.main_layout.addWidget(self.run_analysis_button)

        self.save_yaml_name_q_line = QLineEdit()
        self.save_yaml_name_q_line.returnPressed.connect(self.save_yaml_with_name)
        self.save_title = QPushButton()
        self.save_title.setText("Save parameters with keywords :")
        self.save_title.clicked.connect(self.save_yaml_with_name)

        self.hlayout_args_yaml = QHBoxLayout()
        self.hlayout_args_yaml.addWidget(self.save_title)
        self.hlayout_args_yaml.addWidget(self.save_yaml_name_q_line)

        self.setLayout(self.main_layout)
        # self.show()

        # setting size
        screen_geometry = QApplication.desktop().screenGeometry()
        # making sure the window is not bigger than the dimension of the screen
        width_window = min(800, screen_geometry.width() / 1.5)
        self.setMinimumSize(width_window, self.height())

        if self.config_handler.main_window_bg_pictures_displayed_by_default:
            self.set_random_background_picture()

    def load_arguments(self):
        """
        Will open a FileDialog to select a yaml file used to load arguments used for a previous analysis

        """
        print("cicada_parameters_gui: load_arguments")
        file_dialog = QFileDialog(self, "Loading arguments")

        # setting options
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        file_dialog.setOptions(options)

        # ARE WE TALKING ABOUT FILES OR FOLDERS
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Yaml files (*.yml *.yaml)")

        # OPENING OR SAVING
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)


        # SET THE STARTING DIRECTORY
        # default_value = self.analysis_arg.get_default_value()
        # if default_value is not None and isinstance(default_value, str):
        #     self.file_dialog.setDirectory(default_value)
        if file_dialog.exec_() == QDialog.Accepted:
            yaml_file = file_dialog.selectedFiles()[0]
            self.analysis_arguments_handler.load_analysis_argument_from_yaml_file(yaml_file)

    def save_yaml_with_name(self):
        """
        Save parameters as a YAML file under the name given by the user. The path is retrieved from the config file
        and if it doesn't exist a QFileDialog will be displayed to select the path
        """
        yaml_file_name = self.save_yaml_name_q_line.text()
        my_path = os.path.abspath(os.path.dirname(__file__))

        if yaml_file_name.strip() == "":
            return
        # TODO : Handle path with config handler
        with open(os.path.join(my_path, '../config/config.yaml'), 'r') as stream:
            path_save = yaml.safe_load(stream)
        try:
            dir_name = path_save['yaml_analysis_args_dir_name']
        except KeyError:
            self.file_dialog = QFileDialog(self, "Select Directory")
            # setting options
            options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.DontUseCustomDirectoryIcons

            self.file_dialog.setOptions(options)
            self.file_dialog.setFileMode(QFileDialog.DirectoryOnly)
            if self.file_dialog.exec_() == QDialog.Accepted:
                dir_name = self.file_dialog.selectedFiles()[0]  # returns a list
                self.file_dialog.setDirectory(dir_name)
            path_save.update({'yaml_analysis_args_dir_name': dir_name})
            with open(os.path.join(my_path, '../config/config.yaml'), 'w') as outfile:
                yaml.dump(path_save, outfile, default_flow_style=False)

        dir_name = os.path.join(dir_name, self.cicada_analysis.name)
        # self.cicada_analysis.set_yaml_name(name)
        self.cicada_analysis.analysis_arguments_handler.save_analysis_arguments_to_yaml_file(yaml_file_name=yaml_file_name, path_dir=dir_name)
        message_box = QMessageBox()
        message_box.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))
        message_box.setText(f"Parameters were successfully saved under the name {yaml_file_name}")
        message_box.exec()
        self.save_yaml_name_q_line.clear()

    def open_all_group(self):
        self.yaml_group_window = AllGroups(parent=self)
        yaml_list = self.get_analysis_yaml()
        self.yaml_group_window.populate_list(yaml_list)
        self.yaml_group_window.show()
        self.parent.main_window.object_created.append(self.yaml_group_window)

    def get_analysis_yaml(self):
        # TODO: Get path from config handler
        my_path = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(my_path, '../config/config.yaml'), 'r') as stream:
            path_save = yaml.safe_load(stream)
        path = path_save.get('yaml_analysis_args_dir_name', None)
        if path is None:
            return []
        dir_list = get_subdirs(current_path=path, depth=1)

        files_list = []

        for dir in dir_list:
            if self.analysis_name in dir:
                files_list = get_subfiles(current_path=os.path.join(path, dir), relative_path=True, depth=1)
        yaml_list = []
        for file in files_list:
            if file.endswith('yaml') or file.endswith('yml'):
                if self.analysis_name in file:
                    yaml_list.append(file)
        return yaml_list

    def tabula_rasa(self):
        """
        Erase the widgets and make an empty section

        """
        # clearing the widget to update it
        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        # self.scroll_area_widget_contents.setStyleSheet(self.current_style_sheet_background)
        self.run_analysis_button.setEnabled(False)

    def create_widgets(self, cicada_analysis):
        """

        Args:
            cicada_analysis (CicadaAnalysis): Chosen analysis

        """
        self.cicada_analysis = cicada_analysis

        # clearing the widget to update it
        self.tabula_rasa()

        self.analysis_arguments_handler = self.cicada_analysis.analysis_arguments_handler
        # list of instances of AnalysisArgument
        gui_widgets = self.analysis_arguments_handler.get_gui_widgets(group_by_family=True)

        # to_stretch
        index_widget = 0
        while index_widget < len(gui_widgets):
            gui_widget = gui_widgets[index_widget]
            next_widget = None
            if index_widget < (len(gui_widgets) - 1):
                next_widget = gui_widgets[index_widget + 1]
            if next_widget is None:
                # we add to the VBoxLayout
                self.layout.addWidget(gui_widget)
                # end of the loop anyway, so let's break
                break

            # otherwise, we have to decide if we put both in HBoxLayout
            if (not gui_widget.to_stretch()) and (not next_widget.to_stretch()):
                h_box = QHBoxLayout()
                h_box.addWidget(gui_widget)
                h_box.addWidget(next_widget)
                self.layout.addLayout(h_box)
                index_widget += 2
            else:
                self.layout.addWidget(gui_widget)
                index_widget += 1

        self.layout.addStretch(1)
        self.run_analysis_button.setEnabled(True)
        if self.config_handler.main_window_bg_pictures_displayed_by_default:
            self.set_random_background_picture()

    def set_random_background_picture(self):
        pic_path = self.config_handler.get_random_main_window_bg_picture(widget_id="analysis_params")
        if pic_path is None:
            return

        self.scroll_area_widget_contents.setStyleSheet(".QWidget{" +
                           f"background-image:url(\"{pic_path}\"); "
                           f"background-position: center top; "
                           f"background-repeat: repeat-xy;" + "}")  # no-repeat
        self.special_background_on = True

    def keyPressEvent(self, event):
        """

        Args:
            event: P -> set background picture

        Returns:

        """
        # setting background picture
        if event.key() == QtCore.Qt.Key_P:
            if self.special_background_on:
                self.scroll_area_widget_contents.setStyleSheet(
                    ".QWidget{background-image:url(\"\"); background-position: center;}")
                self.special_background_on = False
            else:
                self.set_random_background_picture()

    def reset_arguments(self):
        """Reset all arguments to default value"""
        self.analysis_arguments_handler.set_widgets_to_default_value()

    def run_analysis(self):
        """Check if the parameters are valid and then create a thread which will run the analysis"""
        if self.analysis_arguments_handler is None:
            return

        # first we check if analysis_arguments are filled correctly
        if not self.analysis_arguments_handler.check_arguments_validity():
            return

        # first we disable the button so we can launch a given analysis only once
        self.run_analysis_button.setEnabled(False)
        self.worker = Worker(self.name, self.cicada_analysis, self.analysis_arguments_handler, self.parent)
        self.thread_list.append(self.worker)
        self.worker.updateProgress.connect(self.progress_bar.update_progress_bar)
        self.worker.updateProgress2.connect(self.progress_bar.update_progress_bar_overview)
        self.worker.start()


class EmittingStream(QtCore.QObject):
    """Class managing the std.out redirection"""
    def __init__(self, parent=None):
        self.parent = parent
        self.terminal = sys.stdout
        self.textWritten = QtCore.Signal(str)

    def write(self, text):
        """
        Override of the write function used to display output
        Args:
            text (str): Python output from stdout

        """
        # Add thread name to the output when writting in the the widget
        current_thread = QThread.currentThread()
        thread_text = text + str(current_thread.name)
        self.terminal.write(str(text))
        dir_path = current_thread.cicada_analysis.get_results_path()
        self.parent.normalOutputWritten(thread_text, dir_path)


    def flush(self):
        pass


class EmittingErrStream(QtCore.QObject):
    """Class managing the std.err redirection"""
    def __init__(self, parent=None):
        self.parent = parent
        self.terminal = sys.stderr
        self.errWritten = QtCore.Signal(str)


    def write(self, text):
        """
        Override of the write function used to display output
        Args:
            text (str): Python output from stdout

        """

        # Add thread name to the output when writting in the the widget
        current_thread = QThread.currentThread()
        thread_text = text + str(current_thread.name)
        self.terminal.write(str(text))
        dir_path = current_thread.cicada_analysis.get_results_path()
        self.parent.errOutputWritten(thread_text, dir_path)


    def flush(self):
        pass

class AnalysisData(QWidget):

    def __init__(self, cicada_analysis, arguments_section_widget, config_handler, parent=None):
        QWidget.__init__(self, parent=parent)
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        # ScrollBarAlwaysOff = 1
        # ScrollBarAlwaysOn = 2
        # ScrollBarAsNeeded = 0
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.main_layout.addWidget(self.scrollArea)

        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)

        self.config_handler = config_handler

        self.analysis_state = AnalysisState(analysis_id=None, cicada_analysis=cicada_analysis,
                                       without_bringing_to_front=True)

        self.layout.addLayout(self.analysis_state)
        self.layout.addStretch(1)
        self.layout.addWidget(arguments_section_widget.see_all_yaml)
        self.layout.addLayout(arguments_section_widget.hlayout_args_yaml)
        self.layout.addWidget(arguments_section_widget.reset_arguments_button)
        self.layout.addWidget(arguments_section_widget.load_arguments_button)
        # adding a separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)
        self.layout.addWidget(arguments_section_widget.run_analysis_button)

        self.setLayout(self.main_layout)

        self.special_background_on = False

        if self.config_handler.main_window_bg_pictures_displayed_by_default:
            self.set_random_background_picture()

    def populate_session_list(self, session_list):
        """
        Add all session to the QListWidget
        Args:
            session_list (list): List of all sessions' identifier

        """
        for session in session_list:
            item = QListWidgetItem()
            item.setText(str(session.identifier))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            self.q_list.addItem(item)

    def set_random_background_picture(self):
        pic_path = self.config_handler.get_random_main_window_bg_picture(widget_id="analysis_data")
        if pic_path is None:
            return

        self.scroll_area_widget_contents.setStyleSheet(".QWidget{" +
                           f"background-image:url(\"{pic_path}\"); "
                           f"background-position: center top; "
                           f"background-repeat: repeat-xy;" + "}")  # no-repeat
        self.special_background_on = True

    def keyPressEvent(self, event):
        """

        Args:
            event: P -> set background picture

        Returns:

        """
        # setting background picture
        if event.key() == QtCore.Qt.Key_P:
            if self.special_background_on:
                self.scroll_area_widget_contents.setStyleSheet(
                    ".QWidget{background-image:url(\"\"); background-position: center;}")
                self.special_background_on = False
            else:
                self.set_random_background_picture()


class AnalysisPackage(QWidget):
    """Widget containing the whole analysis window"""

    def __init__(self, cicada_analysis, analysis_name, name, main_window, config_handler, parent=None):
        """

        Args:
            cicada_analysis (CicadaAnalysis): Chosen analysis
            analysis_name (str): Analysis name
            name (str): Analysis ID
            main_window (QMainWindow): Main Window
        """
        QWidget.__init__(self)
        super().__init__()
        self.name = name
        self.config_handler = config_handler
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))
        self.parent = parent
        self.cicada_analysis = cicada_analysis
        self.main_window = main_window
        self.closeEvent = self.on_close
        screenGeometry = QApplication.desktop().screenGeometry()
        # making sure the window is not bigger than the dimension of the screen
        width_window = min(1600, int(screenGeometry.width()*0.95))
        height_window = min(1000, int(screenGeometry.height()*0.95))
        self.resize(width_window, height_window)
        # self.setFixedSize(self.size())
        self.remaining_time_label = RemainingTime()
        self.progress_bar = ProgressBar(self.remaining_time_label, parent=self)
        self.progress_bar.setEnabled(False)
        cicada_analysis.progress_bar_analysis = self.progress_bar
        # print(cicada_analysis.analysis_arguments_handler)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_output = QLabel()
        self.text_output.setMinimumHeight(200)
        self.text_output.setWordWrap(True)
        self.text_output.setAlignment(Qt.AlignLeft)
        self.text_output.setAlignment(Qt.AlignTop)

        self.scrollAreaErr = QScrollArea()
        self.scrollAreaErr.setWidgetResizable(True)
        self.scrollAreaErr.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollAreaErr.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_output_err = QLabel()
        self.text_output_err.setMinimumHeight(60)
        self.text_output_err.setStyleSheet("color: red;")
        self.text_output_err.setWordWrap(True)
        self.text_output_err.setAlignment(Qt.AlignLeft)
        self.text_output_err.setAlignment(Qt.AlignTop)
        self.setWindowTitle(analysis_name)

        self.layout = QVBoxLayout()
        # self.hlayout = QHBoxLayout()
        self.analysis_param = QWidget()
        self.vlayout = QVBoxLayout()

        self.arguments_section_widget = AnalysisParametersApp(thread_name=self.name, progress_bar=self.progress_bar,
                                                              analysis_name=analysis_name, parent=self,
                                                              config_handler=self.config_handler)

        self.arguments_section_widget.create_widgets(cicada_analysis=cicada_analysis)
        # policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        # # policy.setHeightForWidth(True)
        # self.arguments_section_widget.setSizePolicy(policy)

        self.vlayout.addWidget(self.arguments_section_widget)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        # self.vlayout.addLayout(self.hlayout_yaml)
        self.analysis_param.setLayout(self.vlayout)
        self.analysis_data = AnalysisData(cicada_analysis=cicada_analysis,
                                          arguments_section_widget=self.arguments_section_widget,
                                          config_handler=self.config_handler)

        self.analysis_splitter = QSplitter(Qt.Horizontal)
        self.analysis_splitter.addWidget(self.analysis_data)
        self.analysis_splitter.addWidget(self.analysis_param)

        self.text_output_splitter = QSplitter(Qt.Vertical)
        self.text_output_splitter.setHandleWidth(1)
        self.text_output_splitter.setProperty('terminal', 'True')
        self.text_output_splitter.addWidget(self.scrollArea)
        self.text_output_splitter.addWidget(self.scrollAreaErr)

        self.scrollArea.setWidget(self.text_output)
        self.scrollAreaErr.setWidget(self.text_output_err)

        self.output_widget = QWidget()
        self.hlayout2 = QHBoxLayout()
        # put main window on top
        go_home_button = QPushButton()
        go_home_button.setProperty("home", "True")
        go_home_button.clicked.connect(partial(self.bring_to_front, main_window))
        self.hlayout2.addWidget(go_home_button)
        self.hlayout2.addWidget(self.progress_bar)
        self.hlayout2.addWidget(self.remaining_time_label)
        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.addLayout(self.hlayout2)
        self.bottom_layout.addWidget(self.text_output_splitter)
        self.output_widget.setLayout(self.bottom_layout)

        self.output_analysis_splitter = QSplitter(Qt.Vertical)
        self.output_analysis_splitter.addWidget(self.analysis_splitter)
        self.output_analysis_splitter.addWidget(self.output_widget)
        self.layout.addWidget(self.output_analysis_splitter)

        self.setLayout(self.layout)
        self.show()

    def bring_to_front(self, window_id, event):
        """
        Bring corresponding  window to the front (re-routed from the double click method)

        Args:
            window_id (QWidget) : Analysis Widget object
            event (QEvent) : Double click event
        """
        window_id.setWindowState(window_id.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        # For Windows/Linux
        window_id.activateWindow()
        # For Mac
        window_id.raise_()

    def normalOutputWritten(self, text, path):
        """
        Append std.out text to the QLabel and create a log file.

        Args:
            text (str): Output of the standard output in python interpreter
            path (str): path where we will output the log file
        """
        if self.name in text:
            text = text.replace(self.name, "\n")
            text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])

            text = self.text_output.text() + text
            self.text_output.setText(text)
            self.scrollArea.verticalScrollBar().setSliderPosition(self.text_output.height())
            file = open(os.path.join(path, "log.txt"), "w+")
            file.write(str(self.text_output.text()))
            file.close()

    def errOutputWritten(self, text, path):
        """
        Append std.err text to the QLabel and create an err file.

        Args:
            text (str): Output of the standard output in python interpreter
            path (str): path where we will output the err file

        """

        if self.name in text:
            text = text.replace(self.name, "\n")
            text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])
            file = open(os.path.join(path, "err.txt"), "w+")
            file.write(str(self.text_output_err.text()))
            file.close()
            text = self.text_output_err.text() + text
            self.text_output_err.setText(text)
            self.scrollAreaErr.verticalScrollBar().setSliderPosition(self.text_output.height())
            if "Traceback" in text:
                for thread in self.arguments_section_widget.thread_list:
                    if thread.name == self.name:
                        thread.crashed = True
                self.remaining_time_label.setText("Analysis crashed")
                self.progress_bar.setEnabled(False)
                obj = self.parent.analysis_overview
                eval('obj.' + self.name + '_progress_bar.setEnabled(False)')

    def on_close(self, event):
        """
        Check if an analysis is still on going and prompt the user to let him know then ask whether he still wants to
        close. If yes, delete the associated overview and stop the thread

        Args:
            event (QEvent): Qt Event triggered when attempting to close the window

        """
        thread_found = False
        for thread in self.arguments_section_widget.thread_list:
            if thread.name == self.name:
                thread_found = True
                if thread.run_state:
                    if thread.crashed:
                        self.main_window.object_created.remove(self)
                        thread.terminate()
                        obj = self.parent.analysis_overview
                        for attr in dir(obj):
                            if self.name in attr:
                                if "layout" in attr:
                                    eval('obj.layout.removeItem( obj.' + attr + ')')
                                else:
                                    eval('obj.' + attr + '.setParent(None)')
                                    eval('obj.' + attr + '.deleteLater()')
                    else:
                        self.confirm_quit = QMessageBox()
                        self.confirm_quit.setWindowTitle("CICADA")
                        self.confirm_quit.setText("The analysis is still ongoing, do you still want to quit ?")
                        self.confirm_quit.setStandardButtons(QMessageBox.Yes)
                        self.confirm_quit.addButton(QMessageBox.No)
                        self.confirm_quit.setDefaultButton(QMessageBox.No)
                        if self.confirm_quit.exec() == QMessageBox.Yes:
                            self.progress_bar.setEnabled(False)
                            self.main_window.object_created.remove(self)
                            thread.terminate()
                            obj = self.parent.analysis_overview
                            for attr in dir(obj):
                                if self.name in attr:
                                    if "layout" in attr:
                                        eval('obj.layout.removeItem( obj.' + attr + ')')
                                    else:
                                        eval('obj.' + attr + '.setParent(None)')
                                        eval('obj.' + attr + '.deleteLater()')
                        else:
                            event.ignore()

                else:
                    self.main_window.object_created.remove(self)
                    obj = self.parent.analysis_overview
                    for attr in dir(obj):
                        if self.name in attr:
                            if "layout" in attr:
                                eval('obj.layout.removeItem( obj.' + attr + ')')
                            else:
                                eval('obj.' + attr + '.setParent(None)')
                                eval('obj.' + attr + '.deleteLater()')
        if not thread_found:
            self.main_window.object_created.remove(self)
            obj = self.parent.analysis_overview
            for attr in dir(obj):
                if self.name in attr:
                    if "layout" in attr:
                        eval('obj.layout.removeItem( obj.' + attr + ')')
                    else:
                        eval('obj.' + attr + '.setParent(None)')
                        eval('obj.' + attr + '.deleteLater()')


class Worker(QtCore.QThread):
    """Thread to manage multiple analysises at the same time"""

    # Signals to update the progress bar in the analysis window and overview
    updateProgress = QtCore.Signal(float, float, float)
    updateProgress2 = QtCore.Signal(str, float, float)

    def __init__(self, name, cicada_analysis, analysis_arguments_handler, parent):
        """

        Args:
            name (str): Analysis ID, should be unique
            cicada_analysis (CicadaAnalysis): the analysis run in the thread
            analysis_arguments_handler:
        """
        QtCore.QThread.__init__(self)
        self.name = name
        self.crashed = False
        self.parent = parent
        self.run_state = False
        self.cicada_analysis = cicada_analysis
        self.analysis_arguments_handler = analysis_arguments_handler

    def run(self):
        """Run the analysis"""
        self.run_state = True
        sys.stdout = EmittingStream(self.parent)
        sys.excepthook = except_hook
        # Comment to debug, else we will get unhandled python exception
        sys.stderr = EmittingErrStream(self.parent)
        self.analysis_arguments_handler.run_analysis()
        self.setProgress(self.name, new_set_value=100)
        self.run_state = False

    def setProgress(self, name, time_elapsed=0, increment_value=0, new_set_value=0):
        """
        Emit the new value of the progress bar and time remaining

        Args:
            name (str): Analysis ID
            time_elapsed (float): Start elpased (in sec)
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar


        """
        self.updateProgress.emit(time_elapsed, increment_value, new_set_value)
        self.updateProgress2.emit(name, increment_value, new_set_value)

    def set_results_path(self, results_path):
        """
        Set the selected path to the results in the "Open result folder" button in the corresponding overview

        Args:
            results_path (str): Path to the results

        """
        obj = self.parent.parent.analysis_overview
        if eval('obj.' + self.name + '_button.result_path') is None:
            exec('obj.' + self.name + '_button.result_path = "' + results_path + '"')
            eval('obj.' + self.name + '_button.result_button.setEnabled(True)')
        else:
            pass

class ProgressBar(QProgressBar):
    """Class containing the progress bar of the current analysis"""
    def __init__(self, remaining_time_label, parent=None):
        """

        Args:
            remaining_time_label: Associated analysis remaining time
        """
        QProgressBar.__init__(self)
        self.setMinimum(0)
        self.parent = parent
        self.remaining_time_label = remaining_time_label
        self.last_time_elapsed = 0

    def update_progress_bar(self, time_elapsed, increment_value=0, new_set_value=0):
        """
        Update the progress bar in the analysis widget and the corresponding remaining time
        Args:
            time_elapsed (float): Time elepased since beginning of analysis, in seconds
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar

        Returns:

        """
        self.current_thread = QThread.currentThread()
        self.setEnabled(True)

        # useful for the last called to set the bar at 100%
        if time_elapsed == 0:
            time_elapsed = self.last_time_elapsed
        else:
            self.last_time_elapsed = time_elapsed

        if new_set_value != 0:
            self.setValue(new_set_value)

        if increment_value != 0:
            self.setValue(self.value() + increment_value)

        if self.isEnabled() and self.value() != 0:
            if self.value() == 100:
                self.remaining_time_label.update_remaining_time(self.value(), time_elapsed=time_elapsed,
                                                                done=True)
            else:
                self.remaining_time_label.update_remaining_time(self.value(), time_elapsed=time_elapsed)

    def update_progress_bar_overview(self, name, increment_value=0, new_set_value=0):
        """
        Update the overview progress bar

        Args:
            name (str): Analysis ID
            time_started (float): Start time of the analysis
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar

        """
        obj = self.parent.parent.analysis_overview
        try:
            progress_bar_instance = getattr(obj,  name + '_progress_bar')
            progress_bar_instance.setEnabled(True)
            if new_set_value != 0:
                progress_bar_instance.setValue(new_set_value)

            if increment_value != 0:
                progress_bar_instance.setValue(progress_bar_instance.value() + increment_value)
            if progress_bar_instance.isEnabled() and progress_bar_instance.value() != 0:
                progress_bar_instance.setEnabled(True)
        except:
            pass


class RemainingTime(QLabel):
    """Class containing the remaining time of the analysis"""
    def __init__(self, parent=None):
        QLabel.__init__(self, parent=parent)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(self.size())
        self.setText("Time remaining : ")

    def update_remaining_time(self, progress_value, time_elapsed, done=False):
        """
        Update the remaining time
        Args:
            progress_value (float): Current progress bar value
            time_elapsed (float): Time elepased since the beginning of the analysis (in sec)
            done (bool): True if the analysis is done and false if still running

        """
        if not done:
            remaining_time = time_elapsed * (100 / progress_value)
            remaining_time_text = self.correct_time_converter(remaining_time)
            time_elapsed_text = self.correct_time_converter(time_elapsed)
            self.setText("Time remaining : " + time_elapsed_text + "/" + remaining_time_text)
        else:
            time_elapsed_text = self.correct_time_converter(time_elapsed)
            self.setText("Analysis done in " + time_elapsed_text)

    @staticmethod
    def correct_time_converter(time_to_convert):
        """
        Convert a float in a correct duration value
        Args:
            time_to_convert (float): Float value representing seconds to be converted in a correct duration with MM.SS

        Returns:
            time_text (str): String of the correct duration
        """
        time_to_convert_str = str(time_to_convert)
        dot_index = time_to_convert_str.find(".")
        if dot_index == -1:
            seconds = time_to_convert
            m_sec = "00"
        else:
            seconds = int(time_to_convert_str[:dot_index])
            if dot_index < len(time_to_convert_str)-1:
                m_sec = time_to_convert_str[dot_index+1:min(dot_index+3, len(time_to_convert_str))]
            else:
                m_sec = "00"
        # converting in minutes
        minutes = seconds // 60
        seconds_remaining = str(seconds % 60)
        if len(seconds_remaining) == 1:
            seconds_remaining = "0" + seconds_remaining
        time_text = ""
        if minutes >= 1:
            minutes_str = str(minutes)
            if len(minutes_str) == 1:
                minutes_str = "0" + minutes_str
            time_text = time_text + minutes_str + ":"
        else:
            time_text = time_text + "00" + ":"
        time_text = time_text + seconds_remaining + "." + m_sec

        return time_text

def clearvbox(self, L=False):
    if not L:
        L = self.vbox
    if L is not None:
        while L.count():
            item = L.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()
            else:
                self.clearvbox(item.layout())

def except_hook(cls, exception, traceback):
    """Redirect exception to std.err so we can display stack trace on exceptions"""
    sys.__excepthook__(cls, exception, traceback)
