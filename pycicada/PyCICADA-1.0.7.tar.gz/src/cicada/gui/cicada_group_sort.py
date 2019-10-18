from qtpy.QtWidgets import *
from qtpy import QtCore, QtGui
from cicada.gui.cicada_metadata_widget import MetaDataWidget
from qtpy.QtCore import Qt
import yaml
import datetime
from random import randint
import os
from time import sleep


class SessionsListWidget(QListWidget):

    def __init__(self, session_widget, config_handler):
        QListWidget.__init__(self)
        self.config_handler = config_handler
        self.special_background_on = False
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # TODO: fixed menu to show subject info
        # self.customContextMenuRequested.connect(self.showContextMenu)
        self.session_widget = session_widget
        self.arguments_section_widget = None

        if config_handler.main_window_bg_pictures_displayed_by_default:
            self.set_random_background_picture()

    def set_random_background_picture(self):
        """Set a random background picture from the repertory set in the config file"""
        pic_path = self.config_handler.get_random_main_window_bg_picture(widget_id="sessions")
        if pic_path is None:
            return
        self.setStyleSheet(
            f"background-image:url(\"{pic_path}\"); "
            f"background-position: center top; "
            f"background-repeat:repeat-xy;") # no-repeat
        self.special_background_on = True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_P:
            if self.special_background_on:
                self.setStyleSheet(
                    "background-image:url(\"\"); background-position: center;")
                self.special_background_on = False
            else:
               self.set_random_background_picture()
        elif event.key() == QtCore.Qt.Key_Return:
            data_to_analyse = self.session_widget.get_data_to_analyse()
            self.session_widget.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def showContextMenu(self, pos):
        """
        Display a context menu at the cursor position. Allow the user to see informations about the selected sessions.

        Args:
            pos (QPoint): Coordinate of the cursor

        """
        self.global_pos = self.mapToGlobal(pos)
        self.context_menu = QMenu()
        self.context_menuAct = QAction("Show info", self, triggered=self.show_info)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.context_menuAct.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/question-mark.svg')))
        self.context_menu.addAction(self.context_menuAct)
        self.context_menu.exec(self.global_pos)

    def show_info(self):
        """Open the metadata widget associated to the selected items"""
        item_list = self.selectedItems()
        for item in item_list:
            meta_widget = MetaDataWidget(self.session_widget.cicada_main_window.data_dict[item.text()])
            setattr(item.text() + "_metadata", meta_widget)
            # exec('self.' + item.text() + '_metadata = '
            #                              'MetaDataWidget(self.session_widget.parent.nwb_path_list.get(item.text()),'
            #                              ' "nwb")')
            self.session_widget.parent.object_created.append(getattr(item.text() + '_metadata'))


