import datetime
import re

from QiDataProcessing.Core.EnumExchange import EnumExchange
from QiDataProcessing.Core.EnumMarket import EnumMarket
from QiDataProcessing.Instrument.FutureManager import FutureManager
from QiDataProcessing.TradingFrame.DateTimeSlice import DateTimeSlice
from QiDataProcessing.TradingFrame.TimeSlice import TimeSlice
from QiDataProcessing.TradingFrame.TradingFrameManager import TradingFrameManager
from QiDataProcessing.TradingFrame.YfTimeHelper import YfTimeHelper


class InstrumentManager:
    FuMainId = "9999"
    FuCurMonthId = "9998"
    FuNextMonthId = "9997"
    FuNextQuarterId = "9996"
    FuNNextQuarterId = "9995"
    FuIndexId = "9990"

    def __init__(self):
        self.__all_instruments = {}
        self.__all_exchanges = {}
        self.__all_products = {}
        self.__trading_frame_manager = TradingFrameManager()

    def __getitem__(self, item):
        if item in self.__all_instruments.keys():
            return self.__all_instruments[item]
        return None

    def has_instrument(self, instrument_id):
        return instrument_id in self.__all_instruments.keys()

    @property
    def all_instruments(self):
        return self.__all_instruments

    def get_exchange_by_instrument_id(self, instrument_id):
        instrument = self.__all_instruments[instrument_id]
        if instrument is not None:
            return self.get_exchange(instrument.exchange_id)

        return None

    def get_exchange(self, exchange):
        if isinstance(exchange, str):
            if exchange in self.__all_exchanges.keys():
                return self.__all_exchanges[exchange]
        if isinstance(exchange, EnumExchange):
            if exchange == EnumExchange.中金所:
                return self.get_exchange("CFFEX")
            elif exchange == EnumExchange.大商所:
                return self.get_exchange("DCE")
            elif exchange == EnumExchange.上期所:
                return self.get_exchange("SHFE")
            elif exchange == EnumExchange.郑商所:
                return self.get_exchange("CZCE")
            elif exchange == EnumExchange.上证所:
                return self.get_exchange("SH")
            elif exchange == EnumExchange.深交所:
                return self.get_exchange("SZ")
            else:
                raise Exception("非法的交易所代码:" + str(exchange))
        return None

    @property
    def all_exchanges(self):
        return self.__all_exchanges

    def clear(self):
        self.__all_instruments.clear()
        self.__all_exchanges.clear()

    def __get_trading_time(self, trading_day, instrument_id):
        instrument = self[instrument_id]
        if (instrument is not None) & (self.__trading_frame_manager is not None):
            product_id = InstrumentManager.get_product_id(instrument_id)
            return self.__trading_frame_manager.get_trading_time_slices(trading_day, instrument.market, instrument.exchange_id, product_id)

        if instrument is None:
            product_id = InstrumentManager.get_product_id(instrument_id)
            if (product_id == "") | (product_id[0] == "."):
                return None

            product = self.get_future_product(product_id)
            if product is None:
                return None

            if (product.all_slice is not None) & (len(product.all_slie) > 0):
                return product.all_slice

            exchange = self.get_exchange(product.exchange_id)

            if exchange is not None:
                return exchange.all_slice

            return None
        else:
            if instrument.market == EnumMarket.期货:
                future = instrument
                if future is None:
                    return None

                product = self.get_future_product(future.product_id)
                if product is None:
                    return None

                if (product.all_slice is not None) & (len(product.all_slie) > 0):
                    return product.all_slice

                exchange = self.get_exchange(product.exchange_id)

                if exchange is not None:
                    return exchange.all_slice

                return None

    def get_trading_time(self, trading_day, instrument_id, *instrument_ids):
        source = self.__get_trading_time(trading_day, instrument_id)
        if instrument_ids is None:
            return source
        if len(instrument_ids) == 0:
            return source

        for intersect_instrument_id in instrument_ids:
            target = self.__get_trading_time(trading_day, intersect_instrument_id)
            source = InstrumentManager.intersect(source, target)

        return source

    @staticmethod
    def intersect(source, target):
        lst_time_slices = []
        lst_source = []
        lst_target = []
        today = datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        for temp_time_slice in source:
            lst_source.append(YfTimeHelper.get_date_time_by_trading_day(today, temp_time_slice.begin_time))
            lst_source.append(YfTimeHelper.get_date_time_by_trading_day(today, temp_time_slice.end_time))

        for temp_time_slice in target:
            lst_target.append(YfTimeHelper.get_date_time_by_trading_day(today, temp_time_slice.begin_time))
            lst_target.append(YfTimeHelper.get_date_time_by_trading_day(today, temp_time_slice.end_time))

        i = 0
        j = 0
        while (i < len(lst_source) - 1) & (j < len(lst_target) - 1):
            source_begin_time = lst_source[i]
            source_end_time = lst_source[i + 1]
            target_begin_time = lst_target[j]
            target_end_time = lst_target[j + 1]

            if (source_begin_time < target_begin_time) & (source_end_time < target_begin_time):
                i += 2
                continue

            if (target_begin_time < source_begin_time) & (target_end_time < source_begin_time):
                j += 2
                continue

            if source_begin_time >= target_begin_time:
                begin_time = source_begin_time
            else:
                begin_time = target_begin_time

            if source_end_time >= target_end_time:
                end_time = target_end_time
            else:
                end_time = source_end_time

            temp_time_slice = TimeSlice()
            temp_time_slice.begin_time = datetime.timedelta(hours=begin_time.hour, minutes=begin_time.minute, seconds=begin_time.second)
            temp_time_slice.end_time = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
            lst_time_slices.append(temp_time_slice)

            if source_end_time < target_end_time:
                i += 2
                continue
            if source_end_time > target_end_time:
                j += 2
                continue

            i += 2
            j += 2

        return lst_time_slices

    def get_future_product(self, product_id):
        if product_id in self.__all_products.keys():
            return self.__all_products[product_id]

        return None

    def __merge(self, future_manager):
        for future_id in future_manager.all_instruments.keys():
            if future_id not in self.__all_instruments.keys():
                self.__all_instruments[future_id] = future_manager.all_instruments[future_id]

        for exchange_id in future_manager.all_exchanges.keys():
            if exchange_id not in self.__all_exchanges.keys():
                self.__all_exchanges[exchange_id] = future_manager.all_exchanges[exchange_id]

        for product_id in future_manager.all_products.keys():
            if product_id not in self.__all_products.keys():
                self.__all_products[product_id] = future_manager.all_products[product_id]

    def load(self, config_directory, market):
        try:
            self.__trading_frame_manager.load(config_directory)

            if market == EnumMarket.期货:
                future_manager = FutureManager()
                future_manager.load(config_directory)
                self.__merge(future_manager)
                return True
        except Exception as e:
            self.clear()
            print(str(e))

        return False

    @staticmethod
    def get_market_by_exchange_id(exchange):
        if exchange == EnumExchange.大商所:
            return EnumMarket.期货
        if exchange == EnumExchange.上期所:
            return EnumMarket.期货
        if exchange == EnumExchange.郑商所:
            return EnumMarket.期货
        if exchange == EnumExchange.中金所:
            return EnumMarket.期货
        if exchange == EnumExchange.上证所:
            return EnumMarket.股票
        if exchange == EnumExchange.深交所:
            return EnumMarket.股票
        if exchange == EnumExchange.新交所:
            return EnumMarket.外盘

        return EnumMarket.期货

    def is_normal_open_close_time(self, instrument_id):
        instrument = self[instrument_id]
        if instrument is None:
            return True

        if instrument.market == EnumMarket.期货:
            future = instrument
            if future is None:
                return True

            product = self.get_future_product(future.product_id)
            if product is None:
                return None

            if (product.all_slice is not None) & (len(product.all_slice) > 0):
                return False

        return True

    def get_living_time(self, trading_day, instrument_id):
        instrument = self[instrument_id]
        if (instrument is not None) & (self.__trading_frame_manager is not None):
            product_id = InstrumentManager.get_product_id(instrument_id)
            return self.__trading_frame_manager.get_living_time(trading_day, instrument.market, instrument.exchange_id, product_id)

        if instrument is None:
            product_id = InstrumentManager.get_product_id(instrument_id)
            if (product_id == "") | (product_id[0] == "."):
                return None

            product = self.get_future_product(product_id)
            if product is None:
                return None

            if (product.all_slice is not None) & (len(product.all_slie) > 0):
                time_slice = TimeSlice()
                time_slice.begin_time = product.all_slice[0].begin_time
                time_slice.end_time = product.all_slice[-1].end_time
                return time_slice

            exchange = self.get_exchange(product.exchange_id)

            if exchange is not None:
                time_slice = TimeSlice()
                time_slice.begin_time = exchange.all_slice[0].begin_time
                time_slice.end_time = exchange.all_slice[-1].end_time
                return time_slice

            return None
        else:
            if instrument.market == EnumMarket.期货:
                future = instrument
                if future is None:
                    return None

                product = self.get_future_product(future.product_id)
                if product is None:
                    return None

                if (product.all_slice is not None) & (len(product.all_slie) > 0):
                    time_slice = TimeSlice()
                    time_slice.begin_time = product.all_slice[0].begin_time
                    time_slice.end_time = product.all_slice[-1].end_time
                    return time_slice

                exchange = self.get_exchange(product.exchange_id)

                if exchange is not None:
                    time_slice = TimeSlice()
                    time_slice.begin_time = exchange.all_slice[0].begin_time
                    time_slice.end_time = exchange.all_slice[-1].end_time
                    return time_slice

                return None

    @staticmethod
    def get_product_id(instrument_id):
        return re.sub(r"\d", "", instrument_id, 0)

    def get_living_date_time(self, trading_day, instrument_id):
        time_slice = self.get_living_time(trading_day, instrument_id)
        date_time_slice = DateTimeSlice()
        date_time_slice.begin_time = YfTimeHelper.get_date_time_by_trading_day(trading_day, time_slice.begin_time)
        date_time_slice.end_time = YfTimeHelper.get_date_time_by_trading_day(trading_day, time_slice.end_time)
        return date_time_slice

