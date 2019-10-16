from __future__ import print_function
import json, time, datetime
from collections import OrderedDict
import decimal
import pandas as pd
import os
from os.path import isfile
from raven_preprocess.basic_utils.basic_response import (ok_resp, err_resp)


import raven_preprocess.col_info_constants as col_const
from raven_preprocess.np_json_encoder import NumpyJSONEncoder
from raven_preprocess.type_guess_util import TypeGuessUtil
from raven_preprocess.summary_stats_util import SummaryStatsUtil
from raven_preprocess.column_info import ColumnInfo
from raven_preprocess.plot_values import PlotValuesUtil
from raven_preprocess.variable_display_util import VariableDisplayUtil
from raven_preprocess.dataset_level_info_util import DatasetLevelInfo
from raven_preprocess.file_format_util import FileFormatUtil


KEY_JSONLD_CITATION = 'jsonld_citation'


class PreprocessRunner(object):
    """Preprocess relatively small files using pandas"""

    def __init__(self, dataframe, **kwargs):
        """Init with a pandas dataframe

        optional kwargs:
        job_id - id of a PreprocessJob object
        jsonld_citation - jsonld_citation as an OrderedDict
        """
        self.data_frame = dataframe
        self.job_id = kwargs.get('job_id', None)

        # for a json_ld citation from dataverse
        self.jsonld_citation = kwargs.get(KEY_JSONLD_CITATION, None)
        self.schema_info_dict = kwargs.get('SCHEMA_INFO_DICT', None)

        # for data source
        self.data_source_info = kwargs.get('data_source_info')

        self.celery_task = kwargs.get('celery_task')
        # to populate
        self.variable_info = {}  # { variable_name: ColumnInfo, ...}
        self.num_vars = None
        self.num_vars_complete = None

        # for error handling
        self.has_error = False
        self.error_message = None
        time_stamp = time.time()
        self.current_time = datetime.datetime.fromtimestamp(time_stamp)\
            .strftime('%Y-%m-%d %H:%M:%S')
        self.preprocess_id = None


        self.run_preprocess()

    def add_error_message(self, err_msg):
        """Add error message"""
        # print(err_msg)
        self.has_error = True
        self.error_message = err_msg

    def update_task_status(self):
        """Optional: update a celery task status"""
        if not self.celery_task:
            # no task available
            return

        if self.num_vars and self.num_vars > 0:
            self.celery_task.update_state(
                state='PROGRESS',
                meta={'current': self.num_vars_complete,
                      'total': self.num_vars})
            return

        self.add_error_message('Celery update failed')

    def run_preprocess(self):
        """Run preprocess"""
        if not isinstance(self.data_frame, pd.DataFrame):
            self.add_error_message('The dataframe is not valid')
            return False

        if not self.calculate_features():
            return False

        return True

    @staticmethod
    def load_from_file(input_file, **kwargs):
        """decide type/format, and name"""
        # Use new class to decide "csv file", "tab file"
        # etc
        file_format_util = FileFormatUtil(input_file, **kwargs)

        if file_format_util.has_error:
            return err_resp(file_format_util.error_message)
        else:
            if 'data_source_info' not in kwargs:
                kwargs['data_source_info'] = file_format_util.data_source_info

            runner = PreprocessRunner(\
                        file_format_util.dataframe,
                        **kwargs)
                        #job_id=job_id,
                        #data_source_info=file_format_util.data_source_info)
            if runner.has_error:
                return err_resp(runner.error_message)

            return ok_resp(runner)

    @staticmethod
    def load_update_file(preprocess_input, update_input):
        """ Returns the dict from the file input"""
        if not isfile(preprocess_input):
            return None, 'The file was not found: [%s]' % preprocess_input
        elif not isfile(update_input):
            return None, 'The file was not found: [%s]' % update_input

        filesize_preprocess = os.stat(preprocess_input).st_size
        filesize_update = os.stat(update_input).st_size
        if filesize_preprocess == 0:
            return None, 'The file size is zero: [%s]' % preprocess_input

        elif filesize_update == 0:
            return None, 'The file size is zero: [%s]' % update_input

        try:
            preprocess_input_dict = json.loads(preprocess_input, object_pairs_hook=OrderedDict)
        except TypeError as err_obj:
            err_msg = ('Input does not have Ordered dict convertable type'
                       '\n - File: %s\n - %s') % (preprocess_input, err_obj)
            return None, err_msg
        except Exception as err_obj:
            err_msg = ('Failed to convert into Orderd dict'
                       ' \n - File: %s\n - %s') % (preprocess_input, err_obj)
            return None, err_msg

        try:
            update_input_dict = json.loads(update_input,
                                           object_pairs_hook=OrderedDict,
                                           parse_float=decimal.Decimal)
        except TypeError as err_obj:
            err_msg = ('Input does not have Ordered dict convertable type'
                       '\n - File: %s\n - %s')% (update_input, err_obj)
            return None, err_msg
        except Exception as err_obj:
            err_msg = ('Failed to convert into Orderd dict'
                       ' \n - File: %s\n - %s') % (update_input, err_obj)
            return None, err_msg

        display_util = VariableDisplayUtil(preprocess_input_dict, update_input_dict)

        if display_util.has_error:
            return None, display_util.get_error_messages()

        return display_util, None

    def calculate_features(self):
        """For each variable, calculate summary stats"""
        if self.has_error:
            return False
        # Iterate through data frame and
        # run type guess, cal_stats, and plot_values on each ColumnInfo object
        #
        self.num_vars = len(self.data_frame.columns)
        self.num_vars_complete = 0

        for colnames in self.data_frame:
            # set stats for each column
            col_info = ColumnInfo(colnames)
            col_series = self.data_frame[colnames]

            type_guess_util = TypeGuessUtil(col_series, col_info)
            if type_guess_util.has_error():
                self.add_error_message(type_guess_util.get_error_message())
                return

            SummaryStatsUtil(col_series, col_info)
            PlotValuesUtil(col_series, col_info)
            # VariableDisplayUtil(col_series, col_info)
            # assign object info to the variable_info
            #
            self.num_vars_complete += 1
            self.variable_info[colnames] = col_info

        # print("completed column", self.num_vars_complete)
        # print(" Number of variable ", self.num_vars)
        return True

    '''
    def add_plot_info(self):
        """For each variable, add plot information as needed"""
        if self.has_error:
            return False

        if not self.variable_info:
            self.add_error_message('Error encountered. self.variable_info not available')
            return False

        for col_name, col_info in self.variable_info.items():
            # set stats for each column
            PlotValuesUtil(self.data_frame, col_info)

        return True
    '''

    def get_self_section(self):
        """
        {
          "self": {
            "description": "TwoRavens metadata generated by  https://github.com/TwoRavens/raven-metadata-service",
            "created": "current timestamp", # job.modified when done via the web
            "preprocess_id": 45  # null for now; job.id when done via the web
            "version": 1 # subsequent updates will increment this number
        },
        """
        self_section = OrderedDict()
        self_section['description'] = \
               ('TwoRavens metadata generated by'
                ' https://github.com/TwoRavens/raven-metadata-service')
        self_section['created'] = self.current_time
        self_section[col_const.PREPROCESS_ID] = self.job_id
        self_section['version'] = 1

        if self.schema_info_dict:
            self_section['schema'] = self.schema_info_dict

        return self_section


    def get_dataset_level_info(self):
        """
        "dataset": {
       "row_cnt": 1000,
       "variable_cnt": 25
                }
        """
        dataset_level_info = DatasetLevelInfo(self.data_frame)
        if dataset_level_info.has_error:
            info_dict = OrderedDict()
            info_dict["error"] = dataset_level_info.error_messages
            return info_dict

        info_dict = dataset_level_info.final_output
        if self.data_source_info:
            info_dict[col_const.DATA_SOURCE_INFO] = self.data_source_info.as_dict()

        if self.jsonld_citation:
            info_dict[col_const.DATASET_CITATION] = self.jsonld_citation
            #info_dict[col_const.DATA_SOURCE_INFO][col_const.DATASET_CITATION] = \
            #    self.jsonld_citation

        return info_dict

    def show_final_info(self):
        """Print the final info to the screen"""
        if self.has_error:
            err_msg = 'An error occurred earlier in the process:\n%s' % \
                      self.error_message
            print(err_msg)
            return

        info_string = self.get_final_dict(as_string=True)

        print(info_string)

    def get_final_json_indented(self, indent=4):
        """Return the final variable info as a JSON string"""
        if self.has_error:
            err_msg = 'An error occurred earlier in the process:\n%s' % \
                      self.error_message
            print(err_msg)
            return

        return self.get_final_dict(as_string=True,
                                   indent=indent)

    def get_final_json(self, indent=None):
        """Return the final variable info as a JSON string"""
        if self.has_error:
            err_msg = 'An error occurred earlier in the process:\n%s' % \
                      self.error_message
            print(err_msg)
            return

        return self.get_final_dict(as_string=True,
                                   indent=indent)

    def get_final_dict(self, as_string=False, **kwargs):
        """Return the preprocess data as an OrderedDict"""
        if self.has_error:
            err_msg = 'An error occurred earlier in the process:\n%s' % \
                      self.error_message
            print(err_msg)
            return

        fmt_variable_info = OrderedDict()   # capture the variables section
        fmt_display_variable_info = OrderedDict()   # capture the variable_display section
        fmt_display_variable_info['editable'] = ColumnInfo.get_editable_column_labels()
        # Iterate through each column and pull variable + variable_display info
        #
        for col_name, col_info in self.variable_info.items():
            # col_info.print_values()
            fmt_variable_info[col_name] = col_info.as_dict()
            fmt_display_variable_info[col_name] = VariableDisplayUtil.get_default_settings()

        # Format the entire document
        #
        overall_dict = OrderedDict()

        overall_dict[col_const.SELF_SECTION_KEY] = self.get_self_section()  # add the "self" section

        # add the 'dataset' section
        overall_dict[col_const.DATASET_LEVEL_KEY] = self.get_dataset_level_info()

        overall_dict[col_const.VARIABLES_SECTION_KEY] = fmt_variable_info    # add "variables"

        overall_dict[col_const.VARIABLE_DISPLAY_SECTION_KEY] = fmt_display_variable_info

        if as_string:
            # Convert the OrderedDict to a JSON string
            #
            indent_level = kwargs.get('indent', 4)
            if indent_level is None:
                pass
            elif (not isinstance(indent_level, int)) or indent_level > 50:
                indent_level = 4

            return json.dumps(overall_dict,
                              indent=indent_level,
                              cls=NumpyJSONEncoder)

        # w/o this step, a regular json.dumps() fails on the returned dict
        #
        jstring = json.dumps(overall_dict,
                             cls=NumpyJSONEncoder)
        return json.loads(jstring,
                          object_pairs_hook=OrderedDict,
                          parse_float=decimal.Decimal)
