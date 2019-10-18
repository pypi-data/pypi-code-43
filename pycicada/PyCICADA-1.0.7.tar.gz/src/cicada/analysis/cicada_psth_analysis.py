from cicada.analysis.cicada_analysis import CicadaAnalysis
import sys
from qtpy.QtCore import Signal
from qtpy import QtCore
import PyQt5.QtCore as Core
from time import sleep, time

class CicadaPsthAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        A list of
        :param data_to_analyse: list of data_structure
        :param family_id: family_id indicated to which family of analysis this class belongs. If None, then
        the analysis is a family in its own.
        :param data_format: indicate the type of data structure. for NWB, NIX
        """
        CicadaAnalysis.__init__(self, name="PSTH", family_id="Intervals",
                         short_description="Build PSTH")

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        super().check_data()

        self.invalid_data_help = "Not implemented yet"
        return False

        if self._data_format != "nwb":

            # non NWB format compatibility not yet implemented
            return False
        # if len(self._data_to_analyse) < 3:
        #     return False
        # for data in self._data_to_analyse:
        #     # check is there is at least one processing module
        #     if len(data.processing) == 0:
        #         return False
        #
        #     # in our case, we will use 'ophys' module
        #     if "ophys" not in data.processing:
        #         return False
        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        self.add_intervals_arg_for_gui(arg_name="intervals", short_description="Intervals representing the stimuli")

        range_arg = {"arg_name": "psth_range", "value_type": "int", "min_value": 50, "max_value": 2000,
                     "default_value": 500, "short_description": "Range of the PSTH (ms)"}
        self.add_argument_for_gui(**range_arg)

        stim_arg = {"arg_name": "stimulus name", "value_type": "str",
                     "default_value": "stim", "short_description": "Name of the stimulus",
                    "long_description": "Input the name to be given to the stimulus"}
        self.add_argument_for_gui(**stim_arg)

        plot_arg = {"arg_name": "plot_options", "choices": ["lines", "bars"],
                    "default_value": "bars", "short_description": "Options to display the PSTH"}
        self.add_argument_for_gui(**plot_arg)

        avg_arg = {"arg_name": "average_fig", "value_type": "bool",
                   "default_value": True, "short_description": "Add a figure that average all sessions"}

        self.add_argument_for_gui(**avg_arg)

        choices_dict = dict()
        for index, data in enumerate(self._data_to_analyse):
            if index < 2:
                choices_dict[data.identifier] = ["test_1", "test_2"]
            else:
                choices_dict[data.identifier] = ["test_3", "test_4", "test_6"]

        test_arg = {"arg_name": "test_multiple_choices", "choices": choices_dict,
                    "short_description": "Test choices for each session",
                    "multiple_choices": True}

        self.add_argument_for_gui(**test_arg)

        format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
                    "default_value": "pdf", "short_description": "Formats in which to save the figures",
                    "multiple_choices": True}

        self.add_argument_for_gui(**format_arg)

        self.add_roi_response_series_arg_for_gui(short_description="Neural activity to use", long_description=None)

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        test
        :param kwargs:
        :return:
        """
        CicadaAnalysis.run_analysis(self, **kwargs)
        # for data in self._nwb_data:
        #     print(f"PSTH ----- {data.identifier} on range {kwargs['psth_range']} with {kwargs['plot_options']} "
        #           f"plot using {kwargs['segmentation']} "
        #           f"with formats {kwargs['save_formats']} ")
        start_time = time()
        for i in range(101):
            print(i)
            # sys.stderr.write('No error\n')
            sleep(0.1)
            self.update_progressbar(start_time, 1)
            if i == 50:
                x = {}
                for j in range(1000000):
                    x = {1: x}
                repr(x)
