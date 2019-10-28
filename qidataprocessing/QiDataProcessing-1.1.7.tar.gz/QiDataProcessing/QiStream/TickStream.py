import datetime
import os
import sys

from QiDataProcessing.Core.BinaryReader import BinaryReader
from QiDataProcessing.Core.CSharpUtils import QiCore
from QiDataProcessing.Core.Tick import Tick
from QiDataProcessing.Core.TradingDayHelper import TradingDayHelper
from QiDataProcessing.Core.Quote import Quote


class TickStream:
    CFileHeaderLen = 44
    COrigDayLen = 8 * 4
    CTickOffset = CFileHeaderLen + COrigDayLen

    CPosTickLenV0 = 32
    CPosTickLenV1 = 40
    CPosTickPerLevelLen = 4 * 4
    CFileFlag = 1262700884  # ('K' << 24) + ('C' << 16) + ('I' << 8) + 'T'

    # VersionOld
    CReserveOld = 27
    CTickHeaderLenOld = 32
    CFileHeaderLenOld = 64

    def __init__(self, market, instrument_id, exchange_id, file_path):
        self.__file_path = ""
        self.__instrument_id = ""
        self.__exchange_id = ""
        self.__market = 0
        self.__first_read = False
        self.__b_new_version = True

        # Header
        self.__version = 1
        self.__quote_count = 0
        self.__multi_unit = 1000
        self.__trading_day = datetime.date
        self.__pre_close_price = 0.0
        self.__pre_settlement_price = 0.0
        self.__pre_interest = 0.0
        self.__up_limit = 0.0
        self.__down_limit = 0.0
        self.__open_price = 0.0
        self.__tick_count = 0
        self.__orig_day_count = 1
        self.__orig_day_offset = 0
        self.__tick_offset = 0

        # OrigDay
        self.__orig_days = []
        self.__orig_tick_offset = []

        # 18点后
        self.__pre_trading_day1 = datetime.date
        # 9点前
        self.__pre_trading_day2 = datetime.date

        self.__file_path = file_path
        self.__instrument_id = instrument_id
        self.__exchange_id = exchange_id
        self.__first_read = True
        self.__trading_day = datetime.date
        self.__market = market

    def read_by_count(self, tick_series, offset, count):
        if not os.path.exists(self.__file_path):
            _firstRead = True
            print("读取期货tick数据失败(" + self.__file_path + "),文件不存在")
            return False

        stream = open(self.__file_path, 'rb')
        reader = BinaryReader(stream)

        if self.__first_read:
            if self.read_header(reader):
                stream.seek(self.__orig_day_offset, 0)
                self.read_orig_days(reader)
            else:
                stream.seek(0, 0)
                self.read_old_header(reader)
            _firstRead = False

        if self.__b_new_version:
            if self.__version == 1:
                pos = self.__tick_offset + offset * (self.CPosTickLenV0 + self.__quote_count * self.CPosTickPerLevelLen)
                stream.seek(pos)
                if self.__quote_count == 1:
                    self.read_ticks1_v1_by_count(tick_series, reader, offset, count)
                else:
                    raise Exception("不支持" + str(self.__quote_count) + "档盘口")
            else:
                pos = self.__tick_offset + offset * (self.CPosTickLenV1 + self.__quote_count * self.CPosTickPerLevelLen)
                stream.seek(pos)
                if self.__quote_count == 1:
                    self.read_ticks1_v0_by_count(tick_series, reader, offset, count)
                else:
                    raise Exception("不支持" + str(self.__quote_count) + "档盘口")
        else:
            pos = self.CFileHeaderLenOld + offset * (self.CTickHeaderLenOld + self.__quote_count * 2 * 8)
            stream.seek(pos)
            if self.__quote_count == 1:
                self.read_old_ticks1_by_count(tick_series, reader, offset, count)
            else:
                raise Exception("不支持" + str(self.__quote_count) + "档盘口")
        stream.close()
        return True

    def read_by_time(self, tick_series, begin_time, end_time):
        if (begin_time == datetime.datetime) & end_time == datetime.datetime:
            return self.read_by_count(0, sys.maxsize)

        if end_time == datetime.datetime:
            end_time = datetime.datetime.max

        try:
            if not os.path.exists(self.__file_path):
                _firstRead = True
                print("读取期货tick数据失败(" + self.__file_path + "),文件不存在")
                return False

            stream = open(self.__file_path, 'rb')
            reader = BinaryReader(stream)

            if self.__first_read:
                if self.read_header(reader):
                    stream.seek(self.__orig_day_offset, 0)
                    self.read_orig_days(reader)
                else:
                    stream.seek(0, 0)
                    self.read_old_header(reader)
                _firstRead = False

            if self.__b_new_version:
                if self.__version == 1:
                    if self.__quote_count == 1:
                        self.read_ticks1_v1_by_time(tick_series, reader, begin_time, end_time)
                    else:
                        raise Exception("不支持" + str(self.__quote_count) + "档盘口")
                else:
                    if self.__quote_count == 1:
                        self.read_ticks1_v0_by_time(tick_series, reader, begin_time, end_time)
                    else:
                        raise Exception("不支持" + str(self.__quote_count) + "档盘口")
            else:
                pos = self.CFileHeaderLenOld
                stream.seek(pos)
                if self.__quote_count == 1:
                    self.read_old_ticks1_by_time(tick_series, reader, begin_time, end_time)
                else:
                    raise Exception("不支持" + str(self.__quote_count) + "档盘口")
            stream.close()
            return True
        except Exception as e:
            print(str(e))

        return False

    def read_header(self, reader):
        flag = reader.read_int32()
        if flag != self.CFileFlag:
            return False
        self.__orig_days.clear()
        self.__orig_tick_offset.clear()
        self.__orig_day_count = 0

        self.__version = reader.read_int16()
        self.__quote_count = reader.read_byte()

        tmp = 1
        multi = reader.read_byte()
        for i in range(0, multi):
            tmp = tmp * 10

        self.__multi_unit = tmp

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()

        self.__trading_day = datetime.date(year, month, day)

        self.__pre_close_price = reader.read_int32() / self.__multi_unit
        self.__pre_settlement_price = reader.read_int32() / self.__multi_unit
        self.__pre_interest = reader.read_int32()
        self.__up_limit = reader.read_int32() / self.__multi_unit
        self.__down_limit = reader.read_int32() / self.__multi_unit
        self.__open_price = reader.read_int32() / self.__multi_unit
        self.__tick_count = reader.read_int32()

        orig = reader.read_int16()
        self.__orig_day_count = (orig >> 12)
        self.__orig_day_offset = (orig & 0x0fff)
        self.__tick_offset = reader.read_int16()
        return True

    def read_old_header(self, reader):
        self.__orig_days.clear()
        self.__orig_tick_offset.clear()
        self.__orig_day_count = 0

        interval = reader.read_int16()
        bar_type = reader.read_int16()
        if (bar_type & 0xff) != 0:
            raise Exception("错误的tick数据文件标识")

        self.__b_new_version = False
        if ((bar_type >> 10) & 0x3) == 1:
            self.__multi_unit = 1000
        else:
            self.__multi_unit = 100

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()

        self.__trading_day = datetime.date(year, month, day)
        self.__pre_trading_day1 = TradingDayHelper.GetPreTradingDay(self.__trading_day)
        self.__pre_trading_day2 = self.__pre_trading_day1 + datetime.timedelta(days=1)

        self.__pre_close_price = reader.read_int32() / self.__multi_unit
        self.__pre_settlement_price = reader.read_int32() / self.__multi_unit
        self.__pre_interest = reader.read_int32()
        self.__up_limit = reader.read_int32() / self.__multi_unit
        self.__down_limit = reader.read_int32() / self.__multi_unit
        self.__open_price = reader.read_int32() / self.__multi_unit
        self.__tick_count = reader.read_int32()
        self.__quote_count = reader.read_byte()

        reader.read_bytes(self.CReserveOld)

    def read_orig_days(self, reader):
        for i in range(0, self.__orig_day_count):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()
            orig_tick_offset = reader.read_int32()

            orig_day = datetime.date(year, month, day)

            self.__orig_days.append(orig_day)
            self.__orig_tick_offset.append(orig_tick_offset)

    def read_ticks1_v1_by_count(self, tick_series, reader, offset, count):
        origin_index = 0
        for origin_index in range(0, len(self.__orig_tick_offset)):
            if offset < self.__orig_tick_offset[origin_index]:
                break
            origin_index = origin_index + 1

        origin_index = origin_index - 1
        if origin_index < 0:
            return

        orig_day = self.__orig_days[origin_index]
        next_orig_offset = 100000000
        if origin_index < len(self.__orig_tick_offset) - 1:
            next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

        tick_len = self.__tick_count - offset
        if tick_len < count:
            tick_len = tick_len
        else:
            tick_len = count

        for i in range(0, tick_len):
            tick = Tick()
            tick.market = self.__market,
            tick.open_price = self.__open_price,
            tick.pre_close_price = self.__pre_close_price,
            tick.instrument_id = self.__instrument_id,
            tick.exchange_id = self.__exchange_id,
            tick.pre_open_interest = self.__pre_interest,
            tick.pre_settlement_price = self.__pre_settlement_price,
            tick.up_limit = self.__up_limit,
            tick.drop_limit = self.__down_limit

            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            tick.local_time = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())

            tick.date_time = datetime.datetime(orig_day.year, orig_day.month, orig_day.day, hour, minute, second, milliseconds)
            tick.trading_day = self.__trading_day
            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            # quote = quote()
            # quote.ask_volume1 = reader.read_int32()
            # quote.bid_volume1 = reader.read_int32()
            # quote.ask_price1 = reader.read_int32() / self._multiUnit
            # quote.bid_price1 = reader.read_int32() / self._multiUnit
            # tick.quote = quote
            tick.AskVolume1 = reader.read_int32()
            tick.BidVolume1 = reader.read_int32()
            tick.AskPrice1 = reader.read_int32() / self.__multi_unit
            tick.BidPrice1 = reader.read_int32() / self.__multi_unit
            tick_series.append(tick)

            if i + offset >= next_orig_offset:
                origin_index = origin_index + 1
                if origin_index < len(self.__orig_days):
                    orig_day = self.__orig_days[origin_index]

                next_orig_offset = 10000000
                if origin_index < len(self.__orig_tick_offset) - 1:
                    next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

    def read_ticks1_v0_by_count(self, tick_series, reader, offset, count):
        origin_index = 0
        for origin_index in range(0, len(self.__orig_tick_offset)):
            if offset < self.__orig_tick_offset[origin_index]:
                break
            origin_index = origin_index + 1

        origin_index = origin_index - 1
        if origin_index < 0:
            return

        orig_day = self.__orig_days[origin_index]
        next_orig_offset = 100000000
        if origin_index < len(self.__orig_tick_offset) - 1:
            next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

        tick_len = self.__tick_count - offset
        if tick_len < count:
            tick_len = tick_len
        else:
            tick_len = count

        for i in range(0, tick_len):
            tick = Tick()
            tick.market = self.__market,
            tick.open_price = self.__open_price,
            tick.pre_close_price = self.__pre_close_price,
            tick.instrument_id = self.__instrument_id,
            tick.exchange_id = self.__exchange_id,
            tick.pre_open_interest = self.__pre_interest,
            tick.pre_settlement_price = self.__pre_settlement_price,
            tick.up_limit = self.__up_limit,
            tick.drop_limit = self.__down_limit

            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            tick.local_time = datetime.date
            tick.date_time = datetime.datetime(orig_day.year, orig_day.month, orig_day.day, hour, minute, second, milliseconds)
            tick.trading_day = self.__trading_day
            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            tick.quote = Quote()
            tick.quote.ask_volume1 = reader.read_int32()
            tick.quote.bid_volume1 = reader.read_int32()
            tick.quote.ask_price1 = reader.read_int32() / self.__multi_unit
            tick.quote.bid_price1 = reader.read_int32() / self.__multi_unit
            tick_series.append(tick)

            if i + offset >= next_orig_offset:
                origin_index = origin_index + 1
                if origin_index < len(self.__orig_days):
                    orig_day = self.__orig_days[origin_index]

                next_orig_offset = 10000000
                if origin_index < len(self.__orig_tick_offset) - 1:
                    next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

    def read_old_ticks1_by_count(self, tick_series, reader, offset, count):
        tick_len = self.__tick_count - offset
        if tick_len < count:
            tick_len = tick_len
        else:
            tick_len = count

        for i in range(0, tick_len):
            tick = Tick()
            tick.market = self.__market
            tick.open_price = self.__open_price
            tick.pre_close_price = self.__pre_close_price
            tick.instrument_id = self.__instrument_id
            tick.exchange_id = self.__exchange_id
            tick.pre_open_interest = self.__pre_interest
            tick.pre_settlement_price = self.__pre_settlement_price
            tick.up_limit = self.__up_limit
            tick.drop_limit = self.__down_limit

            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            tick.trading_day = self.__trading_day
            if hour < 7:
                tick.date_time = datetime.datetime(self.__pre_trading_day2.year, self.__pre_trading_day2.month,
                                                   self.__pre_trading_day2.day, hour, minute, second, milliseconds)
            elif hour < 18:
                tick.date_time = datetime.datetime(self.__trading_day.year, self.__trading_day.month,
                                                   self.__trading_day.day, hour, minute, second, milliseconds)
            else:
                tick.date_time = datetime.datetime(self.__pre_trading_day1.year, self.__pre_trading_day1.month,
                                                   self.__pre_trading_day1.day, hour, minute, second, milliseconds)

            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            quote = Quote()
            quote.ask_volume1 = reader.read_int32()
            quote.bid_volume1 = reader.read_int32()
            quote.ask_price1 = reader.read_int32() / self.__multi_unit
            quote.bid_price1 = reader.read_int32() / self.__multi_unit
            tick.quote = quote
            tick_series.append(tick)

    def read_ticks1_v1_by_time(self, tick_series, reader, begin_time, end_time):
        if len(self.__orig_days) == 0:
            return

        origin_index = 0
        orig_day = self.__orig_days[origin_index]
        next_orig_offset = sys.maxsize
        if origin_index < len(self.__orig_tick_offset) - 1:
            next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

        blk_len = self.CPosTickLenV1 + self.__quote_count * self.CPosTickPerLevelLen - 4

        for i in range(self.__tick_count):
            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            date_time = datetime.datetime(orig_day.year, orig_day.month, orig_day.day, hour, minute, second, milliseconds)

            if date_time > end_time:
                return

            if date_time < begin_time:
                if i >= next_orig_offset:
                    origin_index += 1

                    if origin_index < len(self.__orig_days):
                        orig_day = self.__orig_days[origin_index]

                    next_orig_offset = sys.maxsize
                    if origin_index < (len(self.__orig_tick_offset) - 1):
                        next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1
                reader.read_byte(blk_len)
                continue

            tick = Tick()
            tick.local_time = QiCore.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
            tick.market = self.__market,
            tick.open_price = self.__open_price,
            tick.pre_close_price = self.__pre_close_price,
            tick.instrument_id = self.__instrument_id,
            tick.exchange_id = self.__exchange_id,
            tick.pre_open_interest = self.__pre_interest,
            tick.pre_settlement_price = self.__pre_settlement_price,
            tick.up_limit = self.__up_limit,
            tick.drop_limit = self.__down_limit
            tick.date_time = date_time
            tick.trading_day = self.__trading_day
            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            quote = Quote()
            quote.ask_volume1 = reader.read_int32()
            quote.bid_volume1 = reader.read_int32()
            quote.ask_price1 = reader.read_int32() / self.__multi_unit
            quote.bid_price1 = reader.read_int32() / self.__multi_unit
            tick.quote = quote
            tick_series.append(tick)

            if i >= next_orig_offset:
                origin_index += 1
                if origin_index < len(self.__orig_days):
                    orig_day = self.__orig_days[origin_index]

                next_orig_offset = sys.maxsize
                if origin_index < len(self.__orig_tick_offset) - 1:
                    next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

    def read_ticks1_v0_by_time(self, tick_series, reader, begin_time, end_time):
        if len(self.__orig_days) == 0:
            return

        origin_index = 0
        orig_day = self.__orig_days[origin_index]
        next_orig_offset = sys.maxsize
        if origin_index < len(self.__orig_tick_offset) - 1:
            next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

        blk_len = self.CPosTickLenV1 + self.__quote_count * self.CPosTickPerLevelLen - 4

        for i in range(self.__tick_count):
            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            date_time = datetime.datetime(orig_day.year, orig_day.month, orig_day.day, hour, minute, second, milliseconds)

            if date_time > end_time:
                return

            if date_time < begin_time:
                if i >= next_orig_offset:
                    origin_index += 1

                    if origin_index < len(self.__orig_days):
                        orig_day = self.__orig_days[origin_index]

                    next_orig_offset = sys.maxsize
                    if origin_index < (len(self.__orig_tick_offset) - 1):
                        next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1
                reader.read_byte(blk_len)
                continue

            tick = Tick()
            tick.local_time = datetime.datetime.min
            tick.market = self.__market,
            tick.open_price = self.__open_price,
            tick.pre_close_price = self.__pre_close_price,
            tick.instrument_id = self.__instrument_id,
            tick.exchange_id = self.__exchange_id,
            tick.pre_open_interest = self.__pre_interest,
            tick.pre_settlement_price = self.__pre_settlement_price,
            tick.up_limit = self.__up_limit,
            tick.drop_limit = self.__down_limit
            tick.date_time = date_time
            tick.trading_day = self.__trading_day
            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            quote = Quote()
            quote.ask_volume1 = reader.read_int32()
            quote.bid_volume1 = reader.read_int32()
            quote.ask_price1 = reader.read_int32() / self.__multi_unit
            quote.bid_price1 = reader.read_int32() / self.__multi_unit
            tick.quote = quote
            tick_series.append(tick)

            if i >= next_orig_offset:
                origin_index += 1
                if origin_index < len(self.__orig_days):
                    orig_day = self.__orig_days[origin_index]

                next_orig_offset = sys.maxsize
                if origin_index < len(self.__orig_tick_offset) - 1:
                    next_orig_offset = self.__orig_tick_offset[origin_index + 1] - 1

    def read_old_ticks1_by_time(self, tick_series, reader, begin_time, end_time):
        blk_len = self.CPosTickLenV0 + self.__quote_count * self.CPosTickPerLevelLen - 4

        for i in range(self.__tick_count):
            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            millisecond = reader.read_byte()
            millisecond *= 10

            if hour < 7:
                tick_time = datetime.datetime(self.__pre_trading_day2.year, self.__pre_trading_day2.month,
                                              self.__pre_trading_day2.day, hour, minute, second, millisecond)
            elif hour < 18:
                tick_time = datetime.datetime(self.__trading_day.year, self.__trading_day.month,
                                              self.__trading_day.day, hour, minute, second, millisecond)
            else:
                tick_time = datetime.datetime(self.__pre_trading_day1.year, self.__pre_trading_day1.month,
                                              self.__pre_trading_day1.day, hour, minute, second, millisecond)

            if tick_time > end_time:
                return

            if tick_time < begin_time:
                reader.read_byte(blk_len)
                continue

            tick = Tick()
            tick.market = self.__market
            tick.open_price = self.__open_price
            tick.pre_close_price = self.__pre_close_price
            tick.instrument_id = self.__instrument_id
            tick.exchange_id = self.__exchange_id
            tick.pre_open_interest = self.__pre_interest
            tick.pre_settlement_price = self.__pre_settlement_price
            tick.up_limit = self.__up_limit
            tick.drop_limit = self.__down_limit
            tick.trading_day = self.__trading_day
            tick.date_time = tick_time

            tick.last_price = reader.read_int32() / self.__multi_unit
            tick.high_price = reader.read_int32() / self.__multi_unit
            tick.low_price = reader.read_int32() / self.__multi_unit
            tick.open_interest = reader.read_int32()
            tick.volume = reader.read_int32()
            tick.turnover = reader.read_double()
            quote = Quote()
            quote.ask_volume1 = reader.read_int32()
            quote.bid_volume1 = reader.read_int32()
            quote.ask_price1 = reader.read_int32() / self.__multi_unit
            quote.bid_price1 = reader.read_int32() / self.__multi_unit
            tick.quote = quote
            tick_series.append(tick)