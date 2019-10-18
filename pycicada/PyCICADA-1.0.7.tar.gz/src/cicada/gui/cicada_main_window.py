from qtpy.QtWidgets import *
from qtpy import QtGui
from qtpy import QtCore
from qtpy.QtCore import Qt
import os
from copy import deepcopy
import sys
from functools import partial
import cicada.preprocessing.utils as utils
import yaml
from cicada.analysis.cicada_analysis_nwb_wrapper import CicadaAnalysisNwbWrapper
from cicada.gui.cicada_analysis_tree_gui import AnalysisTreeApp
from cicada.gui.cicada_analysis_overview import AnalysisOverview
from cicada.gui.cicada_analysis_parameters_gui import AnalysisPackage
from cicada.gui.cicada_group_sort import SessionsWidget
from cicada.gui.cicada_all_group import AllGroups
import platform
from sortedcontainers import SortedDict

import ctypes


class CicadaMainWindow(QMainWindow):
    """Main window of the GUI"""
    def __init__(self, config_handler):
        super().__init__()
        # To display an the window icon as the application icon in the task bar on Windows
        if platform.system() == "Windows":
            myappid = u'cossart.cicada.gui.alpha'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))

        # ----- misc attributes -----
        self.labels = []
        self.to_add_labels = []

        # attributes concerning menus, groups etc...
        self.group_menu_actions = dict()
        # associated to each action name an id that link it to the corresponding attribution in CicadaWrapperInstance
        self.actions_names_id = dict()

        # allows to access config param
        self.config_handler = config_handler

        self.createActions()
        self.createMenus()
        self.object_created = []
        self.labels = []
        self.setWindowTitle("CICADA")

        screenGeometry = QApplication.desktop().screenGeometry()
        # making sure the window is not bigger than the dimension of the screen
        width_window = min(1500, screenGeometry.width())
        # width_window = screenGeometry.width()
        height_window = min(800, screenGeometry.height())
        self.resize(width_window, height_window)
        self.param_list = []
        self.param_group_list = []
        self.grouped = False
        self.sorted = False
        self.nwb_path_list = dict()
        # contains the data, will be instances of CicadaAnalysisFormatWrapper
        # the key is the identifier of the data file, value is the instance
        self.data_dict = dict()

        self.openWindow()
        self.load_data_from_config()


    def load_group_from_config(self):
        """Load groups from a YAML file in the config folder"""
        my_path = os.path.abspath(os.path.dirname(__file__))

        group_file_name = os.path.join(my_path,"../config/group.yaml")
        self.group_data = dict()
        self.all_groups = dict()
        if os.path.isfile(group_file_name):
            with open(group_file_name, 'r') as stream:
                self.group_data = yaml.safe_load(stream)
            self.all_groups = deepcopy(self.group_data)
            if self.group_data:
                keys_to_del = []
                for key, value in self.group_data.items():
                    missing_file = False
                    for file in value:
                        if file not in self.nwb_path_list.values():
                            missing_file = True
                    if missing_file:
                        keys_to_del.append(key)
                for key in keys_to_del:
                    self.group_data.pop(key)
            self.grouped_labels = []
            if self.group_data:
                self.grouped = True
                for value in self.group_data.values():
                    nwb_file_list = []
                    for file in value:
                        nwb_wrapper = CicadaAnalysisNwbWrapper(data_ref=file)
                        self.data_dict[nwb_wrapper.identifier] = nwb_wrapper
                        nwb_file_list.append(nwb_wrapper.identifier)
                    self.grouped_labels.append(nwb_file_list)
                self.showGroupMenu.setEnabled(True)
                self.addGroupDataMenu.setEnabled(True)
                self.selectGroupMenu.setEnabled(True)
                self.populate_menu()
            else:
                self.showGroupMenu.setEnabled(False)
                self.addGroupDataMenu.setEnabled(False)
                self.selectGroupMenu.setEnabled(False)
                self.showGroupMenu.clear()
                self.selectGroupMenu.clear()
                self.addGroupDataMenu.clear()


    def load_data_from_config(self):
        """Check if the last dir opened is saved in config and load it automatically"""
        self.labels = []
        self.to_add_labels = []
        if self.config_handler.files_to_analyse_dir_name is not None:
            self.load_data_from_dir(dir_name=self.config_handler.files_to_analyse_dir_name, method='clear')

    def open_new_dataset(self):
        """Open a directory"""

        self.labels = []
        self.to_add_labels = []
        self.nwb_path_list = dict()
        self.grouped_labels = []
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
            self.load_data_from_dir(dir_name=dir_name, method='clear')

    def add_data(self):
        """Open a directory"""

        self.to_add_labels = []
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
            self.load_data_from_dir(dir_name=dir_name, method='add')

    def load_data_from_dir(self, dir_name, method):
        """
        Load data (currently only NWB) from selected directory

        Args:
            dir_name (str): Path to data
            method (str): String to choose whether to add data to the existing dataset or open a new one,
             takes two values : 'add' or 'clear'

        """

        # TODO: deal with the different format
        # TODO: decide if we should add those nwb to the ones already opened (if that's the case)
        #  or erase the ones present and replace them by the new one.
        #  probably best to have 2 options on the menu open new, and something like add data
        file_names = []
        # look for filenames in the first directory, if we don't break, it will go through all directories
        for (dirpath, dirnames, local_filenames) in os.walk(dir_name):
            file_names.extend(local_filenames)
            break
        for file_name in file_names:
            if file_name.endswith(".nwb"):
                nwb_wrapper = CicadaAnalysisNwbWrapper(data_ref=os.path.join(dir_name, file_name))
                self.data_dict[nwb_wrapper.identifier] = nwb_wrapper
                self.nwb_path_list[nwb_wrapper.identifier] = os.path.join(dir_name, file_name)
                self.to_add_labels.append(nwb_wrapper.identifier)
        self.labels = self.labels + self.to_add_labels
        # checking there is at least one data file loaded
        if len(self.data_dict) > 0:
            if method == 'clear':
                self.musketeers_widget.session_widget.populate(self.labels, method)
                self.load_group_from_config()
            else:
                self.musketeers_widget.session_widget.populate(self.to_add_labels, method)
            self.sortMenu.setEnabled(True)
            self.groupMenu.setEnabled(True)
            # then we save the last location opened in the yaml file in config
            self.save_last_data_location(dir_name=dir_name)

    def save_last_data_location(self, dir_name):
        """
        Keep path to last data directory selected in a YAML in config

        Args:
            dir_name (str): Path to data to be saved

        """
        # TODO think about where to keep the config yaml file

        config_file_name = self.config_handler._path_to_config_file
        config_dict = None
        if os.path.isfile(config_file_name):
            with open(config_file_name, 'r') as stream:
                config_dict = yaml.safe_load(stream)
        if config_dict is None:
            config_dict = dict()
        config_dict["dir_name"] = dir_name
        with open(config_file_name, 'w') as outfile:
            yaml.dump(config_dict, outfile, default_flow_style=False)

    def populate_menu(self):
        """Populate the menu to load groups"""
        # TODO : Performance issue ?
        self.showGroupMenu.clear()
        self.addGroupDataMenu.clear()
        self.selectGroupMenu.clear()
        counter = 0
        for group_name in self.group_data.keys():
            counter +=1
            exec('self.groupAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupAct' + str(counter) + '.triggered.connect(partial(self.load_group, group_name))')
            exec('self.groupAddAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupAddAct' + str(counter) + '.triggered.connect(partial(self.add_group_data, group_name))')
            exec('self.groupSelectAct' + str(counter) + ' = QAction("' + group_name+'", self)')
            eval('self.groupSelectAct' + str(counter) + '.triggered.connect(partial(self.select_group, group_name))')
            self.showGroupMenu.addAction(eval('self.groupAct' + str(counter)))
            self.addGroupDataMenu.addAction(eval('self.groupAddAct' + str(counter)))
            self.selectGroupMenu.addAction(eval('self.groupSelectAct' + str(counter)))


    def select_group(self, group_name):
        """
        Select all sessions of a group

        Args:
            group_name (str) : Name of the group saved in YAML

        """
        for path_list in {group_name: self.all_groups.get(group_name)}.values():
            for path in path_list:
                nwb_wrapper = CicadaAnalysisNwbWrapper(data_ref=path)
                self.musketeers_widget.session_widget.select_item(nwb_wrapper.identifier)

    def load_group(self, group_name):
        """
        Load a group of saved sessions, it will clear the current session list

        Args:
            group_name (str) : Name of the group saved in YAML

        """
        self.sorted = False
        self.grouped = False
        self.nwb_path_list = dict()
        self.labels = []
        for path_list in {group_name: self.all_groups.get(group_name)}.values():
            for path in path_list:
                nwb_wrapper = CicadaAnalysisNwbWrapper(data_ref=path)
                self.labels.append(nwb_wrapper.identifier)
                self.nwb_path_list.update({nwb_wrapper.identifier: path})
        self.musketeers_widget.session_widget.populate(self.labels)
        self.musketeers_widget.session_widget.update_text_filter()
        self.groupMenu.setEnabled(True)
        self.sortMenu.setEnabled(True)

    def add_group_data(self, group_name):
        """
        Add a group of saved sessions to the current list of session

        Args:
            group_name (str) : Name of the group saved in YAML

        """
        self.sorted = False
        self.grouped = False
        self.labels_to_add = []
        for path in self.all_groups.get(group_name):
            nwb_wrapper = CicadaAnalysisNwbWrapper(data_ref=path)
            # self.labels.append(nwb_file.identifier)
            self.nwb_path_list.update({nwb_wrapper.identifier: path})
            self.labels_to_add.append(nwb_wrapper.identifier)
        self.musketeers_widget.session_widget.populate(self.labels_to_add, 'add')
        self.musketeers_widget.session_widget.update_text_filter()
        self.groupMenu.setEnabled(True)
        self.sortMenu.setEnabled(True)


    def createMenus(self):
        """Create menu bar and put some menu in it"""

        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.addAct)
        self.fileMenu.addSeparator()
        # self.fileMenu.addAction(self.showSessionAct)
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.viewMenu = QMenu("&View", self)

        self.sortMenu = QMenu("Sort by", self.viewMenu, enabled=False)
        self.groupMenu = QMenu("Group by", self.viewMenu, enabled=False)

        self.showGroupMenu = QMenu("Load Group", self.fileMenu, enabled=False)
        self.addGroupDataMenu = QMenu('Add Group', self.fileMenu, enabled=False)
        self.selectGroupMenu = QMenu("Select group", self.fileMenu, enabled=True)
        self.fileMenu.addMenu(self.showGroupMenu)
        self.fileMenu.addMenu(self.addGroupDataMenu)
        self.fileMenu.addMenu(self.selectGroupMenu)
        self.fileMenu.addAction(self.seeAllGroupAct)
        self.viewMenu.addMenu(self.groupMenu)
        self.viewMenu.addMenu(self.sortMenu)

        # Add filters to "Sort by"
        self.create_sort_menu()
        self.sortMenu.addAction(self.ageSortAct)
        self.sortMenu.addAction(self.sexSortAct)
        self.sortMenu.addAction(self.genotypeSortAct)
        self.sortMenu.addAction(self.speciesSortAct)
        self.sortMenu.addAction(self.subjectIDSortAct)
        self.sortMenu.addAction(self.weightSortAct)
        self.sortMenu.addAction(self.birthSortAct)
        self.sortMenu.addSeparator()

        self.sortMenu.addAction(self.fluorescenceSortAct)
        self.sortMenu.addAction(self.imagesegSortAct)
        self.sortMenu.addAction(self.rasterSortAct)

        # Add filters to "Group by"
        self.create_group_menu()
        for q_action in self.group_menu_actions.values():
            self.groupMenu.addAction(q_action)
        # self.groupMenu.addAction(self.ageGroupAct)
        # self.groupMenu.addAction(self.sexGroupAct)
        # self.groupMenu.addAction(self.genotypeGroupAct)
        # self.groupMenu.addAction(self.speciesGroupAct)
        # self.groupMenu.addAction(self.subjectIDGroupAct)
        # self.groupMenu.addAction(self.weightGroupAct)
        # self.groupMenu.addAction(self.birthGroupAct)

        # self.groupMenu.addSeparator()

        # self.groupMenu.addAction(self.fluorescenceGroupAct)
        # self.groupMenu.addAction(self.imagesegGroupAct)
        # self.groupMenu.addAction(self.rasterGroupAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def create_group_menu(self):
        """Create group menu"""
        self.group_menu_actions = SortedDict()
        self.actions_names_id = dict()

        actions_names = ["Age", "Sex", "Genotype", "Species", "Subject ID", "Weight"]
        # TODO: handle dates, and handle boolean
        # "Birth", "with neural activity"

        for action_name in actions_names:
            if action_name == "Subject ID":
                self.actions_names_id[action_name] = "subject_id"
                continue
            self.actions_names_id[action_name] = action_name.lower()

        for action_name in actions_names:
            q_action = QAction(action_name, self, checkable=True)
            q_action.triggered.connect(partial(self.uncheck_group, action_name))
            q_action.triggered.connect(partial(self.on_group, action_name))
            self.group_menu_actions[action_name] = q_action

    def create_sort_menu(self):
        """Create sort menu"""

        self.ageSort = QCheckBox("&Age", self.sortMenu)
        self.ageSortAct = QWidgetAction(self.sortMenu)
        self.ageSortAct.setDefaultWidget(self.ageSort)
        self.ageSort.stateChanged.connect(partial(self.on_sort, "age"))

        self.sexSort = QCheckBox("&Sex", self.sortMenu)
        self.sexSortAct = QWidgetAction(self.sortMenu)
        self.sexSortAct.setDefaultWidget(self.sexSort)
        self.sexSort.stateChanged.connect(partial(self.on_sort,"sex"))

        self.genotypeSort = QCheckBox("&Genotype", self.sortMenu)
        self.genotypeSortAct = QWidgetAction(self.sortMenu)
        self.genotypeSortAct.setDefaultWidget(self.genotypeSort)
        self.genotypeSort.stateChanged.connect(partial(self.on_sort,"genotype"))

        self.speciesSort = QCheckBox("&Species", self.sortMenu)
        self.speciesSortAct = QWidgetAction(self.sortMenu)
        self.speciesSortAct.setDefaultWidget(self.speciesSort)
        self.speciesSort.stateChanged.connect(partial(self.on_sort,"species"))

        self.subjectIDSort = QCheckBox("&Subject ID", self.sortMenu)
        self.subjectIDSortAct = QWidgetAction(self.sortMenu)
        self.subjectIDSortAct.setDefaultWidget(self.subjectIDSort)
        self.subjectIDSort.stateChanged.connect(partial(self.on_sort,"subject_id"))

        self.weightSort = QCheckBox("&Weight", self.sortMenu)
        self.weightSortAct = QWidgetAction(self.sortMenu)
        self.weightSortAct.setDefaultWidget(self.weightSort)
        self.weightSort.stateChanged.connect(partial(self.on_sort,"weight"))

        self.birthSort = QCheckBox("&Birth", self.sortMenu)
        self.birthSortAct = QWidgetAction(self.sortMenu)
        self.birthSortAct.setDefaultWidget(self.birthSort)
        self.birthSort.stateChanged.connect(partial(self.on_sort,"birth"))


        self.fluorescenceSort = QCheckBox("&Has fluorescence", self.sortMenu)
        self.fluorescenceSortAct = QWidgetAction(self.sortMenu)
        self.fluorescenceSortAct.setDefaultWidget(self.fluorescenceSort)
        self.fluorescenceSort.stateChanged.connect(partial(self.on_sort,"fluorescence"))

        self.imagesegSort = QCheckBox("&Has image segmentation", self.sortMenu)
        self.imagesegSortAct = QWidgetAction(self.sortMenu)
        self.imagesegSortAct.setDefaultWidget(self.imagesegSort)
        self.imagesegSort.stateChanged.connect(partial(self.on_sort,"imagesegmentation"))

        self.rasterSort = QCheckBox("&Has rasterplot", self.sortMenu)
        self.rasterSortAct = QWidgetAction(self.sortMenu)
        self.rasterSortAct.setDefaultWidget(self.rasterSort)
        self.rasterSort.stateChanged.connect(partial(self.on_sort,"raster"))


    def createActions(self):
        """Create some QAction"""

        self.openAct = QAction("&Open new dataset...", self, shortcut="Ctrl+O", triggered=self.open_new_dataset)
        self.addAct = QAction("&Add data to current dataset...", self, shortcut="Ctrl+P", triggered=self.add_data)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.exitAct.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)
        # self.showSessionAct = QAction("&Show session", self, triggered=self.openWindow)
        self.showGroupAct = QAction("&Show all groups", self)
        self.seeAllGroupAct = QAction('&See all groups', self, triggered=self.see_all_groups)


    def see_all_groups(self):
        """Display a widget with all existing groups"""
        self.all_group_window = AllGroups(widget='main', parent=self)
        if self.all_groups:
            self.all_group_window.populate_list(self.all_groups.keys())
        self.all_group_window.show()
        self.object_created.append(self.all_group_window)

    def uncheck_all_sort(self):
        """Uncheck all checkboxes in sort menu"""

        self.param_list = []
        self.ageSort.setChecked(False)
        self.sexSort.setChecked(False)
        self.speciesSort.setChecked(False)
        self.genotypeSort.setChecked(False)
        self.subjectIDSort.setChecked(False)
        self.weightSort.setChecked(False)
        self.birthSort.setChecked(False)
        self.fluorescenceSort.setChecked(False)
        self.imagesegSort.setChecked(False)
        self.rasterSort.setChecked(False)

    def uncheck_group(self, param=''):
        """
        Uncheck group menu parameter

        Args:
            param (str): Parameter name to uncheck

        """
        self.param_group_list = []
        for q_action in self.group_menu_actions.values():
            q_action.setChecked(False)

    def on_group(self, param, state):
        """
        Give group list and parameters value to populate QListWidget

        Args:
            param (str): Parameter to group by
            state (int): State of the checkbox
        """
        self.grouped = True
        if state > 0:  # From unchecked to checked
            self.sorted = False
            self.uncheck_all_sort()
            self.musketeers_widget.session_widget.update_text_filter(param)
            if param not in self.param_group_list:
                self.param_group_list.append(param)

            dict_group = SortedDict()
            # data is an instance of CicadaAnalysisWrapper
            for data in self.data_dict.values():
                param_id = self.actions_names_id.get(param, param)
                if param_id.lower().startswith("has"):
                    continue
                # print(f"data dir {dir(data)}")
                value = getattr(data, param_id.lower(), None)
                # print(f"value {value}")
                # value = data.age
                if value is None:
                    value = "NA"
                else:
                    if isinstance(value, str) and ("_" in value):
                        pass
                    else:
                        # changing it as int or float, use
                        try:
                            value = int(value)
                        except ValueError:
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                value = utils.ComparableItem(value=value)
                if value not in dict_group:
                    # print(f"value {str(value)}")
                    dict_group[value] = []
                dict_group[value].append(data)

            self.musketeers_widget.session_widget.form_group(dict_group)
        else:  # From checked to unchecked
            if param in self.param_group_list:
                if len(self.param_group_list) == 1:
                    self.param_group_list = []
                else:
                    self.param_group_list.remove(param)
            self.grouped = False
            self.musketeers_widget.session_widget.update_text_filter()
            self.musketeers_widget.session_widget.populate(self.labels)

    def on_sort(self, param, state):
        """
        Give sorted list to populate QListWidget
        Args:
            param (str): Parameter to sort by
            state (int): State of the checkbox

        """
        if state > 0:  # From unchecked to checked
            self.grouped = False
            self.uncheck_group()
            if param not in self.param_list:
                self.param_list.append(param)
        else:  # From checked to unchecked
            if param in self.param_list:
                if len(self.param_list) == 1:
                    self.param_list = []
                else:
                    self.param_list.remove(param)
        self.sorted_labels = utils.sort_by_param(self.nwb_path_list.values(), self.param_list)
        if self.param_list:
            self.sorted = True
        else:
            self.sorted = False
        self.musketeers_widget.session_widget.update_text_filter()
        self.musketeers_widget.session_widget.populate(self.sorted_labels)

    def about(self):
        """Small about QMessageBox for the project"""
        self.about_box = QDialog()
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.about_box.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))
        self.about_box.setWindowTitle("About CICADA")
        self.object_created.append(self.about_box)
        self.about_box.setMinimumSize(275, 125)
        vlayout = QVBoxLayout()

        github_layout = QHBoxLayout()
        icon_label_github = QLabel()
        icon_label_github.setScaledContents(True)
        icon_label_github.setMaximumSize(48, 48)
        icon_github_box = QtGui.QPixmap(os.path.join(my_path, 'icons/svg/github-logo.svg'))
        icon_label_github.setPixmap(icon_github_box)
        label_github_box = QLabel(self.about_box)
        label_github_box.setAlignment(Qt.AlignCenter)
        label_github_box.setTextFormat(Qt.RichText)
        label_github_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label_github_box.setOpenExternalLinks(True)
        label_github_box.setText("<a href=\"https://github.com/pappyhammer/cicada\">Github link!</a>")
        github_layout.addWidget(icon_label_github)
        github_layout.addWidget(label_github_box)

        doc_layout = QHBoxLayout()
        icon_label_doc = QLabel()
        icon_label_doc.setScaledContents(True)
        icon_label_doc.setMaximumSize(48, 48)
        icon_doc_box = QtGui.QPixmap(os.path.join(my_path, 'icons/svg/doc.svg'))
        icon_label_doc.setPixmap(icon_doc_box)
        label_doc_box = QLabel(self.about_box)
        label_doc_box.setAlignment(Qt.AlignCenter)
        label_doc_box.setTextFormat(Qt.RichText)
        label_doc_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label_doc_box.setOpenExternalLinks(True)
        label_doc_box.setText("<a href=\"https://readthedocs.org/\">Documentation link!</a>")
        doc_layout.addWidget(icon_label_doc)
        doc_layout.addWidget(label_doc_box)

        vlayout.addLayout(github_layout)
        vlayout.addLayout(doc_layout)
        self.about_box.setLayout(vlayout)
        self.about_box.show()

    def openWindow(self):
        """Open all widgets in a CentralWidget and call some menus that needed those widgets"""
        # self.showSessionAct.setEnabled(False)
        self.musketeers_widget = MusketeersWidget(config_handler=self.config_handler, cicada_main_window=self)
        self.setCentralWidget(self.musketeers_widget)
        self.saveGroupMenu = QAction('Save Group', self.fileMenu)
        self.fileMenu.addAction(self.saveGroupMenu)
        self.saveGroupMenu.triggered.connect(self.musketeers_widget.session_widget.save_group)

    def closeEvent(self, event):
        """
        Close all analyses windows on main window close
        """

        self.object_created = utils.flatten(self.object_created)
        copied_list = self.object_created.copy()
        for obj in copied_list:
            if isinstance(obj, AnalysisPackage):
                obj.close()
            else:
                obj.close()
                self.object_created.remove(obj)

        if self.object_created:
            event.ignore()
        else:
            self.close()


