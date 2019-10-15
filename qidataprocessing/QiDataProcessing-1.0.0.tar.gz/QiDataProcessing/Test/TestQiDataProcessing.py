import pandas as pd

from QiDataProcessing.Core.EnumMarket import EnumMarket
from QiDataProcessing.Instrument.InstrumentManager import InstrumentManager
from QiDataProcessing.QiDataController import QiDataController
import datetime
from QiDataProcessing.Core.EnumBarType import EnumBarType
from QiDataProcessing.QiDataDirectory import QiDataDirectory

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

trading_day = datetime.datetime(2019, 10, 13)
tick_path = "\\\\192.168.1.200\\MqData\\futuretick\\Future"
min_path = "\\\\192.168.1.200\\MqData\\futuremin"
day_path = "\\\\192.168.1.200\\MqData\\futureday"
config_dir = "D:\WorkSpace\CarlSnow\Python\QiDataProcessing\QiDataProcessing\Config"

qi_data_directory = QiDataDirectory()
qi_data_directory.trading_day = trading_day
qi_data_directory.future_tick = tick_path
qi_data_directory.future_tick_cache = tick_path
qi_data_directory.future_min = min_path
qi_data_directory.future_day = day_path

instrument_manager = InstrumentManager()
instrument_manager.load(config_dir, EnumMarket.期货)

qi_data_controller = QiDataController(qi_data_directory, instrument_manager)

interval = 5
bar_type = EnumBarType.day
instrument_id_a = "IF9999"
instrument_id_b = "rb9999"
begin_time = datetime.datetime(2019, 7, 10)
end_time = datetime.datetime(trading_day.year, trading_day.month, trading_day.day)

bar_series = qi_data_controller.get_bar_series_by_time(EnumMarket.期货, instrument_id_a, interval, bar_type, begin_time, end_time)
index = 1
for bar in bar_series:
    print("["+instrument_id_a+"]"+str(index)+":"+bar.to_string())
    index += 1

length = 20
bar_series = qi_data_controller.get_bar_series_by_length(EnumMarket.期货, instrument_id_b, interval, bar_type, length, end_time)
index = 1
for bar in bar_series:
    print("["+instrument_id_b+"]"+str(index)+":"+bar.to_string())
    index += 1

# lst_a = []
# for bar in bar_series:
#     lst_a.append([bar.trading_date, bar.begin_time, bar.end_time, bar.open, bar.high, bar.low, bar.close, bar.pre_close, bar.volume])
# dfA = pd.DataFrame(lst_a, columns=['trading_date', 'begin_time', 'end_time', 'open', 'high', 'low', 'close', 'pre_close', 'volume'])
#
# print(dfA)
#
# tickSeriesA = qi_data_controller.get_tick_series(instrument_id_a, begin_date, end_date)
# lst_a = []
# for tick in tickSeriesA:
#     lst_a.append([tick.date_time, tick.local_time, tick.last_price, tick.ask_price1, tick.bid_price1, tick.ask_volume1, tick.bid_volume1])
# dfA = pd.DataFrame(lst_a, columns=['date_time', 'local_time', 'last_price', 'ask_price1', 'bid_price1', 'ask_volume1', 'bid_volume1'])
#
# print(dfA)
