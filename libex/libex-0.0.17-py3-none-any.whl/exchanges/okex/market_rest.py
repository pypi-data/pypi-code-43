import requests , json,logging 

from .sdk import spot_api  as spot

from pyex.adapter.fail_exception import FailException 
from .code_converter import rest_code
from .sdk.exceptions import OkexAPIException

logger = logging.getLogger(__name__)

class MarketRest(object):


    BASE_URL = 'https://www.okex.com'

    """docstring for CommandAdapter"""
    def __init__(self):
        super(MarketRest, self).__init__()
        

        self.spotApi = spot.SpotAPI('', '', '', True)

    def get_ticker(self,coin,currency):

        instrument_id = ('%s-%s' % (coin,currency)).upper()
        try:
            result = self.spotApi.get_specific_ticker(instrument_id )
        except OkexAPIException as e:

            logger.error('OkexAPIException:%s, %s',e.status_code,e.response.text)

            obj = e.response.json()

            code = rest_code(obj.get('code'))

            raise FailException(code,obj.get('message'))

        logger.debug('get ticker, resp : %s' , result )

        return {
            'code':0,
            'desc':'成功',
            'data':{
                'last':result.get('last'),
                'bid':result.get('best_bid'),
                'ask':result.get('best_ask'),
                'timestamp':result.get('timestamp')
            }
        } 

    def get_book(self,coin,currency):

        instrument_id = ('%s-%s' % (coin,currency)).upper()
        try:
            result = self.spotApi.get_depth(instrument_id )
        except OkexAPIException as e:

            logger.error('OkexAPIException:%s, %s',e.status_code,e.response.text)

            obj = e.response.json()

            code = rest_code(obj.get('code'))

            raise FailException(code,obj.get('message'))

        logger.debug('get ticker, resp : %s' , result )

        return {
            'code':0,
            'desc':'成功',
            'data':result
        } 

     

    def get_deals(self,coin,currency):

        instrument_id = ('%s-%s' % (coin,currency)).upper()
        try:
            result = self.spotApi.get_deal(instrument_id   )
        except OkexAPIException as e:

            logger.error('OkexAPIException:%s, %s',e.status_code,e.response.text)

            obj = e.response.json()

            code = rest_code(obj.get('code'))

            raise FailException(code,obj.get('message'))

        logger.debug('get ticker, resp : %s' , result )

        print(result)

        return {
            'code':0,
            'desc':'成功',
            'data':result
        } 

     

    def get_candles(self,coin,currency):

        instrument_id = ('%s-%s' % (coin,currency)).upper()
        try:
            result = self.spotApi.get_kline(instrument_id   )
        except OkexAPIException as e:

            logger.error('OkexAPIException:%s, %s',e.status_code,e.response.text)

            obj = e.response.json()

            code = rest_code(obj.get('code'))

            raise FailException(code,obj.get('message'))

        logger.debug('get ticker, resp : %s' , result )

        return {
            'code':0,
            'desc':'成功',
            'data':result
        } 


        

        