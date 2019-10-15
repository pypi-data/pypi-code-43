from QiDataProcessing.Core.TradingDayHelper import TradingDayHelper
import datetime


day = TradingDayHelper.get_pre_trading_day(datetime.datetime(2009, 5, 5))
print(day)
