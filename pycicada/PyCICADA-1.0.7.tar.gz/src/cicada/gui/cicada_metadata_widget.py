from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from qtpy.QtGui import *
import numpy as np
from qtpy import QtCore
from random import randint
import sys
import os
from pynwb import NWBHDF5IO, NWBContainer
from pynwb.file import Subject
from shutil import copyfile
from h5py import File

import collections


class NWBMetaDataFinder:
    """ Find all metadata in NWB file, also contains metadata type and description. """

    def __init__(self, session_data):

        self.session_data = session_data
        self.subject = getattr(self.session_data, 'subject', None)
        self.containers_from_data_file = self.get_containers_in_nwb()

        self.general_metadata_list = ['session_description', 'identifier', 'session_start_time', 'file_create_date',
                                      'timestamps_reference_time', 'experimenter', 'experiment_description',
                                      'session_id', 'institution', 'keywords', 'notes', 'pharmacology', 'protocol',
                                      'related_publications', 'slices', 'source_script', 'source_script_file_name',
                                      'data_collection', 'surgery', 'virus', 'stimulus_notes', 'lab']

        self.subject_metadata_list = ["age", "description", "genotype", "sex", "species", "subject_id",
                                      "weight", "date_of_birth"]

        self.description_metadata = {'session_description': 'a description of the session where this data'
                                                            ' was generated',
                                     'identifier': 'a unique text identifier for the file',
                                     'session_start_time': 'the start date and time of the recording session',
                                     'file_create_date': 'the date and time the file was created and\n'
                                                         'subsequent modifications made',
                                     'timestamps_reference_time': 'date and time corresponding to time zero\n'
                                                                  'of all timestamps; defaults to value of\n'
                                                                  'session_start_time',
                                     'experimenter': 'name of person who performed experiment',
                                     'experiment_description': 'general description of the experiment',
                                     'session_id': 'lab-specific ID for the session',
                                     'institution': 'institution(s) where experiment is performed',
                                     'keywords': 'Terms to search over',
                                     'notes': 'Notes about the experiment',
                                     'pharmacology': 'Description of drugs used, including how and when\n'
                                                     'they were administered. Anesthesia(s), painkiller(s), etc.,\n'
                                                     'plus dosage, concentration, etc.',
                                     'protocol': 'Experimental protocol, if applicable. E.g., include IACUC protocol',
                                     'related_publications': 'Publication information.PMID, DOI, URL, etc.\n'
                                                             'If multiple, concatenate together and describe\n'
                                                             'which is which. such as PMID, DOI, URL, etc',
                                     'slices': 'Description of slices, including information about\n'
                                               'preparation thickness, orientation, temperature and bath solution',
                                     'source_script': 'Script file used to create this NWB file.',
                                     'source_script_file_name': 'Name of the source_script file',
                                     'data_collection': 'Notes about data collection and analysis',
                                     'surgery': 'Narrative description about surgery/surgeries,\n'
                                                'including date(s) and who performed surgery.',
                                     'virus': 'Information about virus(es) used in experiments, including virus ID,\n'
                                              'source, date made, injection location, volume, etc.',
                                     'stimulus_notes': 'Notes about stimuli, such as how and where presented.',
                                     'lab': 'lab where experiment was performed',
                                     'age': 'the age of the subject',
                                     'description': 'a description of the subject',
                                     'genotype': 'the genotype of the subject',
                                     'sex': 'the sex of the subject',
                                     'species': 'the species of the subject',
                                     'subject_id': 'a unique identifier for the subject',
                                     'weight': 'the weight of the subject',
                                     'date_of_birth': 'datetime of date of birth. May be supplied instead of age'}

        self.type_metadata = {'session_description': 'str', 'identifier': 'str', 'session_start_time': 'datetime',
                              'file_create_date': 'list', 'timestamps_reference_time': 'datetime',
                              'experimenter': 'str', 'experiment_description': 'str', 'session_id': 'str',
                              'institution': 'str', 'keywords': 'list', 'notes': 'str', 'pharmacology': 'str',
                              'protocol': 'str', 'related_publications': 'str', 'slices': 'str', 'source_script': 'str',
                              'source_script_file_name': 'str', 'data_collection': 'str', 'surgery': 'str',
                              'virus': 'str', 'stimulus_notes': 'str', 'lab': 'str',
                              'age': 'str', 'description': 'str', 'genotype': 'str', 'sex': 'str', 'species': 'str',
                              'subject_id': 'str', 'weight': 'str', 'date_of_birth': 'datetime'}

    def get_metadata(self, name):
        """

        Args:
            name: name of the metadata to find

        Returns: the metadata associated to the name in the NWB file (general field)

        """
        return getattr(self.session_data, name, None)

    def get_subject_metadata(self, name):
        """

        Args:
            name: name of the metadata to find

        Returns: the metadata associated to the name in the Subject (subject is an attribute to NWB file)

        """
        return getattr(self.subject, name, None)

    def get_metadata_description(self, name):
        """

        Args:
            name: name of the metadata to find

        Returns: the description associated to the name of the metadata in description_metadata list

        """
        return self.description_metadata[name]

    def get_metadata_type(self, name):
        """

        Args:
            name: name of the metadata to find

        Returns: the type (str, datetime, int ...) associated to the name of the metadata in type_metadata list

        """
        return self.type_metadata[name]

    def get_containers_in_nwb(self):
        """
        Recursive research of all containers (with 'children' field)
        Containers are all NWB fields which contains data

        Returns: a dictionary with containers name as key and containers as value

        """

        containers_from_data_file = dict()

        # Recursive function
        def check_containers(container):

            children = getattr(container, 'children', None)
            for child in children:
                if isinstance(child, NWBContainer) and not isinstance(child, Subject):
                    # Subject is a NWBContainer but is already got
                    containers_from_data_file[child.name] = child
                    check_containers(child)

        check_containers(self.session_data)

        return containers_from_data_file


