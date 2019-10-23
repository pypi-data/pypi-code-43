import datetime

from QiDataProcessing.BarProviderInfo import BarProviderInfo
from QiDataProcessing.Core.EnumBarType import EnumBarType
from QiDataProcessing.Core.TradingDayHelper import TradingDayHelper
from QiDataProcessing.TradingFrame.DateTimeSlice import DateTimeSlice
from QiDataProcessing.TradingFrame.TimeSlice import TimeSlice
from QiDataProcessing.TradingFrame.YfTimeHelper import YfTimeHelper


class BaseBarHelper:
    one_day = datetime.timedelta(days=1)

    def __init__(self):
        self.__templates = []

    @staticmethod
    def create_bar_provider_info(lst_time_slice, offset, interval, bar_type):
        bars = BaseBarHelper.create_time_slices(lst_time_slice, offset, interval, bar_type)
        if bars is None:
            return None

        bar_provider_info = BarProviderInfo()
        bar_provider_info.time_slices = bars
        bar_provider_info.bar_type = bar_type
        bar_provider_info.interval = interval
        bar_provider_info.offset = offset
        bar_provider_info.living_time = TimeSlice()
        bar_provider_info.living_time.begin_time = lst_time_slice[0].begin_time
        bar_provider_info.living_time.end_time = lst_time_slice[-1].end_time

    @staticmethod
    def create_time_slice(lst_time_slice, offset, interval, bar_type):
        if len(lst_time_slice) == 0:
            return None

        offset_time_span = datetime.timedelta(0, 0, offset)
        if bar_type == EnumBarType.second:
            interval_time_span = datetime.timedelta(seconds=interval)
        elif bar_type == EnumBarType.minute:
            interval_time_span = datetime.timedelta(minutes=interval)
        elif bar_type == EnumBarType.hour:
            interval_time_span = datetime.timedelta(hours=interval)
        elif bar_type == EnumBarType.day:
            day_time_slice = TimeSlice()
            day_time_slice.begin_time = lst_time_slice[0].begin_time
            day_time_slice.end_time = lst_time_slice[-1].end_time
            day_bars = [day_time_slice]
            return day_bars
        else:
            raise Exception("不支持的K线:" + str(bar_type))

        begin_time = lst_time_slice[0].begin_time
        bars = []
        if offset > 0:
            slice = TimeSlice()
            slice.begin_time = begin_time
            slice.end_time = begin_time + offset_time_span
            if slice.end_time.days() > 0:
                slice.end_time = slice.end_time = BaseBarHelper.one_day

            bars.append(slice)

            begin_time = slice.end_time

        end_time = begin_time
        diff_time_span = datetime.timedelta(0, 0, 0)
        for i in range(len(lst_time_slice)):
            ts = lst_time_slice[i]
            while True:
                tmp = ts.end_time - end_time
                if tmp < datetime.timedelta(0, 0, 0):
                    tmp = tmp + BaseBarHelper.one_day

                if (tmp + diff_time_span) < interval_time_span:
                    break

                end_time = end_time + (interval_time_span - diff_time_span)
                if end_time >= BaseBarHelper.one_day:
                    end_time = end_time - BaseBarHelper.one_day

                slice = TimeSlice()
                slice.begin_time = begin_time
                slice.end_time = end_time
                bars.append(slice)

                begin_time = end_time
                diff_time_span = datetime.timedelta(0, 0, 0)

            if i < (len(lst_time_slice) - 1):
                diff_time_span = diff_time_span + ts.end_time - end_time
                if diff_time_span < datetime.timedelta(0, 0, 0):
                    diff_time_span = diff_time_span + BaseBarHelper.one_day

                end_time = lst_time_slice[i + 1].begin_time

                if diff_time_span == datetime.timedelta(0, 0, 0):
                    begin_time = end_time
            else:
                if begin_time < ts.end_time:
                    slice = TimeSlice()
                    slice.begin_time = begin_time
                    slice.end_time = ts.end_time
                    bars.append(slice)

        return bars

    @staticmethod
    def create_date_time_slice(trading_day, lst_time_slices):
        pre_trading_day1 = TradingDayHelper.get_pre_trading_day(trading_day)
        pre_trading_day2 = pre_trading_day1 + datetime.timedelta(days=1)

        lst_date_time_slice = []
        for timeSlice in lst_time_slices:
            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = YfTimeHelper.join_date_time(trading_day, pre_trading_day1, pre_trading_day2, timeSlice.begin_time)
            date_time_slice.end_time = YfTimeHelper.join_date_time(trading_day, pre_trading_day1, pre_trading_day2, timeSlice.end_time)
            lst_date_time_slice.append(date_time_slice)
        return lst_date_time_slice

    @staticmethod
    def create_out_day_date_time_slice(begin_time, end_time, interval, bar_type):
        lst_date_time_slice = []
        lst_trading_days = TradingDayHelper.get_trading_days(begin_time, end_time)
        end_index = len(lst_trading_days) - 1
        start_index = end_index - interval + 1
        while (end_index >= 0) & (start_index >= 0):
            begin_date = lst_trading_days[start_index]
            end_date = lst_trading_days[end_index]

            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = begin_date
            date_time_slice.end_time = end_date
            lst_date_time_slice.insert(0, date_time_slice)

            end_index = end_index - interval
            start_index = end_index - interval + 1

        if end_index >= 0:
            begin_date = lst_trading_days[0]
            end_date = lst_trading_days[end_index]

            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = begin_date
            date_time_slice.end_time = end_date
            lst_date_time_slice.insert(0, date_time_slice)

        return lst_date_time_slice

    @staticmethod
    def create_in_day_date_time_slice(instrument_manager, instrument_id, begin_time, end_time, interval, bar_type, *instrument_ids):
        lst_all_date_time_slices = []
        begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
        end_trading_day = YfTimeHelper.get_trading_day(end_time)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                if dateTimeSlice.end_time >= begin_time:
                    lst_all_date_time_slices.append(dateTimeSlice)

        return lst_all_date_time_slices

    @staticmethod
    def create_day_date_time_slice(instrument_manager, instrument_id, trading_day, interval, bar_type, *instrument_ids):
        lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
        lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
        lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
        return lst_date_time_slices
