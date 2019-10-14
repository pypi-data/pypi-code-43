# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public holiday."""

from .country_or_region_time_public_data import CountryOrRegionTimePublicData

from datetime import datetime, date
from dateutil import parser
from pandas import DataFrame as PdDataFrame
from pandas import Series
import pandas as pd
from pyspark.sql.functions import col
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from typing import Optional, List, Dict
from warnings import warn

from ..dataaccess._public_holidays_offline_blob_info import PublicHolidaysOfflineBlobInfo
from ..environ import SparkEnv, PandasEnv
from ..dataaccess.pandas_data_load_limit import PandasDataLoadLimitNone
from multimethods import multimethod


import os.path
import pkg_resources
import lzma
import pickle
from pyspark.sql import SparkSession

pkgs = __name__.split('.')
PACKAGE_NAME = '.'.join(pkgs[: pkgs.index('opendatasets') + 1])
HOLIDAYS_DATA_PATH = pkg_resources.resource_filename(PACKAGE_NAME,
                                                     os.path.join('data', 'holidays.7z'))


def _holiday_data_loader(_path=HOLIDAYS_DATA_PATH):
    """Load holiday data as a static initializer."""
    with lzma.open(_path, "rb") as fr:
        df = pickle.loads(fr.read())
        df['countryRegionCode'] = df['countryRegionCode'] \
            .apply(lambda x: x if type(x) == str else None)
        df['isPaidTimeOff'] = df['isPaidTimeOff'] \
            .apply(lambda x: x if type(x) == bool else None)
        return df


