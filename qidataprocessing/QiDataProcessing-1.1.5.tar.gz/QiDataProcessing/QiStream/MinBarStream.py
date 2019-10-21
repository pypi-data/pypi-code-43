from QiDataProcessing.Core.FileHeader import FileHeader
from QiDataProcessing.Core.EnumBarType import EnumBarType
from QiDataProcessing.Core.BinaryReader import BinaryReader
from QiDataProcessing.Core.Bar import Bar
from QiDataProcessing.Core.CSharpUtils import QiCore
import datetime
import os
import os.path


class MinBarStream(object):
    BarLength = 88
    SimpleDayBarCountThreshold = 18

    def __init__(self, market, instrument_id, file_path):
        self._fileStream = None
        self._fileHeader = FileHeader()
        self._fileExtension = ".min"
        self._instrumentId = ""
        self._filePath = ""

        self._fileHeader.file_version = "MQ 1.0"
        self._fileHeader.period = 1
        self._fileHeader.market = market
        self._fileHeader.bar_type = EnumBarType.minute
        self._filePath = file_path

        if file_path.strip() == '':
            raise Exception("Invalid ConfigFilePath!")

        extension = os.path.splitext(file_path)[1].lower()
        if extension != self._fileExtension:
            raise Exception("Invalid file extension!")

        create_new = not os.path.exists(file_path)
        self._instrumentId = instrument_id.split('.')[0]
        self._fileStream = open(file_path, 'rb')

        if not create_new:
            if os.path.getsize(file_path) == 0:
                raise Exception("Invalid file length!")
            if self._fileHeader is None:
                self._fileHeader = FileHeader()
            reader = BinaryReader(self._fileStream)
            self._fileHeader.read(reader)

    def read_trading_day(self, bar_series, trading_day):
        if bar_series is None:
            raise Exception("bar_series为空")

        if not isinstance(trading_day, datetime.date):
            raise Exception("trading_day参数错误")

        read_count = 0
        trading_day = datetime.datetime(trading_day.year, trading_day.month, trading_day.day)
        reader = BinaryReader(self._fileStream)
        self._fileHeader.read(reader)
        if (trading_day < self._fileHeader.begin_trading_day) & (trading_day > self._fileHeader.end_trading_day):
            return False

        start_offset = -1
        count = -1
        data = self._fileHeader.trading_day_indices.try_get(trading_day, start_offset, count)
        start_offset = data[1]
        count = data[2]
        if data[0]:
            reader.stream.seek(start_offset, 0)
            while count > 0:
                bar = self.read_bar(reader)
                bar_series.append(bar)
                count -= 1
                read_count += 1

        return read_count > 0

    def read_trading_days(self, bar_series, begin_trading_day, end_trading_day):
        if bar_series is None:
            raise Exception("bar_series为空")

        if not isinstance(begin_trading_day, datetime.date):
            raise Exception("begin_time参数错误")

        if not isinstance(end_trading_day, datetime.date):
            raise Exception("end_time参数错误")

        begin_trading_day = datetime.datetime(begin_trading_day.year, begin_trading_day.month, begin_trading_day.day)
        end_trading_day = datetime.datetime(end_trading_day.year, end_trading_day.month, end_trading_day.day)

        if begin_trading_day > end_trading_day:
            raise Exception("end_trading_day must be larger than begin_trading_day")

        if begin_trading_day == end_trading_day:
            return self.read_trading_day(bar_series, begin_trading_day)

        read_count = 0
        reader = BinaryReader(self._fileStream)
        self._fileHeader.read(reader)
        if (end_trading_day < self._fileHeader.begin_trading_day) & (begin_trading_day > self._fileHeader.end_trading_day):
            return False

        if begin_trading_day < self._fileHeader.begin_trading_day:
            begin_trading_day = self._fileHeader.begin_trading_day

        if end_trading_day > self._fileHeader.end_trading_day:
            end_trading_day = self._fileHeader.end_trading_day

        start_offset = -1
        end_offset = -1
        start_count = 0
        end_count = 0
        data = self._fileHeader.trading_day_indices.get_trading_day_offsets(begin_trading_day, end_trading_day, start_offset, end_offset, start_count,
                                                                            end_count)
        start_offset = data[1]
        end_offset = data[2]
        end_count = data[4]
        if data[0]:
            end_offset += self.BarLength * end_count
            reader.stream.seek(start_offset, 0)
            while reader.stream.tell() < end_offset:
                bar = self.read_bar(reader)
                bar_series.append(bar)
                read_count += 1

        return read_count > 0

    @staticmethod
    def read_bar(reader):
        bar = Bar()
        bar.begin_time = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        bar.end_time = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        bar.trading_date = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        bar.open = reader.read_double()
        bar.close = reader.read_double()
        bar.high = reader.read_double()
        bar.low = reader.read_double()
        bar.pre_close = reader.read_double()
        bar.volume = reader.read_double()
        bar.turnover = reader.read_double()
        bar.open_interest = reader.read_double()
        # bar.IsCompleted = True

        return bar
