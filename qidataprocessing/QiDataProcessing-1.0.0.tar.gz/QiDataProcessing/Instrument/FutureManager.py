import datetime
import os
import xml
import xml.dom.minidom

from QiDataProcessing.Core.Exchange import Exchange
from QiDataProcessing.Core.FutureProduct import FutureProduct
from QiDataProcessing.Instrument.Future import Future
from QiDataProcessing.TradingFrame.TradingFrameHelper import TradingFrameHelper


class FutureManager:
    FileName = "future.xml"

    def __init__(self):
        self.__all_exchanges = {}
        self.__all_products = {}
        self.__all_futures = {}
        self.__is_loaded = False
        self.__path = ""

    @property
    def all_exchanges(self):
        return self.__all_exchanges

    @property
    def all_products(self):
        return self.__all_products

    @property
    def all_instruments(self):
        return self.__all_futures

    def __getitem__(self, item):
        if item.id in self.__all_futures.keys():
            return self.__all_futures[item.id]
        return None

    def load(self, config_directory):
        if not self.__is_loaded:
            try:
                self.__path = os.path.join(config_directory, self.FileName)
                if os.path.exists(self.__path):
                    pass
                else:
                    print("未找到配置文件:" + self.__path)
                _root = xml.dom.minidom.parse(self.__path).documentElement
                exchange_nodes = _root.getElementsByTagName('Exchange')
                for exchange_node in exchange_nodes:
                    self.__read_exchange(exchange_node)

                self.__is_loaded = True
            except Exception as e:
                print(str(e))

    def __read_exchange(self, exchange_node):
        exchange = Exchange()
        exchange.exchange_id = exchange_node.getAttribute('id')
        exchange.exchange_name = exchange_node.getAttribute('name')

        trading_time_nodes = exchange_node.getElementsByTagName('TradingTime')
        trading_time = self.get_node_value(trading_time_nodes[0])
        exchange.all_slice = TradingFrameHelper.parse_time_slice(trading_time)
        # trading_time_arr = trading_time.split(',')
        # count = len(trading_time_arr) / 2
        # for i in range(int(count)):
        #     time_slice = TimeSlice()
        #     time_slice.begin_time = TradingFrameHelper.str_pares_timedelta(trading_time_arr[i * 2])
        #     time_slice.end_time = TradingFrameHelper.str_pares_timedelta(trading_time_arr[i * 2 + 1])
        #
        #     exchange.all_slice.append(time_slice)

        open_time_nodes = exchange_node.getElementsByTagName('OpenTime')
        open_timedelta = TradingFrameHelper.str_pares_timedelta(self.get_node_value(open_time_nodes[0]))
        exchange.open_time = datetime.date.today() + open_timedelta

        close_time_nodes = exchange_node.getElementsByTagName('CloseTime')
        close_timedelta = TradingFrameHelper.str_pares_timedelta(self.get_node_value(close_time_nodes[0]))
        exchange.close_time = datetime.date.today() + close_timedelta

        self.__add_exchange(exchange)

        product_nodes = exchange_node.getElementsByTagName('Product')
        for product_node in product_nodes:
            self.__read_product(product_node, exchange.exchange_id)

    def __read_product(self, product_node, exchange_id):
        product = FutureProduct()
        product.product_id = product_node.getAttribute('id')
        product.product_name = product_node.getAttribute('name')
        product.exchange_id = exchange_id

        if product.product_id != "":
            self.__add_product(product)

        future_nodes = product_node.getElementsByTagName('Future')
        for future_node in future_nodes:
            future = self.__read_future(future_node)
            future_id = future.id
            if (future_id.find("9995") > 0) | (future_id.find("9996") > 0) | (future_id.find("9997") > 0) | (future_id.find("9998") > 0) | (
                    future_id.find("9999") > 0):
                future.real_future = future

            if future.id != "":
                future.exchange_id = product.exchange_id
                future.product_id = product.product_id

                self.__add_future(future)

    def __read_future(self, future_node):
        future = Future()
        future.id = future_node.getAttribute('id')
        future.name = future_node.getAttribute('name')

        product_id_nodes = future_node.getElementsByTagName('ProductID')
        future.product_id = self.get_node_value(product_id_nodes[0])

        exchange_id_nodes = future_node.getElementsByTagName('ExchangeID')
        future.exchange_id = self.get_node_value(exchange_id_nodes[0])

        open_date_nodes = future_node.getElementsByTagName('OpenDate')
        future.open_date = datetime.datetime.strptime(self.get_node_value(open_date_nodes[0]), '%Y/%m/%d %H:%M:%S')

        expire_date_nodes = future_node.getElementsByTagName('ExpireDate')
        future.expire_date = datetime.datetime.strptime(self.get_node_value(expire_date_nodes[0]), '%Y/%m/%d %H:%M:%S')

        long_margin_ratio_nodes = future_node.getElementsByTagName('LongMarginRatio')
        future.long_margin_ratio = float(self.get_node_value(long_margin_ratio_nodes[0]))

        short_margin_ratio_nodes = future_node.getElementsByTagName('ShortMarginRatio')
        future.short_margin_ratio = float(self.get_node_value(short_margin_ratio_nodes[0]))

        volume_multiple_nodes = future_node.getElementsByTagName('VolumeMultiple')
        future.volume_multiple = int(self.get_node_value(volume_multiple_nodes[0]))

        price_tick_nodes = future_node.getElementsByTagName('PriceTick')
        future.price_tick = float(self.get_node_value(price_tick_nodes[0]))

        return future

    @staticmethod
    def get_node_value(node):
        return node.firstChild.data

    def __add_exchange(self, exchange):
        if exchange.exchange_id in self.__all_exchanges.keys():
            return

        self.__all_exchanges[exchange.exchange_id] = exchange

        # print(exchange.to_string())

    def __add_product(self, product):
        if product.product_id in self.__all_products.keys():
            return

        self.__all_products[product.product_id] = product

        # print(product.to_string())

    def __add_future(self, future):
        if future is None:
            return

        if future.id in self.__all_futures.keys():
            return

        self.__all_futures[future.id] = future

        # print(future.to_string())

# future_manager = FutureManager()
# config_dir = "D:\WorkSpace\CarlSnow\Python\QiDataProcessing\QiDataProcessing\Config"
# future_manager.load(config_dir)
# for data in future_manager.all_instruments.values():
#     print(data.to_string())
