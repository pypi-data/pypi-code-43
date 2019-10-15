import datetime
import os

from QiDataProcessing.Core.Bar import Bar
from QiDataProcessing.Core.BinaryReader import BinaryReader


class DayBarStream(object):
    CFileHeaderLen = 64
    CBarLen = 12 * 4
    CReserve = 48
    CPosEnd = 8

    def __init__(self, market, instrument_id, file_path):
        self._filePath = ""
        self._instrumentId = ""
        self._tickCount = 0
        self._bValid = False
        self._firstRead = False
        self._beginDate = datetime.date
        self._endDate = datetime.date

        self._instrumentId = instrument_id.split('.')[0]
        self._filePath = file_path
        self._firstRead = True
        self._bValid = False
        self._tickCount = 0

    def read(self, bar_series, begin_date, end_date):
        try:
            if not os.path.exists(self._filePath):
                self._firstRead = True
                self._bValid = False

                print("读取期货日k线失败(" + self._filePath + "),文件不存在")

                return False

            stream = open(self._filePath, 'rb')
            length = os.path.getsize(self._filePath)
            if (length - self.CFileHeaderLen) % self.CBarLen != 0:
                raise Exception("日k线文件被破坏，数据出错")

            reader = BinaryReader(stream)

            pos = self.CFileHeaderLen
            if self._firstRead:
                self.read_header(reader)
                pos -= self.CFileHeaderLen

            reader.stream.seek(pos, 1)
            self.read_bars(reader, bar_series, begin_date, end_date)
            self._bValid = True
            return True
        except Exception as e:
            self._firstRead = True
            self._bValid = False
            print("读取期货日k线失败(" + self._filePath + ")")
        finally:
            pass

        return False

    def read_header(self, reader):
        interval = reader.read_int16()
        bar_type = reader.read_int16()
        if (bar_type != 4) | (interval != 1):
            print("错误的日k线文件标识")

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()
        self._beginDate = datetime.datetime(year, month, day)

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()
        self._endDate = datetime.datetime(year, month, day)

        if (self._beginDate == datetime.datetime.max) | (self._endDate == datetime.datetime.max) | (
                self._beginDate > self._endDate):
            raise Exception("非法的日k线文件")

        self._tickCount = reader.read_int32()
        length = os.path.getsize(self._filePath)
        if self._tickCount != int(((length - self.CFileHeaderLen) / self.CBarLen)):
            raise Exception("日k线文件被破坏，数据出错")

        reader.stream.seek(self.CReserve, 1)

        self._firstRead = False

    def read_bars(self, reader, bar_series, begin_date, end_date):
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        i = 0
        for i in range(0, self._tickCount):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()
            reader.stream.seek(self.CBarLen - 4, 1)
            dt = datetime.datetime(year, month, day)
            if dt >= begin_date:
                reader.stream.seek(-self.CBarLen, 1)
                break

        for index in range(i, self._tickCount):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()

            dt = datetime.datetime(year, month, day)

            if dt > end_date:
                break

            bar = Bar()
            bar.begin_time = dt
            bar.end_time = dt
            bar.open = reader.read_int32() / 1000.0
            bar.close = reader.read_int32() / 1000.0
            bar.high = reader.read_int32() / 1000.0
            bar.low = reader.read_int32() / 1000.0
            bar.pre_close = reader.read_int32() / 1000.0
            bar.volume = reader.read_double()
            bar.turnover = reader.read_double()
            bar.open_interest = reader.read_double()
            # bar.IsCompleted = True
            bar.trading_date = dt

            bar_series.append(bar)
