from QiDataProcessing.Core.DateTimeToOffsetMap import DateTimeToOffsetMap
from QiDataProcessing.Core.EnumMarket import EnumMarket
from QiDataProcessing.Core.EnumBarType import EnumBarType
from QiDataProcessing.Core.CSharpUtils import QiCore
import datetime


class FileHeader:
    FileVersionSize = 8
    FileHeaderSize = 64
    FileHeaderTotalSize = 64 + 32 * 20 + 32 * 20

    def __init__(self):
        self._isDirty = False
        self._fileVersion = '1.0'
        self._market = EnumMarket.期货
        self._barType = EnumBarType.minute
        self._beginTime = datetime.datetime(1990, 1, 1)
        self._endTime = datetime.datetime(1990, 1, 1)
        self._beginTradingDay = datetime.datetime(1990, 1, 1)
        self._endTradingDay = datetime.datetime(1990, 1, 1)
        self._barCount = 0
        self._period = 1
        self._tradingDayIndices = None
        self._naturalDayIndices = None

    @property
    def file_version(self):
        return self._fileVersion

    @file_version.setter
    def file_version(self, value):
        self._fileVersion = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def bar_type(self):
        return self._barType

    @bar_type.setter
    def bar_type(self, value):
        self._barType = value

    @property
    def begin_time(self):
        return self._beginTime

    @begin_time.setter
    def begin_time(self, value):
        self._beginTime = value

    @property
    def end_time(self):
        return self._endTime

    @end_time.setter
    def end_time(self, value):
        self._endTime = value

    @property
    def begin_trading_day(self):
        return self._beginTradingDay

    @begin_trading_day.setter
    def begin_trading_day(self, value):
        self._beginTradingDay = value

    @property
    def end_trading_day(self):
        return self._endTradingDay

    @end_trading_day.setter
    def end_trading_day(self, value):
        self._endTradingDay = value

    @property
    def bar_count(self):
        return self._barCount

    @bar_count.setter
    def bar_count(self, value):
        self._barCount = value

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @property
    def trading_day_indices(self):
        return self._tradingDayIndices

    @trading_day_indices.setter
    def trading_day_indices(self, value):
        self._tradingDayIndices = value

    @property
    def natural_day_indices(self):
        return self._naturalDayIndices

    @natural_day_indices.setter
    def natural_day_indices(self, value):
        self._naturalDayIndices = value

    def __init__(self):
        self._tradingDayIndices = DateTimeToOffsetMap(self)
        self._naturalDayIndices = DateTimeToOffsetMap(self)

    def mark_as_dirty(self, value):
        self._isDirty = value

    def read(self, reader):
        reader.stream.seek(0, 0)
        self._fileVersion = reader.read_string()
        reader.stream.seek(self.FileVersionSize, 0)
        self._market = reader.read_int32()
        self._barType = reader.read_int32()
        self._period = reader.read_int32()
        self._beginTime = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._endTime = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._beginTradingDay = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._endTradingDay = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._barCount = reader.read_int32()
        reader.stream.seek(self.FileHeaderSize, 0)
        self._tradingDayIndices.read(reader)
        self._naturalDayIndices.read(reader)
        self.mark_as_dirty(False)
