#from .cybos import CybosPlusStockChart
from .yahoo import YahooEvents, YahooStockChart
from .naver import NaverEvents, NaverStockChart
from datetime import datetime
#from .db import DB
import time

class data:
    def __init__(self):
        pass

    @staticmethod
    def history(asset_arr, field_arr, from_date, to_date=datetime.now().strftime("%Y-%m-%d"), freq="1d"):
        historical_data = {}

        yahoo_stock_chart = YahooStockChart()
        naver_stock_chart = NaverStockChart()

        for asset in asset_arr:
            # if asset.source == 'cybos':
            #     cybos_stock_chart = CybosPlusStockChart()
            #     historical_data[asset.use()] = cybos_stock_chart.request(symbol=asset.use(), fields=field_arr,
            #                                                               from_date=from_date, freq=freq)
            #     time.sleep(0.5)
            if asset.source == 'yahoo':
                symbol = asset.use().replace("/", "-")
                historical_data[asset.use()] = yahoo_stock_chart.request(symbol=symbol, fields=field_arr,
                                                                         from_date=from_date, to_date=to_date,
                                                                         freq=freq)
                time.sleep(0.5)
            # elif asset.source == 'db':
            #     historical_data[asset.use()] = DB(db_fname='ohlcvd.db').request(symbol=asset.use(),
            #                                                                        fields=field_arr,
            #                                                                        from_date=from_date)
            elif asset.source == 'naver':
                historical_data[asset.use()] = naver_stock_chart.request(symbol=asset.use(), fields=field_arr,
                                                                         from_date=from_date, to_date=to_date)

            else:
                raise Exception

        return historical_data

    @staticmethod
    def events(asset_arr, field_arr, start_date="1990-01-01", end_date=datetime.now().strftime("%Y-%m-%d")):
        events_data = {}
        naver_events = NaverEvents()
        yahoo_events = YahooEvents()

        for asset in asset_arr:
            # if asset.source == 'cybos':
            #     events_data[asset.use()] = naver_events.request(symbol=asset.symbol, fields=field_arr)  # 네이버 대체
            #     pass
            #     time.sleep(0.5)  # TR Limit
            if asset.source == 'yahoo':
                symbol = asset.use().replace("/", "-")
                events_data[asset.use()] = yahoo_events.request(symbol=symbol, field_arr=field_arr,
                                                                 from_date=start_date, to_date=end_date)
                time.sleep(0.5)
            elif asset.source == 'naver':
                events_data[asset.use()] = naver_events.request(symbol=asset.use(), fields=field_arr)

            # elif asset.source == 'db':
            #     events_data[asset.use()] = DB(db_fname='cp_dy.db').request_non_time_series(symbol=asset.use(), fields=field_arr)
            else:
                raise Exception
        return events_data