#
# instrument_manager = InstrumentManager()
#
# config_dir = "D:\WorkSpace\CarlSnow\Python\QiDataProcessing\QiDataProcessing\Config"
# instrument_manager.load(config_dir, EnumMarket.期货)
# for instrument_id in instrument_manager.all_instruments.keys():
#     print(instrument_manager.all_instruments[instrument_id].to_string())
#
# for exchange_id in instrument_manager.all_exchanges.keys():
#     print(exchange_id)
#
# instrument_id = "IF9999"
# print("GetItem:" + instrument_manager[instrument_id].to_string())
# print("HasInstrument:" + str(instrument_manager.has_instrument(instrument_id)))
# #
# exchange_id = "CFFEX"
# exchange = instrument_manager.get_exchange(exchange_id)
# print("GetExchangeById:" + str(exchange))
#
# exchange = instrument_manager.get_exchange(EnumExchange.中金所)
# print("GetExchangeByEnum:" + str(exchange))
#
# instrument_id = "ag9999"
# trading_day = datetime.datetime(2019, 10, 10)
# lst_time_slice = instrument_manager.get_trading_time(trading_day, instrument_id)
# print("get_trading_time:")
# for time_slice in lst_time_slice:
#     print(time_slice.to_string())
#
# product = instrument_manager.get_future_product("IF")
# print("get_future_product:" + product.to_string())
#
# time_slice = instrument_manager.get_living_time(trading_day, instrument_id)
# print("get_living_time:" + time_slice.to_string())
#
# product_id = instrument_manager.get_product_id("IF9999")
# print("get_product_id:" + product_id)
#
# date_time_slice = instrument_manager.get_living_date_time(trading_day, instrument_id)
# print("get_living_date_time:" + date_time_slice.begin_time.strftime('%Y/%m/%d %H:%M:%S') + "-" + date_time_slice.end_time.strftime('%Y/%m/%d %H:%M:%S'))
