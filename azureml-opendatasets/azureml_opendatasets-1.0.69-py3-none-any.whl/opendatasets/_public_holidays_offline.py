# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public holiday."""

from datetime import datetime, date
import pandas as pd
from .accessories.public_holidays_offline_accessory import PublicHolidaysOfflineAccessory
from typing import List, Optional


class PublicHolidaysOffline:
    """Public holiday class."""

    def __init__(
            self,
            country_or_region: str = PublicHolidaysOfflineAccessory.default_country_or_region,
            start_date: datetime = PublicHolidaysOfflineAccessory.default_start_date,
            end_date: datetime = PublicHolidaysOfflineAccessory.default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the PublicHolidays class.
        It can be initialized from parameters.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        self.worker = PublicHolidaysOfflineAccessory(
            country_or_region=country_or_region,
            start_date=start_date,
            end_date=end_date,
            cols=cols,
            enable_telemetry=enable_telemetry)

    def to_pandas_dataframe(self):
        """Create a Pandas dataframe by executing the transformation pipeline defined by this Dataset definition.

        .. remarks::

            Return a Pandas DataFrame fully materialized in memory.

        :return: A Pandas DataFrame.
        :rtype: pandas.core.frame.DataFrame
        """
        return self.worker.to_pandas_dataframe()

    def to_spark_dataframe(self):
        """Create a Spark DataFrame that can execute the transformation pipeline defined by this Dataset definition.

        .. remarks::

            The Spark Dataframe returned is only an execution plan and does not actually contain any data,
            as Spark Dataframes are lazily evaluated.

        :return: A Spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        return self.worker.to_spark_dataframe()

    def is_holiday(self, target_date: date, country_code: str = "US") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        return self.worker.is_holiday(target_date, country_code)

    def is_holiday_by_country_or_region(self, target_date: date, country_or_region: str = "United States") -> bool:
        """
        Detect a date is a holiday or not.

        :param target_date: The date which needs to be check.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: Whether the target_date is a holiday or not. True or False.
        """
        return self.worker.is_holiday_by_country_or_region(target_date, country_or_region)

    def get_holidays_in_range(self, start_date: date, end_date: date, country_code: str = "US") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_code: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        return self.worker.get_holidays_in_range(start_date, end_date, country_code)

    def get_holidays_in_range_by_country_or_region(self, start_date: date, end_date: date,
                                                   country_or_region: str = "United States") -> pd.DataFrame:
        """
        Get a list of holiday infomation base on the given date range.

        :param start_date: The start date of the date range.
        :param end_date: The end date of the date range.
        :param country_or_region: Indicate which country/region's holiday infomation will be used for the check.
        :return: A DataFrame which contains the holidays in the target date range.
        """
        return self.worker.get_holidays_in_range_by_country_or_region(start_date, end_date, country_or_region)