class SessionsWidget(QWidget):
    """Class containing the widget holding the list of loaded sessions"""
    def __init__(self, config_handler, cicada_main_window, to_analysis_button=None):

        super().__init__()
        self.cicada_main_window = cicada_main_window
        # deal with the configuration
        self.config_handler = config_handler

        # setting attribute used in methods
        self.sortButton = None
        self.groupButton = None

        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.check_menu()
        self.sort_menu()
        self.group_menu()
        self.textLabel = QLabel()
        self.textLabel.setTextInteractionFlags(Qt.NoTextInteraction)
        self.hlayout.addWidget(self.textLabel)
        self.more_menu()

        self.q_list = SessionsListWidget(session_widget=self, config_handler=self.config_handler)
        self.q_list.doubleClicked.connect(self.double_click_event)
        self.q_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # connecting the button that will fill the analysis tree
        # TODO: see to deactivate until the tree is loaded
        if to_analysis_button:
            to_analysis_button.clicked.connect(self.send_data_to_analysis_tree)

        self.layout.addWidget(self.q_list)
        self.items = []
        if self.cicada_main_window.grouped:
            self.form_group(self.cicada_main_window.grouped_labels)
        elif self.cicada_main_window.sorted:
            self.populate(self.cicada_main_window.sorted_labels)
        else:
            self.populate(self.cicada_main_window.labels)
        self.q_list.itemSelectionChanged.connect(self.on_change)
        self.hlayout2.addLayout(self.layout)
        self.setLayout(self.hlayout2)
        self.analysis_tree = None

    def double_click_event(self, clicked_item):
        """
        Handle double click on item in QListWidget.
        Check or uncheck an item or a group on double click.

        Args:
            clicked_item: Double clicked item

        """
        flags = clicked_item.flags()
        if flags & 1:  # Item is selectable, meaning it is a session
            if self.q_list.item(clicked_item.row()).checkState():
                self.q_list.item(clicked_item.row()).setCheckState(QtCore.Qt.Unchecked)
            else:
                self.q_list.item(clicked_item.row()).setCheckState(QtCore.Qt.Checked)
        else:  # Item is not selectable, meaning it is a separator
            row_index = clicked_item.row() + 1
            item_is_selectable = True
            while item_is_selectable:
                if self.q_list.item(row_index).checkState():
                    self.q_list.item(row_index).setCheckState(QtCore.Qt.Unchecked)
                else:
                    self.q_list.item(row_index).setCheckState(QtCore.Qt.Checked)
                try:
                    if not self.q_list.item(row_index + 1).flags() & 1:
                        item_is_selectable = False
                    row_index += 1
                except AttributeError:
                    item_is_selectable = False

    def sort_menu(self):
        """Create sort menu"""

        self.sortButton = QToolButton()
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.sortButton.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/sort.svg')))
        self.sortButton.setPopupMode(QToolButton.InstantPopup)
        self.sortButton.setMenu(self.cicada_main_window.sortMenu)
        # TODO: See to fix sortButton
        # self.hlayout.addWidget(self.sortButton)

    def group_menu(self):
        """Create group menu"""

        self.groupButton = QToolButton()
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.groupButton.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/group.svg')))
        self.groupButton.setPopupMode(QToolButton.InstantPopup)
        self.groupButton.setMenu(self.cicada_main_window.groupMenu)
        # TODO: Use dict to be able to do group of group and use button to sort to change the sorting order
        self.hlayout.addWidget(self.groupButton)

    def more_menu(self):
        """Create more menu"""

        self.otherActionsButton = QToolButton()
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.otherActionsButton.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/more2.svg')))
        self.otherActionsButton.setStyleSheet('border: none;')
        self.otherActionsButton.setPopupMode(QToolButton.InstantPopup)
        self.otherActionsMenu = QMenu()
        self.otherActionsButton.setMenu(self.otherActionsMenu)
        self.removeAct = QAction('Remove selected', shortcut='Delete')
        self.removeAct.triggered.connect(self.remove_data)
        self.createGroupAct = QAction("Create groups")
        self.createGroupAct.triggered.connect(self.save_group)
        self.otherActionsMenu.addMenu(self.cicada_main_window.selectGroupMenu)
        self.otherActionsMenu.addAction(self.cicada_main_window.seeAllGroupAct)
        self.otherActionsMenu.addAction(self.removeAct)
        self.otherActionsMenu.addAction(self.createGroupAct)
        self.hlayout.addWidget(self.otherActionsButton)
        self.layout.addLayout(self.hlayout)
        self.hlayout2 = QHBoxLayout()

    def check_menu(self):
        """Create menu to check or uncheck all/none/selected items"""

        self.selectButton = QToolButton()
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.selectButton.setIcon(QtGui.QIcon(os.path.join(my_path, 'icons/svg/checkbox.svg')))
        self.selectButton.setStyleSheet('border: none;')
        self.selectButton.setPopupMode(QToolButton.InstantPopup)
        self.selectMenu = QMenu()
        self.selectButton.setMenu(self.selectMenu)
        self.selectAllAct = QAction('All')
        self.selectAllAct.triggered.connect(self.check_all)
        self.unselectAllAct = QAction('None')
        self.unselectAllAct.triggered.connect(self.uncheck_all)
        self.unselectSelectedAct = QAction('Uncheck selected')
        self.unselectSelectedAct.triggered.connect(self.uncheck_selected)
        self.selectSelectedAct = QAction('Check selected')
        self.selectSelectedAct.triggered.connect(self.check_selected)
        self.selectMenu.addAction(self.selectAllAct)
        self.selectMenu.addAction(self.unselectAllAct)
        self.selectMenu.addAction(self.unselectSelectedAct)
        self.selectMenu.addAction(self.selectSelectedAct)
        self.hlayout.addWidget(self.selectButton)

    def remove_data(self):
        """Remove selected item(s) from QListWidget"""

        selected_items = self.q_list.selectedItems()
        for item in selected_items:
            item = item.text()
            for label in self.cicada_main_window.labels:
                if item in label:
                    self.cicada_main_window.labels.remove(label)
                    try:
                        del self.cicada_main_window.nwb_path_list[item]
                    except KeyError:
                        continue
                    list_item_to_remove = self.q_list.findItems(item, Qt.MatchExactly)
                    try:
                        for item_to_remove in list_item_to_remove:
                            self.q_list.takeItem(self.q_list.row(item_to_remove))
                    except IndexError:
                        pass
        if not self.cicada_main_window.labels:
            self.cicada_main_window.groupMenu.setEnabled(False)
            self.cicada_main_window.sortMenu.setEnabled(False)
        self.cicada_main_window.load_group_from_config()

    def uncheck_all(self):
        """Uncheck all items"""

        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def uncheck_selected(self):
        """Uncheck selected item(s)"""

        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Unchecked)

    def check_all(self):
        """Check all items"""

        for idx in range(self.q_list.count()):
            self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)

    def check_selected(self):
        """Check selected item(s)"""

        for idx in range(self.q_list.count()):
            for item in self.items:
                if self.q_list.item(idx).text() == item:
                    self.q_list.item(idx).setCheckState(QtCore.Qt.Checked)

    def on_change(self):
        """Handle change in selection"""

        self.items = [item.text() for item in self.q_list.selectedItems()]

    def get_items(self):
        """
        Returns list of items
        Returns:
            list of items

        """

        return [item for item in self.items]

    def get_data_to_analyse(self):
        """Get data to analyse"""

        checked_items = []
        for index in range(self.q_list.count()):
            if self.q_list.item(index).checkState() == 2:
                checked_items.append(self.q_list.item(index).text())
        return [data for key, data in self.cicada_main_window.data_dict.items() if key in checked_items]

    def send_data_to_analysis_tree(self):
        """Send data to the analysis tree function"""
        data_to_analyse = self.get_data_to_analyse()

        #TODO : try to understand why it is not working ?
        # self.analysis_tree.invalidate_all_items()
        # sleep(0.5)

        # the data in data_to_analyse list, are instances of CicadaAnalysisNwbWrapper
        if data_to_analyse:
            self.analysis_tree.set_data(data_to_analyse=data_to_analyse, data_format="nwb")

    def select_item(self, item):
        """
        Set an item as checked

        Args:
            item (str): Session idenfitifer

        """
        items_found = self.q_list.findItems(item, Qt.MatchExactly)
        try:
            for item_found in items_found:
                item_found.setCheckState(QtCore.Qt.Checked)
        except IndexError:
            pass

    def populate(self, labels, method='clear'):
        """
        Populate the QListWidget with sessions labels

        Args:
            labels (list): Sessions identifiers
            method (str): In case we don't want to clear the QListWidget

        """
        if method == 'clear':
            self.q_list.clear()
        if method == 'add':
            for label in labels:
                if label not in self.cicada_main_window.labels:
                    self.cicada_main_window.labels.append(label)
            self.cicada_main_window.load_group_from_config()
        items = []
        if self.q_list.count() != 0:
            for file in labels:
                for index in range(self.q_list.count()):
                    items.append(self.q_list.item(index).text())
                if file not in items:
                    item = QListWidgetItem()
                    item.setCheckState(QtCore.Qt.Checked)
                    item.setText(str(file))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                    self.q_list.addItem(item)
        else:
            for file in labels:
                item = QListWidgetItem()
                item.setCheckState(QtCore.Qt.Checked)
                item.setText(str(file))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                self.q_list.addItem(item)

    # def form_group(self, labels, param=["-"]):
    #     """
    #     Form group of items and display their group name
    #
    #     Args:
    #         labels (list): Session identifiers
    #         param (str): Parameter used to create the groups
    #
    #     """
    #
    #     self.q_list.clear()
    #     while len(param) < len(labels):
    #         param.append("-")
    #     for group in labels:
    #         item = QListWidgetItem()  # delimiter
    #         if param[0] is None:
    #             param[0] = "None"
    #         separator = '--------------------------------------------------------------'
    #         separator = separator[len(str(param[0])):]
    #         middle_separator = len(separator) // 2
    #         item.setText(separator[middle_separator:] + str(param.pop(0)) + separator[middle_separator:])
    #         item.setFlags(QtCore.Qt.ItemIsEnabled)
    #         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)  # item should not be selectable
    #         self.q_list.addItem(item)
    #         for file in group:
    #             item = QListWidgetItem()
    #             item.setCheckState(QtCore.Qt.Unchecked)
    #             item.setText(str(file))
    #             item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
    #             self.q_list.addItem(item)
    def _compare_keys(x, y):
        try:
            x = int(x)
        except ValueError:
            xint = False
        else:
            xint = True
        try:
            y = int(y)
        except ValueError:
            if xint:
                return -1
            return cmp(x.lower(), y.lower())
            # or cmp(x, y) if you want case sensitivity.
        else:
            if xint:
                return cmp(x, y)
            return 1

    def form_group(self, dict_group):
        """
        Form group of items and display their group name

        Args:
            dict_group (dict): key is an instance of cicada.preprocessing.utils.ComparableItem representing
            the group name, and value is an instance of CicadaAnalysisWrapper

        """

        self.q_list.clear()
        # for group_name in sorted(dict_group):
        #     group_members = dict_group[group_name]
        for group_name, group_members in dict_group.items():
            item = QListWidgetItem()  # delimiter
            group_name = str(group_name)
            separator = '--------------------------------------------------------------'
            separator = separator[len(group_name):]
            middle_separator = len(separator) // 2
            item.setText(separator[middle_separator:] + group_name + separator[middle_separator:])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)  # item should not be selectable
            self.q_list.addItem(item)
            # member is an instance of CicadaAnalysisWrapper
            for member in group_members:
                item = QListWidgetItem()
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setText(member.identifier)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                self.q_list.addItem(item)

    def update_text_filter(self, param_group=''):
        """
        Update the QLabel to display the sort/group state

        Args:
            param_group: Parameter used to form group

        """
        if self.cicada_main_window.grouped:
            self.textLabel.setText(f'Grouped by : {param_group}')
        elif self.cicada_main_window.sorted:
            param_list = ', '.join(self.cicada_main_window.param_list)
            self.textLabel.setText(f'Sorted by : {param_list}')
        else:
            self.textLabel.setText('')

    def save_group(self):
        """Save sessions in a group"""

        self.nameBox = QDialog(self)
        self.nameBoxLayout = QVBoxLayout(self.nameBox)
        self.nameBox.setWindowTitle("Save your group as")
        self.save_name = QLineEdit(self.nameBox)
        self.save_name.setText("Group_" + str(datetime.date.today()))
        self.saveButton = QPushButton('Save as')
        self.nameBoxLayout.addWidget(self.save_name)
        self.nameBoxLayout.addWidget(self.saveButton)
        self.nameBox.show()
        self.saveButton.clicked.connect(self.save_group_names)
        self.saveButton.clicked.connect(self.nameBox.close)

    def save_group_names(self):
        """Save group in a YAML with a certain name"""
        my_path = os.path.abspath(os.path.dirname(__file__))
        group_yaml_file = os.path.join(my_path, "../config/group.yaml")
        name = self.save_name.text()
        group_to_save = []
        checked_items = []
        for index in range(self.q_list.count()):
            if self.q_list.item(index).checkState() == 2:
                checked_items.append(self.q_list.item(index).text())
        for item in checked_items:
            for path in self.cicada_main_window.nwb_path_list.values():
                if path.endswith(item + ".nwb"):
                    group_to_save.append(path)
        if self.cicada_main_window.all_groups:
            self.cicada_main_window.all_groups.update({name: group_to_save})
        else:
            self.cicada_main_window.all_groups = {name: group_to_save}
        with open(os.path.realpath(group_yaml_file), 'w+') as stream:
            yaml.dump(self.cicada_main_window.all_groups, stream, default_flow_style=False)
        self.cicada_main_window.load_group_from_config()