# Metadata formatting for GUI
class CicadaMetaDataContainer:
    """ Metadata formatting (input and output) with the GUI """

    def __init__(self, session_data):

        self.session_data = session_data

        self.metadata_finder_wrapper = None
        self.initiate_metadata_finder_wrapper()

        self.session_data = self.metadata_finder_wrapper.session_data

        self.metadata_handler = MetaDataHandler(cicada_metadata_container=self)

        self.general_metadata_list = self.metadata_finder_wrapper.general_metadata_list
        self.subject_metadata_list = self.metadata_finder_wrapper.subject_metadata_list

        self.set_metadata_for_gui()
        self.set_containers_for_gui()

    def initiate_metadata_finder_wrapper(self):
        """
        set the appropriate class to find all metadata informations depending of data_file type ("nwb", ...)

        """
        # if self.data_format == "nwb":
        # TODO: remove all that
        self.metadata_finder_wrapper = NWBMetaDataFinder(self.session_data)

    def add_metadata_group_for_gui(self, **kwargs):
        """
        Transfer a metadata group to MetadataHandler in order to be add to the GUI

        Args:
            **kwargs: all informations and metadata about a group of metadata

        """

        self.metadata_handler.add_group(**kwargs)

    def set_metadata_for_gui(self):
        """
        Set all metadata with their information as dictionaries (name, value_type, value and description) in a group
        Send the group to add_metadata_group_for_gui function for the GUI

        """

        # All metadata with names, value_types, value and description !

        general_metadata = dict()
        general_metadata["group_name"] = 'general_metadata'
        general_metadata["widget_type"] = 'QTable'
        general_metadata["description"] = 'metadata about session, laboratory ...'
        general_metadata["metadata_in_group"] = []

        for metadata in self.general_metadata_list:

            general_metadata_for_gui = {"metadata_name": metadata,
                                        "value_type": self.metadata_finder_wrapper.get_metadata_type(metadata),
                                        "value": self.metadata_finder_wrapper.get_metadata(metadata),
                                        "description": self.metadata_finder_wrapper.get_metadata_description(metadata)}
            general_metadata["metadata_in_group"].append(general_metadata_for_gui)

        self.add_metadata_group_for_gui(**general_metadata)

        # Subject metadata part

        subject_metadata = dict()
        subject_metadata["group_name"] = 'metadata_from_subject'
        subject_metadata["widget_type"] = 'QTable'
        subject_metadata["description"] = 'metadata about the subject'
        subject_metadata["metadata_in_group"] = []

        for metadata in self.subject_metadata_list:
            subject_metadata_for_gui = {"metadata_name": metadata,
                                        "value_type": self.metadata_finder_wrapper.get_metadata_type(metadata),
                                        "value": self.metadata_finder_wrapper.get_subject_metadata(metadata),
                                        "description": self.metadata_finder_wrapper.get_metadata_description(metadata)}
            subject_metadata["metadata_in_group"].append(subject_metadata_for_gui)

        self.add_metadata_group_for_gui(**subject_metadata)

        # TODO : for each of those following metadata, show them or not ? And how ?
        '''
        - epochs_metadata  # epoch object
        - trials_metadata  # table
        - invalid_times_metadata  # table
        - units_metadata  # table
        - electrodes_metadata  # table
        - sweep_table_metadata  # table
        - neurodata_type_metadata  # str
        - modified_metadata  # str
        - container_source_metadata  # str
        - lab_meta_data_metadata  # container
        - epoch_tags_metadata  # set
        '''

    def set_containers_for_gui(self):
        """
        For all containers found, if they have metadata, create a group with their metadata (one for each container)
        Create a group for all containers without metadata


        """

        # TODO : add information about dimension of data, ...

        containers_from_data_file = self.metadata_finder_wrapper.containers_from_data_file

        other_containers = dict()
        other_containers['group_name'] = 'other containers'
        other_containers['widget_type'] = 'QTable'
        other_containers['description'] = 'other containers'
        other_containers['metadata_in_group'] = []

        for container in containers_from_data_file.values():
            container_metadata = dict()
            container_metadata['group_name'] = container.name
            container_metadata['widget_type'] = 'QTable'
            container_metadata['description'] = container.name + "     (type : " \
                                                               + str(type(container)).split("'")[1] + ")"
            container_metadata['metadata_in_group'] = []

            # Try to get all metadata for this container
            for field in container.fields:
                field_class = container.fields.get(field)  # 'field' is a string, corresponds to a 'fields' attribute
                if isinstance(field_class, (str, float, int)):
                    container_metadata_dict = {'metadata_name': str(field), 'value_type':
                                               str(type(field_class)).split("'")[1], 'value': field_class,
                                               'description': str(field) + ' of ' + container.name}
                    container_metadata['metadata_in_group'].append(container_metadata_dict)

            if len(container_metadata['metadata_in_group']) > 0:
                self.add_metadata_group_for_gui(**container_metadata)

            # When there isn't any metadata, put them in a group with all other containers
            else:
                container_to_add = {'metadata_name': str(container.name), 'value_type':
                                    str(type(container)).split("'")[1],
                                    'value': None, 'description': getattr(container, 'description', None)}
                other_containers['metadata_in_group'].append(container_to_add)

        if len(other_containers['metadata_in_group']) > 0:
            self.add_metadata_group_for_gui(**other_containers)

    def print_metadata(self, all_metadata):
        """
        Show all metadata in a txt file in the same directory as the NWB file

        Args:
            all_metadata: dictionary with metadata name as key and group_name and value as value

        """
        parent_dir, file_name = os.path.split(self.data_path)
        metadata_file_path = os.path.join(parent_dir, "all_metadata_from_" + str(file_name).split('.')[0] + '.txt')

        with open(metadata_file_path, "w") as metadata_file:
            group_name = ""
            metadata_file.write("\n======================== " + "all metadata from " +
                                str(file_name).split('.')[0] + " ========================\n\n")
            for metadata_name, metadata_informations in all_metadata.items():
                if metadata_informations["group_name"] != group_name:
                    if group_name != "":
                        metadata_file.write("\n")
                    group_name = metadata_informations["group_name"]
                    metadata_file.write("\n====== " + group_name + " ======\n")
                metadata_file.write("\n - " + metadata_name + " : " + metadata_informations["value"])
            metadata_file.write("\n")

    def save_changes_wrapper(self, general_metadata, subject_metadata):
        """
        Save metadata depending of the changes in the GUI and create a copy with the old data_file
        Set the appropriate save function depending of the data_file format.

        Args:
            general_metadata: dictionary with general metadata name as key and its value as value
            subject_metadata: dictionary with subject metadata name as key and its value as value

        """
        # if self.data_format == 'nwb':
        self.nwb_save_changes(general_metadata, subject_metadata)

    def nwb_save_changes(self, general_metadata, subject_metadata):
        """
        Save function for NWB file

        """
        SaveModifiedNWB(self.data_path, general_metadata=general_metadata, subject_metadata=subject_metadata)


