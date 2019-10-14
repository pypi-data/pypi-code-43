# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NOAA GFS weather."""

from datetime import datetime
from dateutil import parser
from pyspark.sql.functions import col, udf
from typing import List, Optional

from ..dataaccess._noaa_gfs_weather_blob_info import NoaaGfsWeatherBlobInfo
from .location_time_public_data import LocationTimePublicData
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ..environ import SparkEnv, PandasEnv
from ..dataaccess.pandas_data_load_limit import PandasDataLoadLimitToDay
from multimethods import multimethod


class NoaaGfsWeatherAccessory(LocationTimePublicData):
    """NOAA GFS forecast weather accessory class."""

    default_start_date = parser.parse('2018-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = NoaaGfsWeatherBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)

    def __prepare_cols(self):
        """Prepare columns that can be used to join with other data."""
        self.time_column_name = 'currentDatetime'
        self.latitude_column_name = 'latitude'
        self.longitude_column_name = 'longitude'
        self.id = 'ID'

    def __init__(
            self,
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            limit: Optional[int] = -1,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param limit: to_pandas_dataframe() will load only "limit" days of data. -1 means no limit.
        :type limit: int
        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        self.dataset = None
        self._registry_id = self._blobInfo.registry_id
        self.path = self._blobInfo.get_data_wasbs_path()
        self.__prepare_cols()
        self.start_date = start_date\
            if (self.default_start_date < start_date)\
            else self.default_start_date
        self.end_date = end_date\
            if (end_date is None or self.default_end_date > end_date)\
            else self.default_end_date
        super(NoaaGfsWeatherAccessory, self).__init__(cols, enable_telemetry=enable_telemetry)
        self.limit = limit
        if enable_telemetry:
            self.log_properties['StartDate'] = self.start_date
            self.log_properties['EndDate'] = self.end_date
            self.log_properties['Path'] = self.path

    def update_dataset(self, ds, enable_telemetry: bool = True):
        """Update dataset."""
        self.dataset = ds
        if enable_telemetry:
            self.log_properties['from_dataset'] = True

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        self.data = self.data.na.drop(how='all', subset=self.cols).na.drop(
            how='any', subset=[self.longitude_column_name, self.latitude_column_name])

        # create unique id for weather stations, hardcoded due to id issue in weather dataset
        unique_id_udf = udf(lambda x, y: '-'.join([x, y]))
        self.data = self.data.withColumn(
            self.id, unique_id_udf(col(self.latitude_column_name), col(self.longitude_column_name)))

        ds = super(NoaaGfsWeatherAccessory, self).filter(env, min_date, max_date)
        return ds.select(self.selected_columns + [self.id])

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        ds = super(NoaaGfsWeatherAccessory, self).filter(env, min_date, max_date)
        ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
            how='any', axis=0, subset=[self.longitude_column_name, self.latitude_column_name])

        # create unique id for weather stations, hardcoded due to id issue in weather dataset
        ds[self.id] = ds[self.latitude_column_name] + '-' + ds[self.longitude_column_name]

        return ds[self.selected_columns + [self.id]]

    def _get_mandatory_columns(self):
        """
        Get mandatory columns to select.

        :return: a list of column names.
        :rtype: list
        """
        return [self.time_column_name, self.latitude_column_name, self.longitude_column_name]

    def get_pandas_limit(self):
        """Get instance of pandas data load limit class."""
        return PandasDataLoadLimitToDay(self.start_date, self.end_date, limit=self.limit)

    def _to_spark_dataframe(self, activity_logger):
        """To spark dataframe.

        :param activity_logger: activity logger

        :return: SPARK dataframe
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        return descriptor.get_spark_dataframe(self)

    def _to_pandas_dataframe(self, activity_logger):
        """
        Get pandas dataframe.

        :param activity_logger: activity logger

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        return descriptor.get_pandas_dataframe(self)
