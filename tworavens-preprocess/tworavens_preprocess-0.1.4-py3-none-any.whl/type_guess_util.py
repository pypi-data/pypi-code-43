""" Module for type guessing """
import datetime
import re

import dateutil.parser
import numpy as np
import pandas as pd
from pandas.api.types import is_float_dtype, is_numeric_dtype

import raven_preprocess.col_info_constants as col_const
from raven_preprocess.column_info import ColumnInfo
from raven_preprocess.basic_utils.basic_err_check import BasicErrCheck

# allow values like 01.02.03
date_re = re.compile(r'[\d]+\.[\d]+\.[\d]+')
# filter out values like -3, .1, etc
not_date_re = re.compile(r'-?[.\d]+')

def parse_date(val, year):
    """returns datetime.datetime or raises exception by parsing with dateutil after filtering out obvious non-date values"""
    if not isinstance(val, str):
        if not year and val < 1600 or val > 2100:
            raise ValueError

        val = str(val)

    val = val.strip().replace(',', '/')
    if not date_re.fullmatch(val) and not_date_re.fullmatch(val) and not len(val) in (4, 6, 8) or val.startswith('-'):
        raise ValueError

    return dateutil.parser.parse(val)

class TypeGuessUtil(BasicErrCheck):
    """Check variable types of a dataframe"""
    def __init__(self, col_series, col_info):
        """Init with a pandas dataframe"""
        assert col_series is not None, "dataframe can't be None"

        self.col_series = col_series
        self.col_info = col_info
        self.col_info.time_val = col_const.UNKNOWN
        self.binary = False

        # final outout returned
        self.check_types()

    def check_types(self):
        """check the types of the dataframe"""
        # assert self.colnames, 'self.colnames must have values'

        self.col_info.invalid = int(self.col_series.isnull().sum())
        self.col_info.valid = int(self.col_series.count())

        # Drop nulls...
        self.col_series.dropna(inplace=True)

        self.col_info.binary = col_const.BINARY_YES if len(self.col_series.unique()) == 2 else col_const.BINARY_NO

        if self.is_not_numeric(self.col_series) or self.is_logical(self.col_series):
            self.col_info.time_val = self.check_time(self.col_series)
            self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
            self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            self.col_info.nature = col_const.NATURE_NOMINAL
        else:
            try:
                series_info = self.col_series.astype('int')
            except ValueError as e:
                self.add_err_msg('Type guess error when converting to int: %s' % e)
                return

            if any(series_info.isnull()):
                # CANNOT REACH HERE B/C NULLS ARE DROPPED!

                self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
                self.col_info.nature = col_const.NATURE_NOMINAL
                self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            else:
                self.col_info.numchar_val = col_const.NUMCHAR_NUMERIC

                ints = self.col_series.where(lambda x: x is 0 or x % 1 == 0.0)
                if is_float_dtype(self.col_series) and ints.count() != len(self.col_series):
                    self.col_info.default_interval = col_const.INTERVAL_CONTINUOUS
                    self.col_info.nature = self.check_nature(self.col_series, True)
                else:
                    self.col_info.time_val = self.check_time(self.col_series)
                    self.col_info.default_interval = col_const.INTERVAL_DISCRETE
                    self.col_info.nature = self.check_nature(series_info, False)

    @staticmethod
    def is_not_numeric(var_series):
        """Check if pandas Series is a numeric"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        if var_series.size == 0 or var_series.dtype == 'bool':
            return True

        return not is_numeric_dtype(var_series) or var_series.dropna().empty

    @staticmethod
    def is_logical(var_series):
        """Check if pandas Series contains boolean values"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        # Check the dtype
        #    "bool" - True, clearly logical
        #    "object" - possibly logical that had contained np.Nan
        #    ~anything else~ - False
        if var_series.dtype == 'bool':
            return True
        elif var_series.dtype != 'object':
            return False

        # It's an object. Check if all the values are logical
        logical = {True, False, None, np.nan}
        total = sum(cnt for val, cnt in var_series.value_counts(dropna=False).iteritems() if val in logical)
        return total == var_series.size

    @staticmethod
    def check_nature(data_series, continuous_check):
        """Check the nature of the Series"""
        if continuous_check:
            if data_series.between(0, 1).all():
                return col_const.NATURE_PERCENT
            elif data_series.between(0, 100).all() and min(data_series) < 15 and max(data_series) > 85:
                return col_const.NATURE_PERCENT
            return col_const.NATURE_RATIO
        return col_const.NATURE_ORDINAL

    @staticmethod
    def check_time(var_series):
        """Check if Series is a datetime"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        name = var_series.name.lower()
        if name.endswith('id') or not var_series.dtype in ('int64', 'object'):
            return col_const.UNKNOWN

        try:
            var_series[:10].apply(lambda x: parse_date(x, name == 'year'))
            return True
        except:
            return col_const.UNKNOWN
