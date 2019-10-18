from qtpy.QtWidgets import *
from qtpy import QtGui
from qtpy import QtCore
from qtpy.QtCore import Qt
import os
import subprocess
import platform

class AllGroups(QWidget):
    """Class containing the widget used to display all created group found"""
    def __init__(self, widget='', parent=None):
        QWidget.__init__(self)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))
        self.layout = QVBoxLayout()
        self.parent = parent
        self.parent_widget = widget
        self.group_list = QListWidget(self)
        self.group_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.group_list.customContextMenuRequested.connect(self.showContextMenu)
        self.group_list.doubleClicked.connect(self.double_click_event)
        self.hlayout = QHBoxLayout()
        if widget == "main":
            self.setWindowTitle("All sessions groups")

            self.layout.addWidget(self.group_list)
            self.group_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.load_button = QPushButton('Load group')
            self.load_button.clicked.connect(self.load_item)
            self.add_button = QPushButton('Add group')
            self.add_button.clicked.connect(self.add_group)
            self.hlayout.addWidget(self.load_button)
            self.hlayout.addWidget(self.add_button)
            self.layout.addLayout(self.hlayout)
        else:
            self.setWindowTitle("All analysis parameters files")
            self.hlayout.addWidget(self.group_list)
            self.remove_shortcut = QShortcut(QtGui.QKeySequence("Delete"), self)
            self.remove_shortcut.activated.connect(self.remove_item)
            self.remove_param_file = QPushButton()
            self.remove_param_file.setIcon(QtGui.QIcon('gui/icons/svg/minus.svg'))
            self.remove_param_file.clicked.connect(self.remove_item)
            self.vlayout = QVBoxLayout()
            self.vlayout.addWidget(self.remove_param_file)
            self.vlayout.addStretch(1)
            self.hlayout.addLayout(self.vlayout)
            self.layout.addLayout(self.hlayout)
            self.select_param = QPushButton('Load parameters')
            self.select_param.clicked.connect(self.load_item)
            self.layout.addWidget(self.select_param)
        self.setLayout(self.layout)

    def populate_list(self, group):
        """Populate the list containing all existing groups"""
        counter = 0
        self.item_list = group
        for group_name in group:
            if '.' in group_name:
                group_name = os.path.splitext(os.path.basename(group_name))[0]
            counter += 1
            exec('self.groupItem' + str(counter) + ' = QListWidgetItem()')
            eval('self.groupItem' + str(counter) + '.setText("' + group_name + '")')
            self.group_list.addItem(eval('self.groupItem' + str(counter)))

    def double_click_event(self, clicked_item):
        """
        Get item which was double clicked and call the function to load the group

        Args:
            clicked_item (QModelIndex): Qt index which correspond to the clicked index
        """
        item = self.group_list.item(clicked_item.row())
        self.load_item()

    def remove_item(self):
        """Remove selected item from the list and if it's a parameter file remove it completely"""
        selected_items = self.group_list.selectedItems()
        for item in selected_items:
            item_text = item.text()
            self.group_list.findItems(item_text, Qt.MatchExactly)
            self.group_list.takeItem(self.group_list.row(item))
            if self.parent_widget != 'main':
                for file in self.item_list:
                    if item_text in file:
                        os.remove(file)

    def add_group(self):
        """Add all selected groups to the current session list"""
        items = self.group_list.selectedItems()
        for item in items:
            self.parent.add_group_data(item.text())

    def load_item(self):
        """Load all selected groups in the session list (clear the existing sessions from the list) or load
        the parameters if it's a parameter file"""
        items = self.group_list.selectedItems()
        counter = 0
        for item in items:
            if self.parent_widget == 'main':
                if counter == 0:
                    self.parent.load_group(item.text())
                else:
                    self.parent.add_group_data(item.text())
                counter += 1
            else:
                for yaml in self.item_list:
                    if item.text() in yaml:
                        self.parent.analysis_arguments_handler.load_analysis_argument_from_yaml_file(yaml)
        self.close()

    def showContextMenu(self, pos):
        """
        Display a context menu at the cursor position. Allow the user to add or load the group at the given position
        for session groups or to open parameter file location.

        Args:
            pos (QPoint): Coordinate of the cursor


        """
        self.global_pos = self.mapToGlobal(pos)
        self.context_menu = QMenu()
        if self.parent_widget == 'main':
            self.context_menuLoadAct = QAction("Load group", self, triggered=self.load_item)
            my_path = os.path.abspath(os.path.dirname(__file__))
            self.context_menuLoadAct.setIcon(QtGui.QIcon(os.path.join(my_path, 'cicada/gui/icons/svg/question-mark.svg')))
            self.context_menu.addAction(self.context_menuLoadAct)
            self.context_menuAddAct = QAction("Add group", self, triggered=self.add_group)
            self.context_menuAddAct.setIcon(QtGui.QIcon(os.path.join(my_path, 'cicada/gui/icons/svg/question-mark.svg')))
            self.context_menu.addAction(self.context_menuAddAct)
        else:
            self.context_menuFileAct = QAction("Open file location", self, triggered=self.open_file_in_directory)
            self.context_menu.addAction(self.context_menuFileAct)
        self.context_menu.exec(self.global_pos)

    def open_file_in_directory(self):
        """Open selected YAML parameter file location"""
        items = self.group_list.selectedItems()
        print(self.item_list)
        for item in items:
            for file in self.item_list:
                if item.text() in file:
                    file = os.path.dirname(file)
                    if platform.system() == 'Darwin':
                        subprocess.run(['open', '--', os.path.realpath(file)])
                    elif platform.system() == 'Linux':
                        subprocess.run(['xdg-open', file])
                    elif platform.system() == 'Windows':
                        subprocess.run(['explorer', os.path.realpath(file)])