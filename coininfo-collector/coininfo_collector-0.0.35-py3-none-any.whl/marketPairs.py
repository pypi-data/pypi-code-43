# -*- coding: utf-8 -*-
# marketPairs 

'''
거래소 페어 정보

알정시간 마다 s3에 코인정보 스냅샷을 저장합니다.
'''

import copy
from datetime import datetime
import logging
import os
from time import mktime
import ujson

from .db_manager import DBManager

from .s3Interface import S3Interface

log = logging.getLogger('coininfo_collector')


class MarketPairsBaseClass:
	pass

class MarketPairsSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(MarketPairsSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class MarketPairs(MarketPairsBaseClass, metaclass=MarketPairsSingleton):
    def __init__(self):
        pass

    def initMarketPairs(self, dbConnString):
        self._tickCnt = 0
        self._marketPairs = dict()

        self._dbm = DBManager(dbConnString)
        self.loadMarketPairs()
    
    def loadMarketPairs(self):
        rows = self._dbm.selectMarketPairsList()

        for row in rows:
            pairs = ujson.loads(row['pairs'])

            self._marketPairs[row['exchange_id']] = {
                'pairs':pairs,
                'last_updated_ts':row['last_updated_ts'],
                'pairJs':row['pairs']
            }

    def tick(self):
        self._tickCnt += 1

        if (self._tickCnt % 18000) == 0:
            S3Interface().addJob({
                'jobName':'snapPair',
                'data':{
                    'data':copy.deepcopy(self._marketPairs),
                    'last_updated':int(mktime(datetime.utcnow().timetuple())),
                },
                'bucketName':'com.bitk.snap',
                'outputPrefix':'market-pairs/{}'.format(os.environ.get('runMode')),
            })


    def setMarketPairs(self, exchange_id, pairs):

        # 페어는 값을 비교할 때 시리얼로 비교하면 합치되는 경우만 찾아냄.
        # 기존에 가지고 있던 페어정보가 새로운 페어정보를 포함하는 개념이 되어야 함.
        # ..
        # 1. 아니면 옵션을 줘서 포함정보가 업데이트 되게 하든지
        # 2. 새로운 페어를 무조건 업데이트 치던지..
        # 요렇게 수정하자.
        # 아래는 합치로 해놨다. 2번에 가까움.

        pass

        # nowTs = int(mktime(datetime.utcnow().timetuple()))

        # if exchange_id not in self._marketPairs:
        #     self._marketPairs[exchange_id] = {
        #         'pairs':pairs,
        #         'last_updated_ts':int(nowTs),
        #         'pairSerial':ujson.dumps(pairs, ensure_ascii=False)
        #     }
        #     self._dbm.insertMarketPairs(obj)
        #     log.debug('inserted marketPairs. exchange_id:{}'.format(exchange_id))

        # else:
        #     obj = self._marketPairs[exchange_id]
            
        #     newPairSerial = ujson.dumps(pairs, ensure_ascii=False)
        #     if obj['pairSerial'] == newPairSerial:
        #         return

        #     obj = {
        #         'pairs':pairs,
        #         'last_updated_ts':int(nowTs),
        #         'pairSerial':newPairSerial
        #     }
        #     # self._coinDict[int(geckoNum)] = obj
        #     self._dbm.insertMarketPairs(obj)
        #     log.debug('updated marketPairs. exchange_id:{}'.format(exchange_id))
        


if __name__ == '__main__':
    import os
    from os.path import dirname, realpath
    appRoot = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(appRoot)

    import utail_base
    utail_base.setup_logging(default_level=logging.DEBUG)
    utail_base.setup_logging_root(loggingLv=logging.DEBUG, filePath='/tmp/testLog.log')
    
    marketPairs = MarketPairs()
    marketPairs.initMarketPairs(
        os.environ.get('dbConnString'),
    )

    pairs = list()
    pairs.append('b1|t1')
    pairs.append('b2|t2')
    marketPairs.setMarketPairs('upbit', pairs)

    pairs2 = list()
    pairs2.append('b3|t3')
    pairs2.append('b4|t4')
    marketPairs.setMarketPairs('upbit', pairs2)

    print('end')