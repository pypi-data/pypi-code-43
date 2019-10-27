# -*- coding: utf-8 -*-
# coinSummary

'''
코인의 대략적인 정보를 관리합니다.

관리요소
 - gecko_id
 - symbol
 - name_en
 - name_ko
 - iamge_thumb
 - image_small
 - image_large
 - trade_url

 알정시간 마다 s3에 코인정보 스냅샷을 저장합니다.

 setCoinInfo => 코인정보 갱신.

 '''

import copy
from datetime import datetime
import enum
import logging
import os
from os.path import dirname, realpath
import requests
import threading
from time import mktime

from .db_manager import DBManager

from .s3Interface import S3Interface

log = logging.getLogger('coininfo_collector')


# GeckoStruct = {
#     coin_id = ''
#     gecko_id = 0
#     symbol = ''
#     name_en = ''
#     name_ko = ''
#     image_thumb = ''
#     image_small = ''
#     image_large = ''
# }

class MarketNoTag(enum.Enum):
    _global = 0
    binance = 1
    upbit = 2
    bithumb = 3

class PriceTupleTag(enum.Enum):
    price = 0
    created_ts = 1


class CoinSummaryBaseClass:
	pass

class CoinSummarySingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(CoinSummarySingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class CoinSummary(CoinSummaryBaseClass, metaclass=CoinSummarySingleton):
    def __init__(self):
        self._coinDict = dict()
        self._lock = threading.Lock()
        self._tickCnt = 0
        

    def initCoinSummary(self, dbConnString):
        self._dbm = DBManager(dbConnString)
        self._loadCoins()
        
        

    def _loadCoins(self):
        rows = self._dbm.selectGeckoCoinList()

        loaded_coin_ids = list()

        for row in rows:
            obj = {
                'coin_id' : row['coin_id'],
                'gecko_id' : int(row['gecko_id']),
                'symbol' : row['symbol'],
                'name_en' : row['name_en'],
                'name_ko' : row['name_ko'],
                'image_thumb' : row['image_thumb'],
                'image_small' : row['image_small'],
                'image_large' : row['image_large'],
                'trade_url' : row['trade_url'],

            }
            self._coinDict[int(obj['gecko_id'])] = obj

            loaded_coin_ids.append(row['coin_id'])

        log.debug('loaded coins:{}'.format(loaded_coin_ids))

    
    def tick(self):
        self._tickCnt += 1

        if (self._tickCnt % 1800) == 0:
            S3Interface().addJob({
                'jobName':'snapCoin',
                'data':{
                    'data':copy.deepcopy(self._coinDict),
                    'last_updated':int(mktime(datetime.utcnow().timetuple())),
                },
                'bucketName':'com.bitk.snap',
                'outputPrefix':'coin-summary/{}'.format(os.environ.get('runMode')),
            })


    def getCoinInfoByCoinId(self, coin_id):
        with self._lock:
            for k, obj in self._coinDict.items():
                if obj['coin_id'] == coin_id:
                    return obj

        return None


    def setCoinInfo(
        self, coin_id, geckoNum, symbol,
        name_en, name_ko, image_thumb, image_small, image_large,
        trade_url
    ):
        symbol = symbol.upper()

        with self._lock:
            if geckoNum not in self._coinDict:
                obj = {
                    'coin_id' : coin_id,
                    'gecko_id' : geckoNum,
                    'symbol' : symbol,
                    'name_en' : name_en,
                    'name_ko' : name_ko,
                    'image_thumb' : image_thumb,
                    'image_small' : image_small,
                    'image_large' : image_large,
                    'trade_url' : trade_url,
                }
                self._coinDict[int(geckoNum)] = obj

                self._dbm.insertGeckoCoin(obj)
                log.debug('inserted coin. geckoNum:{}/symbol:{}/name:{}/coinID:{}/icon:{}'.format(geckoNum, symbol, name_ko, coin_id, image_thumb))
            else:
                obj = self._coinDict[int(geckoNum)]

                update = False
                if coin_id != obj['coin_id']:
                    update = True
                    obj['coin_id'] = coin_id
                if symbol != obj['symbol']:
                    update = True
                    obj['symbol'] = symbol
                if name_en != obj['name_en']:
                    update = True
                    obj['name_en'] = name_en
                if name_ko != obj['name_ko']:
                    update = True
                    obj['name_ko'] = name_ko
                if image_thumb != obj['image_thumb']:
                    update = True
                    obj['image_thumb'] = image_thumb
                if image_small != obj['image_small']:
                    update = True
                    obj['image_small'] = image_small
                if image_large != obj['image_large']:
                    update = True
                    obj['image_large'] = image_large
                if trade_url != obj['trade_url']:
                    update = True
                    obj['trade_url'] = trade_url
                    

                if update is True:
                    self._coinDict[int(geckoNum)] = obj

                    self._dbm.updateGeckoCoin(obj)
                    log.debug('updated coin. geckoNum:{}/symbol:{}/name:{}/coinID:{}/image_thumb:{}'.format(geckoNum, symbol, name_ko, coin_id, image_thumb))


if __name__ == '__main__':
    import os
    appRoot = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(appRoot)

    # setup logging
    import utail_base
    utail_base.setup_logging(default_level=logging.DEBUG)
    utail_base.setup_logging_root(loggingLv=logging.DEBUG, filePath='/tmp/testLog.log')

    from time import sleep


    S3Interface().S3InterfaceInit(
        ACCESS_KEY=os.environ.get('aws_access_key_id'),
        SECRET_KEY=os.environ.get('aws_secret_access_key'),
    )
   
    cs = CoinSummary()
    cs.initCoinSummary(
        os.environ.get('dbConnString'),
    )
    cs._tickCnt = 1800 - 1

    while True:
        sleep(100)

    print('end')