class SaveModifiedNWB:
    """ Save all changes in metadata fields (of the NWB file) with the information given by the user on the GUI """

    # TODO : make it work for other data type, not only str (see metadata_handler.save_changes)
    # it doesn't work with datetime

    def __init__(self, nwb_path, general_metadata=None, subject_metadata=None):
        self.nwb_path = nwb_path

        # New path to save the modified NWB
        parent_dir, file_name = os.path.split(self.nwb_path)
        self.old_path = os.path.join(parent_dir, "old_" + file_name)
        if not os.path.exists(self.old_path):
            copyfile(self.nwb_path, self.old_path)

        self.nwb_file = File(self.nwb_path, 'r+')
        self.general_metadata = general_metadata  # dictionnary with all general metadata fields and values
        self.subject_metadata = subject_metadata  # dictionnary with all subject metadata fields and values

        if general_metadata is not None:
            self.modify_general_metadata()
        if subject_metadata is not None:
            self.modify_subject_metadata()

        self.write_nwb()

    def modify_general_metadata(self):
        """
        # Add or modify general metadata fields in the NWB file

        """

        for metadata_field, metadata_value in self.general_metadata.items():
            original_metadata = getattr(self.nwb_file, metadata_field, None)
            if metadata_value != original_metadata:
                try:
                    del self.nwb_file['general'][metadata_field]  # if exists already
                except KeyError:
                    # can't del because doesn't exists
                    pass
                self.nwb_file['general'].create_dataset(name=metadata_field, data=metadata_value)

    def modify_subject_metadata(self):
        """
        # Add or modify subject metadata fields in the NWB file

        """
        try:
            subject = self.nwb_file['general']['subject']
        except KeyError:
            pass
        else:
            for metadata_field, metadata_value in self.subject_metadata.items():
                original_metadata = getattr(subject, metadata_field, None)
                if metadata_value != original_metadata:
                    try:
                        del subject[metadata_field]  # if exists already
                    except KeyError:
                        # can't del because doesn't exists
                        pass
                    if type(metadata_value) is str:
                        subject.create_dataset(name=metadata_field, data=metadata_value)

    def write_nwb(self):
        """
        Close and try to read the modified NWB file to check if it is corrupted or not.

        """

        # TODO: delete modified file and rename old file if can't read

        self.nwb_file.close()

        with NWBHDF5IO(self.nwb_path, 'r') as io_test:
            io_test.read()