class MusketeersWidget(QWidget):
    """
    Gather in a layout the 3 main sub-windows composing the gui: displaying the subject sessions,
    the analysis tree and an overview of the running analysis
    """
    def __init__(self, config_handler, cicada_main_window=None):
        QWidget.__init__(self, parent=cicada_main_window)
        self.cicada_main_window = cicada_main_window
        self.config_handler = config_handler

        self.layout = QHBoxLayout()
        to_analysis_button = QPushButton()
        to_analysis_button.setProperty("cicada", "True")

        self.session_widget = SessionsWidget(cicada_main_window=cicada_main_window, to_analysis_button=to_analysis_button,
                                             config_handler=self.config_handler)
        self.layout.addWidget(self.session_widget)

        self.layout.addWidget(to_analysis_button)

        to_parameters_button = QPushButton()
        to_parameters_button.setProperty("cicada", "True")

        analysis_tree_app = AnalysisTreeApp(parent=cicada_main_window, to_parameters_button=to_parameters_button,
                                            config_handler=self.config_handler)

        self.session_widget.analysis_tree = analysis_tree_app
        self.layout.addWidget(analysis_tree_app)

        self.layout.addWidget(to_parameters_button)

        # analysis_param_widget = AnalysisParametersApp()
        analysis_overview_widget = AnalysisOverview(parent=cicada_main_window, config_handler=self.config_handler)
        analysis_tree_app.analysis_overview = analysis_overview_widget
        self.layout.addWidget(analysis_overview_widget)
        # analysis_tree_app.arguments_section_widget = analysis_param_widget
        # useful to empty the arguments section when we click on the to_analysis_button
        # self.session_widget.arguments_section_widget = analysis_param_widget
        self.session_widget.analysis_overview_widget = analysis_overview_widget
        self.setLayout(self.layout)
