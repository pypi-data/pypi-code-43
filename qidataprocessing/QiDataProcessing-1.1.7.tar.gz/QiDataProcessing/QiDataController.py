import datetime
import math
import os
import sys

from dateutil.relativedelta import relativedelta

from QiDataProcessing.BarProvider import BarProvider
from QiDataProcessing.BaseBarHelper import BaseBarHelper
from QiDataProcessing.Core.Bar import Bar
from QiDataProcessing.Core.EnumBarType import EnumBarType
from QiDataProcessing.Core.EnumMarket import EnumMarket
from QiDataProcessing.Core.EnumRestoration import EnumRestoration
from QiDataProcessing.Core.TradingDayHelper import TradingDayHelper
from QiDataProcessing.Instrument.InstrumentManager import InstrumentManager
from QiDataProcessing.QiStream.DayBarStream import DayBarStream
from QiDataProcessing.QiStream.MinBarStream import MinBarStream
from QiDataProcessing.QiStream.TickStream import TickStream
from QiDataProcessing.TradingFrame.YfTimeHelper import YfTimeHelper


class QiDataController:
    def __init__(self, qi_data_directory):
        config_dir = os.path.split(os.path.realpath(__file__))[0] + "\\Config"
        instrument_manager = InstrumentManager()
        instrument_manager.load(config_dir, EnumMarket.期货)

        self.instrument_manager = instrument_manager
        self.__trading_day = qi_data_directory.trading_day

        self.__future_tick_path = qi_data_directory.future_tick
        self.__future_tick_cache_path = qi_data_directory.future_tick_cache
        self.__future_min_path = qi_data_directory.future_min
        self.__future_day_path = qi_data_directory.future_day

        self.__bar_series_map = {}
        self.__tick_series_map = {}

    def __load_today_tick_series(self, market, instrument_id, trading_date):
        path = self.__future_tick_cache_path
        tick_series = []
        try:
            file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
            file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
            if instrument_id.lower() != 'index':
                instrument = self.instrument_manager[instrument_id.split('.')[0]]
                tick_stream = TickStream(market, instrument_id, instrument.exchange_id, file_path)
                tick_stream.read_by_count(tick_series, 0, sys.maxsize)
        except Exception as e:
            print(str(e))

        return tick_series

    def __load_history_tick_series(self, market, instrument_id, trading_date):
        path = self.__future_tick_path
        tick_series = []
        try:
            file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
            file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
            if instrument_id.lower() != 'index':
                instrument = self.instrument_manager[instrument_id.split('.')[0]]
                tick_stream = TickStream(market, instrument_id, instrument.exchange_id, file_path)
                tick_stream.read_by_count(tick_series, 0, sys.maxsize)
        except Exception as e:
            print(str(e))

        return tick_series

    def load_min_bar_series(self, market, instrument_id, *trading_dates):
        path = self.__future_min_path
        bar_series = []
        try:
            if len(trading_dates) == 1:
                trading_date = trading_dates[0]

                file_path = os.path.join(path, trading_date.strftime('%Y%m'))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".min")
                if instrument_id.lower() != 'index':
                    min_bar_steam = MinBarStream(market, instrument_id, file_path)
                    min_bar_steam.read_trading_day(bar_series, trading_date)

            if len(trading_dates) == 2:
                begin_date = trading_dates[0]
                end_date = trading_dates[1]
                begin_month = datetime.datetime(begin_date.year, begin_date.month, 1)
                end_month = datetime.datetime(end_date.year, end_date.month, 1) + relativedelta(months=+1) + datetime.timedelta(days=-1)
                date = begin_month
                while date <= end_month:
                    file_path = os.path.join(path, date.strftime('%Y%m'))
                    file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".min")
                    min_bar_steam = MinBarStream(market, instrument_id, file_path)
                    min_bar_steam.read_trading_days(bar_series, begin_date, end_date)
                    date = date + relativedelta(months=+1)
        except Exception as e:
            print(str(e))

        return bar_series

    def load_day_bar_series(self, market, instrument_id, begin_date, end_date):
        path = self.__future_day_path
        bar_series = []
        try:
            begin_month = datetime.datetime(begin_date.year, begin_date.month, 1)
            end_month = datetime.datetime(end_date.year, end_date.month, 1) + relativedelta(months=+1) + datetime.timedelta(days=-1)
            date = begin_month
            while date <= end_month:
                file_path = os.path.join(path, date.strftime('%Y%m'))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".day")
                day_bar_steam = DayBarStream(market, instrument_id, file_path)
                day_bar_steam.read(bar_series, begin_date, end_date)
                date = date + relativedelta(months=+1)
        except Exception as e:
            print(str(e))

        return bar_series

    def load_tick_series(self, market, instrument_id, *trading_dates):
        if len(trading_dates) == 1:
            trading_date = trading_dates[0]
            if trading_date == self.__trading_day:
                return self.__load_today_tick_series(market, instrument_id, trading_date)
            return self.__load_history_tick_series(market, instrument_id, trading_date)
        else:
            begin_time = trading_dates[0]
            end_time = trading_dates[1]
            path = self.__future_tick_path
            all_ticks = []
            try:
                begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
                last_trading_day = YfTimeHelper.get_trading_day(end_time)
                if last_trading_day == self.__trading_day:
                    end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
                else:
                    end_trading_date = last_trading_day
                date = begin_trading_date
                while date <= end_trading_date:
                    file_path = os.path.join(path, date.strftime("%Y%m%D"))
                    file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
                    if instrument_id.lower() != "index":
                        instrument = self.instrument_manager[instrument_id.split('.')[0]]
                        tick_stream = TickStream(market, instrument_id, instrument.exchange_id, file_path)
                        tick_stream.read_by_time(all_ticks, begin_time, end_time)

                    date = date + datetime.timedelta(days=1)

                if end_trading_date != last_trading_day:
                    tick_series = self.load_tick_series(market, instrument_id, self.__trading_day)
                    all_ticks.extend(tick_series)
            except Exception as e:
                print(str(e))

            return all_ticks

    def get_tick_series_by_time(self, market, instrument_id, begin_time, end_time):
        if instrument_id not in self.__tick_series_map.keys():
            all_ticks = self.load_tick_series(market, instrument_id, begin_time, end_time)
            self.__tick_series_map[instrument_id] = all_ticks
        else:
            all_ticks = self.__tick_series_map[instrument_id]
        return all_ticks

    def get_tick_series_by_length(self, market, instrument_id, end_time, length):
        tick_series = []
        if instrument_id not in self.__tick_series_map.keys():
            lst_ticks = []
            trading_date = TradingDayHelper.get_last_trading_day(end_time)
            while len(lst_ticks) < length:
                temp_tick_series = self.load_tick_series(market, instrument_id, trading_date)
                for tick in temp_tick_series:
                    lst_ticks.insert(0, tick)
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
            i = len(lst_ticks) - length
            while i < len(lst_ticks):
                tick_series.append(lst_ticks[i])
            self.__tick_series_map[instrument_id] = tick_series
        else:
            tick_series = self.__tick_series_map[instrument_id]
        return tick_series

    def get_bar_series_by_time(self, market, instrument_id, interval, bar_type, begin_time, end_time, restore=EnumRestoration.不复权, *instrument_ids):
        bar_providers = []
        if instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[instrument_id]
        else:
            self.__bar_series_map[instrument_id] = bar_providers

        # 已经获取过直接返回
        bar_provider = None
        if len(bar_providers) > 0:
            bar_provider = next((data for data in bar_providers if (data.interval == interval) & (data.bar_type == bar_type)), None)
            if bar_provider is not None:
                return bar_provider.bar_series

        # 加载历史数据
        begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
        last_trading_day = YfTimeHelper.get_trading_day(end_time)
        if last_trading_day == self.__trading_day:
            end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
        else:
            end_trading_date = last_trading_day
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        if bar_type == EnumBarType.second:
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_time, end_trading_date, interval, bar_type,
                                                       *instrument_ids)
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_time, end_trading_date, interval, bar_type,
                                                       *instrument_ids)
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_type == EnumBarType.day:
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type,
                                                       *instrument_ids)
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, self.__trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        # 组装当日数据
        self.__combine_today_tick(bar_provider, market, end_time)

        bar_providers.append(bar_provider)
        if (bar_provider.bar_type == EnumBarType.second) | (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            lst_remove = []
            for bar in bar_provider.bar_series:
                if bar.end_time < begin_time:
                    lst_remove.append(bar)
                else:
                    break
            for bar in lst_remove:
                bar_provider.bar_series.remove(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            lst_remove = []
            for bar in bar_provider.bar_series:
                if bar.end_time < begin_trading_date:
                    lst_remove.append(bar)
                else:
                    break
            for bar in lst_remove:
                bar_provider.bar_series.remove(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        return bar_provider.bar_series

    def get_bar_series_by_length(self, market, instrument_id, interval, bar_type, max_length, end_time, restore=EnumRestoration.不复权, *instrument_ids):
        bar_providers = []
        if instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[instrument_id]
        else:
            self.__bar_series_map[instrument_id] = bar_providers

        # 已经获取过直接返回
        if len(bar_providers) > 0:
            bar_provider = next((data for data in bar_providers if (data.interval == interval) & (data.bar_type == bar_type)), None)
            if bar_provider is not None:
                return bar_provider.bar_series

        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        last_trading_day = YfTimeHelper.get_trading_day(end_time)
        if last_trading_day == self.__trading_day:
            end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
        else:
            end_trading_date = last_trading_day
        lst_date_time_slices_one_day = BaseBarHelper.create_day_date_time_slice(self.instrument_manager, instrument_id, end_trading_date, interval, bar_type,
                                                                                *instrument_ids)
        if len(lst_date_time_slices_one_day) > 0:
            n_one_day_count = len(lst_date_time_slices_one_day)
        else:
            n_one_day_count = 1

        n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))
        if bar_type == EnumBarType.day:
            n_trading_days = n_trading_days * interval
        else:
            n_trading_days = n_trading_days

        begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type,
                                                   *instrument_ids)
        if bar_provider.bar_type == EnumBarType.second:
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        if len(bar_provider.bar_series) < max_length:
            trading_date = begin_trading_date
            count = 0
            while count < 5:
                count += 1
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                if bar_provider.bar_type == EnumBarType.second:
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_date)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
                elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                    for bar in bar_series_min:
                        bar_provider.add_bar(bar)
                elif bar_provider.bar_type == EnumBarType.day:
                    begin_date = TradingDayHelper.get_pre_trading_day(trading_date, interval - 1)
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_trading_date)
                    trading_date = begin_date
                    for bar in bar_series_day:
                        bar_provider.add_bar(bar)
                else:
                    raise Exception("不支持的k线:" + str(bar_type))

                for bar in bar_provider.bar_series:
                    bar_series.insert(0, bar)

                if len(bar_series) >= max_length:
                    break

        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, self.__trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        # 组装当日数据
        self.__combine_today_tick(bar_provider, market, end_time)

        bar_providers.append(bar_provider)
        remove_length = len(bar_provider.bar_series) - max_length
        if remove_length > 0:
            del bar_provider.bar_series[0:remove_length]

        return bar_provider.bar_series

    def __combine_today_tick(self, bar_provider, market, end_time):
        date_time_slice = self.instrument_manager.get_living_date_time(self.__trading_day, bar_provider.instrument_id)
        if end_time > date_time_slice.begin_time:
            # 加载当日数据
            tick_series = self.__load_today_tick_series(market, bar_provider.instrument_id, self.__trading_day)

            if (bar_provider.bar_type == EnumBarType.second) | (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                for tick in tick_series:
                    if tick.date_time <= end_time:
                        bar_provider.add_tick(tick)
                        if tick.date_time == date_time_slice.BeginTime:  # 第1个的Tick包含集合竞价信息, 特殊处理
                            bar_provider.bar_series[-1].high = tick.high_price
                            bar_provider.bar_series[-1].open = tick.open_price
                            bar_provider.bar_series[-1].low = tick.low_price
            elif bar_provider.bar_type == EnumBarType.day:
                # // 大于1不组当日日线 和MQ一致(个人认为应该组)
                if bar_provider.interval > 1:
                    return

                if (tick_series is None) | (len(tick_series) == 0):
                    return

                first_tick = tick_series[0]
                temp_tick_series = list((data for data in tick_series if data.get('date_time') <= end_time))[-1]
                last_tick = temp_tick_series[-1]
                if (len(bar_provider.bar_series) == 0) | (bar_provider.bar_series[-1].trading_date != first_tick.trading_day):
                    bar = Bar()
                    bar.trading_date = first_tick.trading_day
                    if len(bar_provider.bar_series) == 0:
                        temp_bar = None
                    else:
                        temp_bar = bar_provider.bar_series[-1]
                    bar.open_bar(first_tick.trading_day, first_tick, temp_bar)
                    bar.turnover = first_tick.turnover
                    bar.volume = first_tick.volume
                    bar_provider.bar_series.append(bar)

                    if last_tick is None:
                        last_tick = first_tick
                    bar_provider.bar_series[-1].high = last_tick.high_price
                    bar_provider.bar_series[-1].low = last_tick.low_price
                    bar_provider.bar_series[-1].turnover = last_tick.turnover
                    bar_provider.bar_series[-1].volume = last_tick.volume
                    bar_provider.bar_series[-1].open_interest = last_tick.open_interest
                    bar_provider.bar_series[-1].end_time = last_tick.date_time
                    bar_provider.bar_series[-1].close = last_tick.last_price
                    bar_provider.bar_series[-1].trading_date = last_tick.trading_day

    def load_bar_series_by_date(self, market, instrument_id, interval, bar_type, begin_date, end_date, *instrument_ids):
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        begin_trading_date = YfTimeHelper.get_trading_day(begin_date)
        end_trading_date = YfTimeHelper.get_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type,
                                                   *instrument_ids)
        if bar_type == EnumBarType.second:
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_type == EnumBarType.day:
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        return bar_provider.bar_series

    def load_bar_series_by_length(self, market, instrument_id, interval, bar_type, max_length, end_date, *instrument_ids):
        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
        lst_date_time_slices_one_day = BaseBarHelper.create_day_date_time_slice(self.instrument_manager, instrument_id, end_trading_date, interval, bar_type,
                                                                                *instrument_ids)
        if len(lst_date_time_slices_one_day) > 0:
            n_one_day_count = len(lst_date_time_slices_one_day)
        else:
            n_one_day_count = 1

        n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))
        if bar_type == EnumBarType.day:
            n_trading_days = n_trading_days * interval
        else:
            n_trading_days = n_trading_days

        begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_period(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type,
                                                   *instrument_ids)
        if bar_provider.bar_type == EnumBarType.second:
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        if len(bar_provider.bar_series) < max_length:
            trading_date = begin_trading_date
            count = 0
            while count < 5:
                count += 1
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                if bar_provider.bar_type == EnumBarType.second:
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_date)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
                elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                    for bar in bar_series_min:
                        bar_provider.add_bar(bar)
                elif bar_provider.bar_type == EnumBarType.day:
                    begin_date = TradingDayHelper.get_pre_trading_day(trading_date, interval - 1)
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_trading_date)
                    trading_date = begin_date
                    for bar in bar_series_day:
                        bar_provider.add_bar(bar)
                else:
                    raise Exception("不支持的k线:" + str(bar_type))

                for bar in bar_provider.bar_series:
                    bar_series.insert(0, bar)

                if len(bar_series) >= max_length:
                    break

        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_day(self.instrument_manager, instrument_id, self.__trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        remove_length = len(bar_provider.bar_series) - max_length
        if remove_length > 0:
            del bar_provider.bar_series[0:remove_length]

        return bar_provider.bar_series

    def on_bar(self, bar):
        if bar.instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[bar.instrument_id]
            for bar_provider in bar_providers:
                bar_provider.add_bar(bar)
        else:
            return
