from __future__ import print_function
""" this is the information of dataset level info"""
from collections import OrderedDict

import raven_preprocess.col_info_constants as col_const


class DatasetLevelInfo(object):

    def __init__(self, df):
        """This class sets the dataset level info of the preprocess file. """

        self.dataframe = df
        self.rows_count = None
        self.variables_count = None
        self.has_error = False
        self.error_messages = []
        self.final_output = OrderedDict()

        self.set_values()

    def set_values(self):
        """
        "dataset": {
       "row_cnt": 1000,
       "variable_cnt": 25
            }
        """
        if self.dataframe is not None:
            self.rows_count = self.dataframe.shape[0]  \
                # shape[0] gives the number of records/rows and is faster then count
            self.variables_count = len(self.dataframe.columns)
        else:
            self.has_error = True
            self.error_messages.append(" There is no data available to get dataset level info")
            return
        if self.rows_count < 1:
            self.has_error = True
            self.error_messages.append(" This is an empty dataframe with no record")
            return
        if self.variables_count < 1:
            self.has_error = True
            self.error_messages.append(" This is an empty dataframe with no variables")
            return

        self.final_output[col_const.DATASET_DESCRIPTION] = ''
        self.final_output[col_const.DATASET_UNIT_OF_ANALYSIS] = ''
        self.final_output[col_const.DATASET_STRUCTURE] = col_const.STRUCTURE_LONG
        self.final_output[col_const.DATASET_ROW_CNT] = self.rows_count
        self.final_output[col_const.DATASET_VARIABLE_CNT] = self.variables_count