class MetaDataHandler:
    """ Associate metadata groups with widgets """

    def __init__(self, cicada_metadata_container):
        self.groups_dict = dict()
        self.cicada_metadata_container = cicada_metadata_container

    def add_group(self, **kwargs):
        """
        Add a given group to a dictionary which contains all groups to show to the GUI (group name as key).

        Args:
            **kwargs: all information about a group of metadata

        """
        metadata_group = MetaDataGroup(**kwargs)
        self.groups_dict[getattr(metadata_group, 'group_name')] = metadata_group

    def get_all_metadata_groups(self):
        """

        Returns: A list with all metadata groups

        """

        all_metadata_groups = list(self.groups_dict.values())
        return all_metadata_groups

    def get_gui_widgets(self):
        """
        For each metadata group, create the corresponding Widget on the GUI
        and add the widget in a list with all widgets

        Returns: a list with all widgets created

        """

        gui_widgets = []
        all_metadata_groups = self.get_all_metadata_groups()
        for metadata_group in all_metadata_groups:
            gui_widget = metadata_group.get_gui_widget()
            if gui_widget:
                gui_widgets.append(gui_widget)
        return gui_widgets

    def print_metadata(self):
        """
        Metadata formatting for print
        Call print_metadata from CicadaMetadataContainer to create a txt file with all metadata

        """
        all_metadata_to_print = collections.OrderedDict()
        for metadata_group_name, metadata_group in self.groups_dict.items():
            for metadata_name, metadata in metadata_group.metadata_dict.items():
                value = metadata_group.get_metadata_value_in_widget(metadata)
                all_metadata_to_print[metadata_name] = {'group_name': metadata_group_name, 'value': value}
        self.cicada_metadata_container.print_metadata(all_metadata_to_print)

    def save_changes(self):
        """
        Metadata formatting for save
        Call save_changes_wrapper from CicadaMetadataContainer to save the modified data file

        """
        general_metadata_values = collections.OrderedDict()
        subject_metadata_values = collections.OrderedDict()
        for metadata_group_name, metadata_group in self.groups_dict.items():
            for metadata_name, metadata in metadata_group.metadata_dict.items():
                value = metadata_group.get_metadata_value_in_widget(metadata)
                if value == 'None':
                    value = None

                if metadata_group_name == 'general_metadata' and value is not None:
                    if metadata.value_type == 'str':
                        general_metadata_values[metadata_name] = value

                elif metadata_group_name == 'metadata_from_subject'and value is not None:
                    if metadata.value_type == 'str':
                        subject_metadata_values[metadata_name] = value

        self.cicada_metadata_container.save_changes_wrapper(general_metadata_values, subject_metadata_values)


