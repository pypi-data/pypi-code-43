# -*- coding: utf-8 -*-
"""Wrappers around the Octopus Energy API swagger client"""
import re
from enum import Enum
from functools import partial
from datetime import datetime
from dataclasses import dataclass
from swagger_client import ApiClient, DefaultApi, Configuration


NUM_RESULTS = 25000
DATE_FMT = "%Y-%m-%dT%H:%M:%S%z"
R_DATE_FMT = re.compile(
    "([0-9]{4}-[0-9]{2}-[0-9]{2}T)"
    "([0-9]{2}:[0-9]{2}:[0-9]{2})"
    "(\+|\-)([0-9]{2}):([0-9]{2})"  # pylint: disable=W1401
)


@dataclass
class GasMeter:
    """Information uniquely identifying a gas meter"""

    mprn: str
    serial_number: str


@dataclass
class ElectricityMeter:
    """Information uniquely identifying an electricity meter"""

    mpan: str
    serial_number: str


class Period(Enum):
    """A time period used by the API"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"


class MeterQueryTool:
    """Query a Gas and Electricity meter using the API

    :param api_key: The API key
    :param gas_meter: A GasMeter
    :param electricity_meter: An ElectricityMeter
    """

    def __init__(self, api_key, gas_meter, electricity_meter):
        self.api = setup_api(api_key)
        self.gas_meter = gas_meter
        self.electricity_meter = electricity_meter

    def gas_consumption(self, period=None):
        """Get details on gas consumption

        >>> from minimock import Mock
        >>> DefaultApi.gas_meter_points_mprn_meters_serial_number_consumption_get = \
          Mock('DefaultApi.gas_meter_points_mprn_meters_serial_number_consumption_get')
        >>> Result = Mock("Result")
        >>> Result.results = []
        >>> DefaultApi.gas_meter_points_mprn_meters_serial_number_consumption_get \
          .mock_returns = Result
        >>> e = ElectricityMeter("1", "2")
        >>> g = GasMeter("3", "4")
        >>> tool = MeterQueryTool(1, g, e)
        >>> tool.gas_consumption()
        Called DefaultApi.gas_meter_points_mprn_meters_serial_number_consumption_get(
            '3',
            '4',
            page_size=25000)
        []

        :param period: a Period enum, otherwise defaults to half hourly info
        :return: a swagger_client.Consumption
        """
        query = partial(
            self.api.gas_meter_points_mprn_meters_serial_number_consumption_get,
            self.gas_meter.mprn,
            self.gas_meter.serial_number,
            page_size=NUM_RESULTS,
        )
        if period:
            query = partial(query, group_by=period.value)
        return _consumption_query(query)

    def electricity_consumption(self, period=None):
        """Get details on electricity consumption

        >>> from minimock import Mock
        >>> DefaultApi.electricity_meter_points_mpan_meters_serial_number_consumption_get \
          = Mock('DefaultApi.electricity_meter_points_mpan_meters_serial_number_consumption_get')
        >>> Result = Mock("Result")
        >>> Result.results = []
        >>> DefaultApi.electricity_meter_points_mpan_meters_serial_number_consumption_get \
          .mock_returns = Result
        >>> e = ElectricityMeter("1", "2")
        >>> g = GasMeter("3", "4")
        >>> tool = MeterQueryTool(1, g, e)
        >>> tool.electricity_consumption()
        Called DefaultApi.electricity_meter_points_mpan_meters_serial_number_consumption_get(
            '1',
            '2',
            page_size=25000)
        []

        :param period: a Period enum, otherwise defaults to half hourly info
        :return: an instance of swagger_client.Consumption
        """
        query = partial(
            self.api.electricity_meter_points_mpan_meters_serial_number_consumption_get,
            self.electricity_meter.mpan,
            self.electricity_meter.serial_number,
            page_size=NUM_RESULTS,
        )
        if period:
            query = partial(query, group_by=period.value)
        return _consumption_query(query)


def _consumption_query(query):
    """Handle issues a 'consumption' API query

    :param query: A function representing the query to issue
    """
    result = query().results
    for consumption in result:
        consumption.interval_end = _fix_date(consumption.interval_end)
        consumption.interval_start = _fix_date(consumption.interval_start)
    return result


def _fix_date(date):
    """Turn a date string into a datetime object

    >>> _fix_date("2018-05-19T23:10:01Z")
    datetime.datetime(2018, 5, 19, 23, 10, 1, tzinfo=datetime.timezone.utc)
    >>> _fix_date("2018-05-19T23:10:01+01:00")
    datetime.datetime(2018, 5, 19, 23, 10, 1, tzinfo=\
datetime.timezone(datetime.timedelta(0, 3600)))

    :param date: The date to fix
    """
    if date[-1] == "Z":
        date = date[:-1] + "+00:00"
    fixed_format = R_DATE_FMT.sub(r"\1\2\3\4\5", date)
    return datetime.strptime(fixed_format, DATE_FMT)


def setup_api(api_key):
    """Setup the Octopus Energy API

    >>> setup_api("mykey")
    <swagger_client.api.default_api.DefaultApi object at ...

    :param api_key: The API key"""
    conf = Configuration()
    conf.username = api_key
    return DefaultApi(ApiClient(conf))
