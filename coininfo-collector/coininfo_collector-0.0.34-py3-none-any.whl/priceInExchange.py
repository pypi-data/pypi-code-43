# -*- coding: utf-8 -*-
# priceInExchange 

'''
주요 거래소에서의 주요 코인 가격

관심 주요 거래소
 - global
 - binance
 - upbit
 - bithumb

주요 코인
 상위 10개 코인
 
'''

from datetime import datetime
import enum
import logging
import os
from time import mktime

from .db_manager import DBManager

log = logging.getLogger('coininfo_collector')


class MarketNoTag(enum.Enum):
    _global = 0
    binance = 1
    upbit = 2
    bithumb = 3

class PriceTupleTag(enum.Enum):
    price = 0
    created_ts = 1

class PriceInExchangeBaseClass:
	pass

class PriceInExchangeSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(PriceInExchangeSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class PriceInExchange(PriceInExchangeBaseClass, metaclass=PriceInExchangeSingleton):
    def __init__(self):
        # 각 시장별 가격맵 준비.
        self._marketList = list()

        self._marketList.append((0, MarketNoTag._global._name_, dict()) )
        self._marketList.append((1, MarketNoTag.binance._name_, dict()) )
        self._marketList.append((2, MarketNoTag.upbit._name_, dict()) )
        self._marketList.append((3, MarketNoTag.bithumb._name_, dict()) )
        
        # 저장 형태 예. 바이낸스 마켓의 BTC 가격
        # self._marketList[MarketNoTag.binance.value]['BTC'] = [
        #     (price, created_ts ),
        #     (price, created_ts ),
        # ]

        self._tickCnt = 0

    def initPriceInExchange(self, dbConnString):
        self._dbm = DBManager(dbConnString)
        self.loadPrices()

    def loadPrices(self):
        rows = self._dbm.selectPriceList()
        for row in rows:
            priceMap = self._marketList[ row['market_no'] ][2]
            self._appendPriceRow(priceMap, row['coin_id'], row['price'], row['created_ts'])

    def tick(self):
        self._tickCnt += 1

        if (self._tickCnt % 1800) == 0:
            self.clearCoinPrice()


    def _appendPriceRow(self, priceMap, coin_id, price, created_ts):
        if coin_id not in priceMap:
            priceList = list()
            priceMap[ coin_id ] = priceList
        else:
            priceList = priceMap[ coin_id ]

        priceList.append(
            (
                price,
                created_ts,
            )
        )

    def _getMarketNo(self, marketId):
        market_no = 0

        if MarketNoTag.binance._name_ == marketId:
            market_no = MarketNoTag.binance.value
        elif MarketNoTag.upbit._name_ == marketId:
            market_no = MarketNoTag.upbit.value
        elif MarketNoTag.bithumb._name_ == marketId:
            market_no = MarketNoTag.bithumb.value

        return market_no


    def getPrice1day(self, marketId, coinId):
        # 어제 가격 조회.
        # 하루 지난자료는 삭제.
        # 보존 가격 중 가장 오래된 가격을 반환.
        market_no = self._getMarketNo(marketId)
        if market_no == 0:
            log.error('invalid market no. marketID:{}'.format(marketId))
            return None

        priceMap = self._marketList[ market_no ][2]
        for k, v in priceMap.items():
            if k == coinId:
                return v[0][PriceTupleTag.price.value]

        return None


    def saveCoinPrice(self, marketId, dic):
        log.debug('save coin price. marketId:{}'.format(marketId))

        nowTs = int(mktime(datetime.utcnow().timetuple()))

        market_no = self._getMarketNo(marketId)
        if market_no == 0:
            log.error('invalid market no. marketID:{}'.format(marketId))
            return

        priceMap = self._marketList[ market_no ][2]
        priceObjList = list()

        for k, v in dic.items():
            priceObjList.append(
                {
                    'market_no':int(market_no),
                    'coin_id':k,
                    'price':v[0],
                    'created_ts':int(nowTs)
                }
            )
            self._appendPriceRow(priceMap, k, v[0], nowTs)

        self._dbm.insertCoinPriceList(priceObjList)

    
    def clearCoinPrice(self):
        # clear mem

        endTs = int(mktime(datetime.utcnow().timetuple())) - 86400

        for market in self._marketList:
            priceMap = market[2]

            for symbol, priceList in priceMap.items():

                for price_createTs_tuple in priceList[:]:
                    if endTs > price_createTs_tuple[1]:
                        priceList.remove(price_createTs_tuple)
                    else:
                        break

        # clear db
        self._dbm.clearPriceList(endTs)



if __name__ == '__main__':
    import os
    from os.path import dirname, realpath
    appRoot = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(appRoot)

    import utail_base
    utail_base.setup_logging(default_level=logging.DEBUG)
    utail_base.setup_logging_root(loggingLv=logging.DEBUG, filePath='/tmp/testLog.log')
    
    piex = PriceInExchange()
    piex.initPriceInExchange(
        os.environ.get('dbConnString'),
    )

    print('end')