class MetaData:
    """ Structure of one metadata """

    def __init__(self, idx_position, **kwargs):
        """

        Args:
            idx_position: position of metadata in the Table Widget (QTableWidget)
            **kwargs: - metadata_name
                      - value_type
                      - value
                      - description
        """

        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)

        self.position_in_widget = idx_position

        self.final_value = None

    def set_metadata_value(self, value):
        """
        Set the value of metadata given by user in the GUI for save or print

        """
        self.final_value = value

    def get_metadata_value(self):
        """
        Just get the value of metadata

        """
        return getattr(self, "value", None)

    def get_metadata_name(self):
        """
        Just get the name of metadata

        """
        return getattr(self, "name", None)


class MetaDataGroup:
    """ Structure of a group of metadata """

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:  - group_name
                       - widget_type
                       - description
                       - metadata_in_group
        """

        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)

        self.widget = None
        self.metadata_dict = dict()
        self.idx_position = 0  # Counter, add 1 each time a metadata is add to the group to define its position inside

        if getattr(self, "metadata_in_group", None) is not None:
            for raw_metadata in getattr(self, "metadata_in_group", None):
                self.add_metadata(**raw_metadata)
        else:
            print("No metadata found !")

    def add_metadata(self, **kwargs):
        """
        Convert metadata from CicadaMetadataContainer in MetaData class and add it to metadata_dict

        Args:
            **kwargs: all informations about a metadata

        """
        metadata_to_add = MetaData(self.idx_position, **kwargs)
        self.metadata_dict[getattr(metadata_to_add, 'metadata_name')] = metadata_to_add
        self.idx_position += 1

    def get_gui_widget(self):
        """
        Get a Widget corresponding to the metadata group to show it in the GUI

        Returns: the corresponding widget (sent to MetaDataHandler)

        """

        if getattr(self, "widget_type", None) == "QTable":
            self.widget = TableWidget(metadata_group=self)
            return self.widget

    def get_metadata_value_in_widget(self, metadata):
        """

        Args:
            metadata: metadata to find in the Widget (on the GUI)

        Returns: value of the metadata found in the Widget

        """
        if self.widget is None:
            return None
        if getattr(self, "widget_type", None) == "QTable":
            return self.widget.get_value(metadata.position_in_widget)
        else:
            return self.widget.get_value()

    def get_group_description(self):
        """
        Just return description of the group

        """
        return getattr(self, "description", None)


class MetaDataWidget(QWidget):
    """ Main Widget to show all metadata """

    def __init__(self, session_data, parent=None):
        QWidget.__init__(self, parent=parent)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.setWindowIcon(QIcon(os.path.join(my_path, 'icons/svg/cicada_open_focus.svg')))

        self.setWindowTitle("Show info")

        # making sure the window is not bigger than the dimension of the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        width_window = min(1200, screen_geometry.width())
        height_window = min(650, screen_geometry.height())
        self.resize(width_window, height_window)

        self.cicada_metadata_container = CicadaMetaDataContainer(session_data)

        self.metadata_handler = None

        self.special_background_on = False
        self.current_style_sheet_background = ".QWidget{background-image:url(\"\"); background-position: center;}"

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

        # Add the buttons
        self.button_layout = QHBoxLayout()

        self.print_button = QPushButton("Print", self)
        self.print_button.clicked.connect(self.print_metadata)
        self.button_layout.addWidget(self.print_button)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_changes)
        self.button_layout.addWidget(self.save_button)

        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

        # Create all widgets
        self.create_widgets(self.cicada_metadata_container)
        self.show()

    def tabula_rasa(self):
        """
        Erase the widgets and make an empty section

        """
        # clearing the widget to update it
        self.scroll_area_widget_contents = QWidget()
        self.scrollArea.setWidget(self.scroll_area_widget_contents)
        self.layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_widget_contents.setStyleSheet(self.current_style_sheet_background)

    def create_widgets(self, cicada_metadata_container):
        """
        Get all widgets and show them

        """

        self.cicada_metadata_container = cicada_metadata_container

        # clearing the widget to update it
        self.tabula_rasa()
        # ==============================

        self.metadata_handler = self.cicada_metadata_container.metadata_handler

        # list of instances of MetadataArgument
        gui_widgets = self.metadata_handler.get_gui_widgets()

        for gui_widget in gui_widgets:
            # print(f"gui_widget {gui_widget}")
            self.layout.addWidget(gui_widget)
            # See to check if gui_widget is an instance of QFrame to round the border only
            # for QFrame instances
            gui_widget.setStyleSheet(
                "background-color:transparent; border-radius: 20px;")

        self.layout.addStretch(1)

    def save_changes(self):
        """
        Connect "save" button to function save_changes of MetaDataHandler

        """
        if self.metadata_handler is None:
            return
        self.metadata_handler.save_changes()

    def print_metadata(self):
        """
        Connect "print" button to function print_metadata of MetaDataHandler

        """
        if self.metadata_handler is None:
            return
        self.metadata_handler.print_metadata()


class TableWidget(QFrame):

    def __init__(self, metadata_group, parent=None):
        QWidget.__init__(self, parent=parent)

        self.metadata_group = metadata_group
        self.metadata_dict = self.metadata_group.metadata_dict

        self.table = QTableWidget()

        nb_rows = len(self.metadata_dict)

        show_description = False
        for metadata in self.metadata_dict.values():
            if metadata.description is not None:
                show_description = True

        if show_description:
            nb_columns = 4
        else:
            nb_columns = 3

        self.table.setRowCount(nb_rows)
        self.table.setColumnCount(nb_columns)

        self.table.setHorizontalHeaderLabels(["metadata name", "value type", "value", "description"])

        for metadata_to_add in self.metadata_dict.values():
            position = metadata_to_add.position_in_widget
            self.table.setItem(position, 0, QTableWidgetItem(metadata_to_add.metadata_name))
            self.table.setItem(position, 1, QTableWidgetItem(metadata_to_add.value_type))
            self.table.setItem(position, 2, QTableWidgetItem(str(metadata_to_add.value)))
            if show_description:
                self.table.setItem(position, 3, QTableWidgetItem(metadata_to_add.description))
            self.table.move(0, 0)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        # Uncomment for use alone

        # self.table.setFixedSize(
        #     self.table.horizontalHeader().length() + self.table.verticalHeader().width() + 2,
        #     self.table.verticalHeader().length() + self.table.horizontalHeader().height() + 2)

        # Change size in the css file
        if nb_rows <= 1:
            self.table.setProperty("set_height", "tiny")
        elif nb_rows <= 3:
            self.table.setProperty("set_height", "small")
        elif nb_rows <= 8:
            self.table.setProperty("set_height", "medium")
        elif nb_rows <= 12:
            self.table.setProperty("set_height", "big")
        else:
            self.table.setProperty("set_height", "gigantic")

        v_box = QVBoxLayout()
        description = self.metadata_group.get_group_description()

        if description:
            q_label = QLabel(description)
            q_label.setAlignment(Qt.AlignCenter)
            q_label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            q_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            v_box.addWidget(q_label)

        h_box = QHBoxLayout()
        h_box.addWidget(self.table)
        v_box.addLayout(h_box)

        self.setLayout(v_box)

    def get_value(self, metadata_position):
        return self.table.item(metadata_position, 2).text()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Change the path !
    # ============================================
    test_file_path = 'C:/Users/Public/nwb_files/p6_18_02_07_a002.nwb'
    # ============================================

    widget = MetaDataWidget(test_file_path, 'nwb')
    sys.exit(app.exec_())
