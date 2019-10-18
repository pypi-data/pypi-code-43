from abc import ABC, abstractmethod, abstractproperty
from cicada.analysis.cicada_analysis_arguments_handler import AnalysisArgumentsHandler
from cicada.analysis.cicada_analysis_nwb_wrapper import CicadaAnalysisNwbWrapper
from cicada.preprocessing.utils import class_name_to_file_name, path_leaf
import importlib
import PyQt5.QtCore as Core
from qtpy.QtCore import QThread
from datetime import datetime
import sys
import os
from time import time
import numpy as np

class CicadaAnalysis(ABC):
    """
    An abstract class that should be inherit in order to create a specific analyse

    """
    def __init__(self, name, short_description, family_id=None, long_description=None,
                 data_to_analyse=None, data_format=None, config_handler=None, gui=True):
        """

        Args:
            name:
            short_description: short string that describe what the analysis is about
             used to be displayed in the GUI among other things
            family_id:  family_id indicated to which family of analysis this class belongs. If None, then
             the analysis is a family in its own.
            long_description:
            data_to_analyse:
            data_format:
            config_handler: Instance of ConfigHandler to have access to configuration
        """

        super().__init__()
        # TODO: when the exploratory GUI will be built, think about passing in argument some sort of connector
        #  to the GUI in order to communicate with it and get the results displayed if needed
        self.short_description = short_description
        self.long_description = long_description
        self.progress_bar_overview = None
        self.progress_bar_analysis = None
        self.family_id = family_id
        self.name = name
        self.gui = gui
        self.yaml_name = ''
        self.current_order_index = 0
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format
        self.config_handler = config_handler
        # attribute that will be used to display the reason why the analysis is not possible with the given
        # data passed to it
        self.invalid_data_help = None
        # Initialized in run_analysis, can be used to save in the log file the run time.
        self.analysis_start_time = 0
        self.analysis_arguments_handler = AnalysisArgumentsHandler(cicada_analysis=self)

        # path of the dir where the results will be saved
        self._results_path = None

        if self._data_to_analyse:
            self.set_arguments_for_gui()

    # @abstractproperty
    # def data_to_analyse(self):
    #     pass
    #
    # @abstractproperty
    # def data_format(self):
    #     pass

    def get_results_path(self):
        """
        Return the path when the results from the analysis will be saved or None if it doesn't exist yet
        Returns:

        """
        return self._results_path

    def create_results_directory(self, dir_path):
        """
        Will create a directory in dir_path with the name of analysis and time at which the directory is created
        so it can be unique. The attribute _results_path will be updated with the path of this new directory
        Args:
            dir_path: path of the dir in which create the results dir

        Returns: this new directory

        """
        # first we check if dir_path exists
        if (not os.path.exists(dir_path)) or (not os.path.isdir(dir_path)):
            print(f"{dir_path} doesn't exist or is not a directory")
            return

        time_str = datetime.now().strftime("%Y_%m_%d.%H-%M-%S")
        self._results_path = os.path.join(dir_path, self.name + f"_{time_str}")
        os.mkdir(self._results_path)

        return self._results_path

    def get_data_identifiers(self):
        """
        Return a list of string representing each data to analyse
        Returns:

        """
        identifiers = []
        if self._data_format == "nwb":
            identifiers = [data.identifier for data in self._data_to_analyse]

        return identifiers

    def copy(self):

        module_name = 'cicada.analysis.' + class_name_to_file_name(self.__class__.__name__)
        module = importlib.import_module(module_name)
        new_class = getattr(module, self.__class__.__name__)
        new_object = new_class()
        new_object.name = self.name
        new_object.yaml_name = self.yaml_name
        new_object.short_description = self.short_description
        new_object.family_id = self.family_id
        new_object.long_description = self.long_description
        new_object.set_data(self._data_to_analyse, self._data_format)
        new_object.config_handler = self.config_handler
        return new_object

    def set_yaml_name(self, name):
        self.yaml_name = name

    def set_data(self, data_to_analyse, data_format="nwb"):
        """
                A list of
                :param data_to_analyse: list of data_structure
                :param data_format: indicate the type of data structure. for NWB, NIX
        """
        # TODO: don't use data_format, as data_format will be available in the wrapper itself
        if not isinstance(data_to_analyse, list):
            data_to_analyse = [data_to_analyse]
        self._data_to_analyse = data_to_analyse
        self._data_format = data_format
        # set_arguments_for_gui cllaed in analysis_tree_gui when double_clicked is called
        # self.set_arguments_for_gui()

    @abstractmethod
    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        self.invalid_data_help = None

    def add_argument_for_gui(self, with_incremental_order=True, **kwargs):
        """

        Args:
            **kwargs:
            with_incremental_order: boolean, if True means the order of the argument will be the same as when added

        Returns:

        """
        if with_incremental_order:
            kwargs.update({"order_index": self.current_order_index})
            self.current_order_index += 1

        self.analysis_arguments_handler.add_argument(**kwargs)

    def set_arguments_for_gui(self):
        """
        Need to be implemented in order to be used through the graphical interface.
        super().set_arguments_for_gui() should be call first to instantiate an AnalysisArgumentsHandler and
        create the attribution for results_path
        :return: None
        """
        if not self.gui:
            return

        # creating a new AnalysisArgumentsHandler instance
        self.analysis_arguments_handler = AnalysisArgumentsHandler(cicada_analysis=self)
        # we order_index at 1000 for it to be displayed at the end
        default_results_path = None
        mandatory = True
        if self.config_handler is not None:
            default_results_path = self.config_handler.get_default_results_path()
            mandatory = False
        results_path_arg = {"arg_name": "results_path", "value_type": "dir",
                            "default_value": default_results_path, "short_description": "Directory to save the results",
                            "with_incremental_order": False, "order_index": 1000, "mandatory": mandatory}

        self.add_argument_for_gui(**results_path_arg)

   
    def get_data_to_analyse(self):

        """

        :return: a list of the data to analyse
        """
        return self._data_to_analyse

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    @abstractmethod
    def run_analysis(self, **kwargs):
        """
        Run the analysis
        :param kwargs:
        :return:
        """
        self.analysis_start_time = time()

        if "results_path" in kwargs:
            results_path = kwargs["results_path"]
            if self._results_path is None:
                self.create_results_directory(results_path)
                if self.gui:
                    thread = QThread.currentThread()
                    thread.set_results_path(self._results_path)
        if self.yaml_name == '':
            self.yaml_name = path_leaf(self._results_path)
        self.analysis_arguments_handler.save_analysis_arguments_to_yaml_file(path_dir=self._results_path,
                                                                             yaml_file_name=self.yaml_name,
                                                                             )

    def update_progressbar(self, time_started, increment_value=0, new_set_value=0):
        """

        Args:
            time_started (float): Start time of the analysis
            increment_value (float): Value that should be added to the current value of the progress bar
            new_set_value (float):  Value that should be set as the current value of the progress bar

        """
        time_elapsed = time() - time_started

        if self.gui:
            worker = QThread.currentThread()
            worker.setProgress(name=worker.name, time_elapsed=time_elapsed, increment_value=increment_value,
                               new_set_value=new_set_value)
        else:
            pass

    def add_ci_movie_arg_for_gui(self, long_description=None):
        """
        Will add an argument for gui, named ci_movie that will list all calcium imaging available for each session
        Returns:

        """
        ci_movies_dict_for_arg = dict()
        for data in self._data_to_analyse:
            ci_movies_dict = data.get_ci_movies(only_2_photons=False)
            for movie_id in ci_movies_dict.keys():
                # we put the identifier of each movie as values
                ci_movies_dict_for_arg[data.identifier] = movie_id

        ci_movie_arg = {"arg_name": "ci_movie", "choices": ci_movies_dict_for_arg,
                        "short_description": "Calcium imaging movie to use", "mandatory": False,
                        "multiple_choices": False}

        if long_description is not None:
            ci_movie_arg.update({"long_description": long_description})

        self.add_argument_for_gui(**ci_movie_arg)

    def add_segmentation_arg_for_gui(self):
        """
            Will add an argument for gui, named segmentation that will list all segmentations available for each session
            Returns:

        """
        segmentation_dict_for_arg = dict()
        for data in self._data_to_analyse:
            segmentation_dict_for_arg[data.identifier] = data.get_segmentations()

        # not mandatory, because one of the element will be selected by the GUI
        segmentation_arg = {"arg_name": "segmentation", "choices": segmentation_dict_for_arg,
                            "short_description": "Segmentation to use", "mandatory": False,
                            "multiple_choices": False}

        self.add_argument_for_gui(**segmentation_arg)

    def add_roi_response_series_arg_for_gui(self, short_description, long_description=None):
        rrs_dict_for_arg = dict()
        for data in self._data_to_analyse:
            rrs_dict_for_arg[data.identifier] = data.get_roi_response_series()

        rrs_arg = {"arg_name": "roi_response_series", "choices": rrs_dict_for_arg,
                   "short_description": short_description, "mandatory": False,
                   "multiple_choices": False}

        if long_description is not None:
            rrs_arg.update({"long_description": long_description})

        self.add_argument_for_gui(**rrs_arg)

    def add_intervals_arg_for_gui(self, short_description, arg_name="intervals", long_description=None):
        intervals_dict_for_arg = dict()
        for data in self._data_to_analyse:
            intervals_dict_for_arg[data.identifier] = data.get_intervals_names()

        intervals_arg = {"arg_name": arg_name, "choices": intervals_dict_for_arg,
                         "short_description": short_description, "mandatory": False,
                         "multiple_choices": False}

        if long_description is not None:
            intervals_arg.update({"long_description": long_description})

        self.add_argument_for_gui(**intervals_arg)
