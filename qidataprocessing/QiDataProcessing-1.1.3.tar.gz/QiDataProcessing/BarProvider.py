import datetime
import threading

from QiDataProcessing.BaseBarHelper import BaseBarHelper
from QiDataProcessing.Core.Bar import Bar
from QiDataProcessing.Core.EnumBarType import EnumBarType


class BarProvider:
    def __init__(self):
        self.__lst_date_time_slices = []
        self.__pos_time = 0
        self.__pos_bar = -1
        self.__last_tick = None
        self.__diff_time_span = datetime.timedelta(0, 0, 0)
        self.__trading_day = datetime.datetime(1990, 1, 1, 0, 0, 0)
        self.is_supplement_blank_bar = False
        self.enable_live = False
        self.change_state = 0
        self.instrument_id = ""
        self.interval = 0
        self.bar_type = EnumBarType.minute
        self.__bar_series = []
        self.lock = threading.RLock()

    def create_bar_provider_by_period(self, instrument_manager, instrument_id, begin_time, end_time, interval, bar_type, *instrument_ids):
        self.instrument_id = instrument_id
        self.interval = interval
        self.bar_type = bar_type
        if (bar_type == EnumBarType.second) | (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            self.__lst_date_time_slices = BaseBarHelper.create_in_day_date_time_slice(instrument_manager, instrument_id, begin_time, end_time, interval,
                                                                                      bar_type, *instrument_ids)
        elif bar_type == EnumBarType.day:
            self.__lst_date_time_slices = BaseBarHelper.create_out_day_date_time_slice(begin_time, end_time, interval, bar_type)
        else:
            raise Exception("不支持的K线类型")

    def create_bar_provider_by_trading_day(self, instrument_manager, instrument_id, trading_day, interval, bar_type, *instrument_ids):
        self.instrument_id = instrument_id
        self.interval = interval
        self.bar_type = bar_type
        self.__lst_date_time_slices = BaseBarHelper.create_day_date_time_slice(instrument_manager, instrument_id, trading_day, interval, bar_type,
                                                                               *instrument_ids)

    @property
    def is_end(self):
        return self.__pos_time >= len(self.__lst_date_time_slices)

    @property
    def bar_series(self):
        return self.__bar_series

    def add_bar(self, new_bar):
        if new_bar is None:
            self.change_state = 4
            return

        self.lock.acquire()
        if self.is_end:
            self.change_state = 4
            return
        result = self.__move_to(new_bar.begin_time)
        ir = result[0]
        index = result[1]
        if ir == -1:
            self.change_state = 4
            return
        bar_open_count = 0
        bar_close_count = 0
        while self.__pos_time < index:
            if self.__pos_bar == self.__pos_time:
                pass
            else:
                self.__pos_bar += 1

            self.__pos_time += 1
        if ir == 0:
            if self.__pos_bar == self.__pos_time:
                bar = self.bar_series[-1]
                bar.add_bar(new_bar)
            else:
                bar = Bar()
                bar.trading_date = new_bar.trading_date
                bar.open_bar_with_new_bar(new_bar)
                self.bar_series.append(bar)

                bar_open_count += 1

                # OnBarOpened(bar)

                self.__pos_bar += 1

                current_date_time_slice = self.__lst_date_time_slices[self.__pos_time]
                if new_bar.end_time >= current_date_time_slice.end_time:
                    bar_close_count += 1

                    self.bar_series[-1].close_bar(current_date_time_slice.end_time)
                    # (BarSeries.Last)

            if (bar_open_count == 0) & (bar_close_count == 0):
                self.change_state = 0
                return

            if bar_open_count > bar_close_count:
                self.change_state = 2
                return

            if bar_close_count > bar_open_count:
                self.change_state = 1
                return

            self.change_state = 3
        self.lock.release()

    def add_tick(self, tick):
        if tick is None:
            self.change_state = 4
            return

        turnover = 0
        volume = 0
        self.__trading_day = tick.TradingDay

        self.lock.acquire()
        # 第一个tick
        if self.__last_tick is not None:
            turnover = self.__last_tick.turnover
            volume = self.__last_tick.volume
        else:
            if self.enable_live:
                self.__diff_time_span = tick.DateTime - datetime.datetime.now()
            for bar in self.bar_series:
                if bar.trading_date == self.__trading_day:
                    turnover = turnover + bar.turnover
                    volume = volume + bar.volume

        if self.is_end:
            self.change_state = 4
            return

        result = self.__move_to(tick.date_time)  # 自动判断是否切换下个区间
        ir = result[0]
        index = result[1]
        if ir == -1:
            self.change_state = 4
            return

        self.__last_tick = tick

        bar_open_count = 0
        bar_close_count = 0
        while self.__pos_time < index:
            current_t = self.__lst_date_time_slices[self.__pos_time]

            if self.__pos_bar == self.__pos_time:
                bar_close_count += 1

                self.bar_series[-1].close_bar(current_t.end_time)
                # OnBarClosed(BarSeries.Last)
            else:
                # 20150628 去掉空Bar
                if self.is_supplement_blank_bar:
                    bar_open_count += 1
                    bar = Bar()
                    bar.begin_time = current_t.begin_time
                    if self.__pos_bar >= 0:
                        bar.close = bar.pre_close = bar.open = bar.high = bar.low = self.bar_series[-1].close
                        bar.open_interest = self.bar_series[-1].open_interest
                    elif self.__last_tick is not None:
                        if self.__last_tick.pre_settlement_price > 0:
                            bar.close = bar.pre_close = bar.open = bar.high = bar.low = self.__last_tick.pre_settlement_price
                        else:
                            bar.close = bar.pre_close = bar.open = bar.high = bar.low = self.__last_tick.pre_close_price

                        bar.open_interest = self.__last_tick.pre_open_interest

                    bar.trading_date = tick.trading_day
                    self.bar_series.append(bar)

                    bar_close_count += 1
                    self.bar_series[-1].close_bar(current_t.end_time)
                    # OnBarClosed(BarSeries.Last)
                self.__pos_bar += 1

            self.__pos_time += 1

        # 有效的
        if ir == 0:
            if self.__pos_bar == self.__pos_time:
                bar = self.bar_series[-1]
                bar.add_tick(tick)
                bar.turnover = bar.turnover + tick.turnover - turnover
                bar.volume = bar.volume + tick.volume - volume
            else:
                last_bar = self.bar_series[-1]
                bar = Bar()
                bar.trading_date = self.__trading_day
                bar.open_bar(self.__lst_date_time_slices[self.__pos_time].begin_time, tick, last_bar)
                if last_bar is not None:
                    bar.turnover = tick.turnover - turnover
                    bar.volume = tick.volume - volume
                else:
                    bar.turnover = tick.turnover
                    bar.volume = tick.volume

                self.bar_series.append(bar)

                bar_open_count += 1
                # OnBarOpened(bar)

                self.__pos_bar += 1

        if (bar_open_count == 0) & (bar_close_count == 0):
            self.change_state = 0
            return

        if bar_open_count > bar_close_count:
            self.change_state = 2
            return

        if bar_close_count > bar_open_count:
            self.change_state = 1
            return

        self.change_state = 3

    def __move_to(self, now):
        index = self.__pos_time

        # region -1 无效
        current_date_time_slice = self.__lst_date_time_slices[self.__pos_time]
        if now < current_date_time_slice.begin_time:
            return -1, index
        # endregion

        # region 1 下一个
        while index < len(self.__lst_date_time_slices) - 1:
            date_time_slice = self.__lst_date_time_slices[index]
            next_date_time_slice = self.__lst_date_time_slices[index + 1]

            ir = self.__is_current_date_time_slice(date_time_slice, next_date_time_slice, now)
            if ir == 0:
                return 0, index
            # 处理盘中休息的异常数据(一般不会出现这种情况)
            if ir == 2:
                index += 1
                return 0, index
            index += 1

        # 收盘以后的Tick处理
        bmy = self.__is_current_date_time_slice(self.__lst_date_time_slices[index], None, now)
        if bmy == 0:
            return 0, index

        index += 1

        # endregion

        return 1, index

    @staticmethod
    def __is_current_date_time_slice(current_date_time_slice, next_date_time_slice, date_time):
        if next_date_time_slice is not None:
            if current_date_time_slice.end_time < next_date_time_slice.begin_time:
                if (date_time > current_date_time_slice.end_time) & (date_time < next_date_time_slice.begin_time):
                    ta = date_time - current_date_time_slice.end_time
                    tb = next_date_time_slice.begin_time - date_time
                    if tb.total_seconds() < ta.total_seconds():
                        return 2
                    return 0

            if (current_date_time_slice.begin_time <= date_time) & (date_time < next_date_time_slice.begin_time):
                return 0
        else:
            # 收盘5秒内的tick都计算
            if (current_date_time_slice.begin_time <= date_time) & (date_time < (current_date_time_slice.end_time + datetime.timedelta(seconds=100))):
                return 0
        return 1