class PublicHolidaysOfflineAccessory(CountryOrRegionTimePublicData):
    """Public holiday class."""

    default_start_date = parser.parse('1970-01-01')
    default_end_date = parser.parse('2099-01-01')
    default_country_or_region = 'US'

    HOLIDAYS_DF = _holiday_data_loader()  # type: pd.DataFrame

    __blobInfo = PublicHolidaysOfflineBlobInfo()

    data = None

    def _prepare_cols(self):
        """Prepare columns that can be used to join with other data."""
        self.time_column_name = 'date'
        self.countrycode_column_name = 'countryRegionCode'
        self.country_or_region_column_name = 'countryOrRegion'

    def __init__(
            self,
            country_or_region: str = default_country_or_region,
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param country_or_region: country or region you'd like to query against.
        :type country_or_region: str
        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        self.dataset = None
        self._registry_id = self.__blobInfo.registry_id
        self.path = HOLIDAYS_DATA_PATH
        self._prepare_cols()

        if country_or_region is None:
            raise ValueError('Unsupported country or region:' + country_or_region)
        self.country_or_region = country_or_region
        self.start_date = start_date\
            if (self.default_start_date < start_date)\
            else self.default_start_date
        self.end_date = end_date\
            if (self.default_end_date > end_date)\
            else self.default_end_date

        self.holidays_dates = None  # type: Optional[Dict[datetime.datetime, None]]
        self.holidays_dates_country = None  # type: Optional[str]
        self.holidays_dates_country_code = None  # type: Optional[str]
        mappings_cr = Series(PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryRegionCode.values,
                             index=PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryOrRegion)
        mappings_cc = Series(PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryOrRegion.values,
                             index=PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryRegionCode)
        mappings_cr = mappings_cr.append(mappings_cc)
        self.holidays_country_mappings = mappings_cr.to_dict()

        super(PublicHolidaysOfflineAccessory, self).__init__(cols=cols, enable_telemetry=enable_telemetry)
        if enable_telemetry:
            self.log_properties['CountryOrRegion'] = self.country_or_region
            self.log_properties['StartDate'] = self.start_date
            self.log_properties['EndDate'] = self.end_date
            self.log_properties['Path'] = self.path

    @multimethod(SparkEnv, SparkDataFrame)
    def _filter_country_region(self, env, data):
        """Filter country or region."""
        if len(self.country_or_region) > 0:
            data = data.where((col(self.countrycode_column_name) == self.country_or_region) | (
                col(self.country_or_region_column_name) == self.country_or_region))
        return data

    @multimethod(PandasEnv, PdDataFrame)
    def _filter_country_region(self, env, data):
        """Filter country or region."""
        if len(self.country_or_region) > 0:
            data = data[(data[self.countrycode_column_name] == self.country_or_region) & (
                data[self.countrycode_column_name] == self.country_or_region)]
        return data

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        self.data = self.data.na.drop(how='all', subset=self.cols).na.drop(how='any', subset=[self.time_column_name])
        self.data = self._filter_country_region(env, self.data)

        ds = super(PublicHolidaysOfflineAccessory, self).filter(env, min_date, max_date)
        ds = self._filter_country_region(env, ds)
        return ds.select(*self.selected_columns)

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        ds = super(PublicHolidaysOfflineAccessory, self).filter(env, min_date, max_date)
        ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
            how='any', axis=0, subset=[self.time_column_name])
        ds = self._filter_country_region(env, ds)

        return ds[self.selected_columns]

    def _get_mandatory_columns(self):
        """
        Get mandatory columns to select.

        :return: a list of column names.
        :rtype: list
        """
        return [self.time_column_name, self.country_or_region_column_name, self.countrycode_column_name]

    def get_pandas_limit(self):
        """Get instance of pandas data load limit class."""
        return PandasDataLoadLimitNone()

    def _to_spark_dataframe(self, activity_logger):
        """To spark dataframe.

        :param activity_logger: activity logger

        :return: SPARK dataframe
        """
        spark = SparkSession.builder.getOrCreate()
        df = self._to_pandas_dataframe(None)
        df['newCountryRegionCode'] = df['countryRegionCode'].apply(lambda x: x if type(x) == str else None)
        df = df.drop(columns=['countryRegionCode']).rename(columns={'newCountryRegionCode': 'countryRegionCode'})
        ds = spark.createDataFrame(df)
        ds = self._filter_country_region(SparkEnv(), ds)
        return ds

    def _to_pandas_dataframe(self, activity_logger):
        """
        Get pandas dataframe.

        :param activity_logger: activity logger

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        ds = PublicHolidaysOfflineAccessory.HOLIDAYS_DF
        filter_mask = (ds[self.time_column_name] >= self.start_date) & (
            ds[self.time_column_name] <= self.end_date)
        if self.cols is not None:
            all_columns = self.selected_columns
            ds = ds.loc[filter_mask]
            ds = ds[all_columns]
        else:
            ds = ds.loc[filter_mask]
            # in case of inst.selected_columns == ['*']
            self.selected_columns = list(ds.columns)
        ds = self._filter_country_region(PandasEnv(), ds)
        return ds

    def get_holidays_dates(self, country_code: Optional[str] = None, country_or_region: Optional[str] = None) \
            -> Optional[Dict[datetime, None]]:
        """
        Get a Dict with Key of the dates of holidays.

        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: The dict with dates of holidays as the keys and None as values.
        """
        date_col_name = 'date'
        if date_col_name in PublicHolidaysOfflineAccessory.HOLIDAYS_DF.columns:
            if country_code:
                if self.holidays_dates_country_code != country_code:
                    self.holidays_dates = dict.fromkeys(
                        PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                            PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryRegionCode == country_code][
                                date_col_name].tolist(), None)
                    self.holidays_dates_country_code = country_code
                    self.holidays_dates_country = self.holidays_country_mappings[country_code]
                elif self.holidays_dates_country_code == country_code and self.holidays_dates is None:
                    self.holidays_dates = dict.fromkeys(
                        PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                            PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryRegionCode == country_code][
                                date_col_name].tolist(), None)
            elif country_or_region:
                if self.holidays_dates_country != country_or_region:
                    self.holidays_dates = dict.fromkeys(
                        PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                            PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryOrRegion == country_or_region][
                                date_col_name].tolist(), None)
                    self.holidays_dates_country_code = self.holidays_country_mappings[country_or_region]
                elif self.holidays_dates_country == country_or_region and self.holidays_dates is None:
                    self.holidays_dates = dict.fromkeys(
                        PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                            PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryOrRegion == country_or_region][
                                date_col_name].tolist(), None)
            else:
                self.holidays_dates_country = None
                self.holidays_dates = None
        else:
            warn("Missing Date column in the holiday data.", ResourceWarning)
            return None

        return self.holidays_dates

    def is_holiday(self, target_date: date, country_code: str = "US") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        country_holiday_dates = self.get_holidays_dates(country_code=country_code)
        if country_holiday_dates:
            return (target_date in country_holiday_dates)
        else:
            return False

    def is_holiday_by_country_or_region(self, target_date: date, country_or_region: str = "United States") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        country_holiday_dates = self.get_holidays_dates(country_or_region=country_or_region)
        if country_holiday_dates:
            return (target_date in country_holiday_dates)
        else:
            return False

    def get_holidays_in_range(self, start_date: date, end_date: date, country_code: str = "US") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        rs = pd.DataFrame(columns=["normalizeHolidayName", "date", "isPaidTimeOff"])
        rsdf_country = PublicHolidaysOfflineAccessory.HOLIDAYS_DF
        if country_code is not None:
            rsdf_country = PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryRegionCode == country_code]
        else:
            return rs
        rs_date = rsdf_country[(rsdf_country.date >= start_date) & (rsdf_country.date <= end_date)]
        rs_date.drop(columns=['countryOrRegion', 'countryRegionCode'], inplace=True)
        rs_date.reset_index(inplace=True, drop=True)
        rs = rs_date
        return rs

    def get_holidays_in_range_by_country_or_region(self, start_date: date, end_date: date,
                                                   country_or_region: str = "United States") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        rs = pd.DataFrame(columns=["normalizeHolidayName", "date", "isPaidTimeOff"])
        rsdf_country = PublicHolidaysOfflineAccessory.HOLIDAYS_DF
        if country_or_region is not None:
            rsdf_country = PublicHolidaysOfflineAccessory.HOLIDAYS_DF[
                PublicHolidaysOfflineAccessory.HOLIDAYS_DF.countryOrRegion == country_or_region]
        else:
            return rs
        rs_date = rsdf_country[(rsdf_country.date >= start_date) & (rsdf_country.date <= end_date)]
        rs_date.drop(columns=['countryOrRegion', 'countryRegionCode'], inplace=True)
        rs_date.reset_index(inplace=True, drop=True)
        rs = rs_date
        return rs
