# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NOAA GFS weather."""

from datetime import datetime
from ._abstract_tabularopendataset import AbstractTabularOpenDataset
from .accessories.noaa_gfs_weather_accessory import NoaaGfsWeatherAccessory
from .dataaccess.dataset_partition_prep import prep_partition_year_month_day
from azureml.data import TabularDataset
from typing import List, Optional


class NoaaGfsWeather(AbstractTabularOpenDataset):
    """NOAA GFS forecast weather class."""

    def __init__(
            self,
            start_date: datetime = NoaaGfsWeatherAccessory.default_start_date,
            end_date: datetime = None,
            cols: Optional[List[str]] = None,
            dataset: TabularDataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the NoaaGfsWeather class.
        It can be initialized from parameters, or dataset alone, but can't from both.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = NoaaGfsWeatherAccessory(
            start_date=start_date,
            end_date=end_date,
            cols=cols,
            enable_telemetry=enable_telemetry)
        if dataset is not None:
            if start_date != NoaaGfsWeatherAccessory.default_start_date and \
                end_date is not None and \
                    cols is not None:
                raise ValueError('With enable_telemetry excluded, it is invalid to set dataset and other parameters \
at the same time! Please use either of them.')
            worker.update_dataset(dataset, enable_telemetry=enable_telemetry)
            self.worker = worker
            TabularDataset.__init__(self)
            self._definition = dataset._definition
            self._properties = dataset._properties
        else:
            AbstractTabularOpenDataset.__init__(self, worker=worker, partition_prep_func=prep_partition_year_month_day,
                                                fine_grain_timestamp='datetime')

    @staticmethod
    def get(dataset: TabularDataset, enable_telemetry: bool = True):
        """Get an instance of NoaaGfsWeather.

        :param dataset: input an instance of TabularDataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of NoaaGfsWeather.
        """
        gfs = NoaaGfsWeather(dataset=dataset, enable_telemetry=enable_telemetry)
        gfs._tags = dataset.tags
        if enable_telemetry:
            AbstractTabularOpenDataset.log_get_operation(gfs.worker)
        return gfs
