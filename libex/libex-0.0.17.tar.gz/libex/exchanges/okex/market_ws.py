#!/usr/bin/env python3
'''
api docs
https://www.okex.com/docs/en/#spot_ws-general
'''

import websockets
import json
import zlib
import iso8601
import traceback
import logging
                
from ...common.timer import Timer

from ...const import Channel
from ...base_market_ws import BaseMarketWs
from .const import WS_URL
from .sdk.exceptions import OkexAPIException
from .sdk import spot_api  as spot
from . import book
from . import rates
from ...events import MarketEvent,EventType

logger = logging.getLogger(__name__)



def _inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

CHANNELS={
    Channel.trade:'spot/trade',
    Channel.book:'spot/depth',
    Channel.book5:'spot/depth5',
    Channel.candle1h:'spot/candle3600s',
    Channel.candle5m:'spot/candle300s'
      
} 




class MarketWs(BaseMarketWs):
    """docstring for OkexAdapter"""

    def __init__(self,exchange,symbols ,channels,listeners):
        super(MarketWs, self).__init__(exchange,symbols,channels,listeners)

        book.register_event('book10', lambda event:self._listener.on_market_event(event))
        book.register_event('book20', lambda event:self._listener.on_market_event(event))
        rates.register_event('rates' , lambda event:self._listener.on_market_event(event))

    def convert_trade(self,origin):
        tid   = origin.get('trade_id')
        price = origin.get('price')
        size  = origin.get('size')
        side  = origin.get('side')
        ts    = origin.get('timestamp')

        ts = iso8601.parse_date(ts).timestamp()

        # ts = iso8601.parse_date(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
        # ts = iso8601.parse_date(ts).astimezone(pytz.timezone("Asia/Shanghai")).isoformat()

        return {
            'tid':tid,
            'price':price,
            'size':size,
            'side':side,
            'ts':ts 
        }


    def convert_book_update(self,origin):
        asks = origin.get('asks')
        bids = origin.get('bids')
        ts    = origin.get('timestamp')

        ts = iso8601.parse_date(ts).timestamp()

        # ts = iso8601.parse_date(ts).astimezone(pytz.timezone("Asia/Shanghai")).isoformat()

        
        return {
            "asks":asks,
            "bids":bids,
            "ts":ts
        }

    def convert_book_snapshot(self,msg):
        asks = msg.get('asks')
        bids = msg.get('bids') 
 
        return {
            "asks":asks,
            "bids":bids
        }
         

    def convert_book5(self,origin):

        logger.debug(f"convert_book5,{json.dumps(origin)}" )

        asks = origin.get('asks')
        bids = origin.get('bids')
        ts   = origin.get('timestamp')

        ts = iso8601.parse_date(ts).timestamp()
        
        return {
            "asks":asks,
            "bids":bids,
            "ts":ts
        }

    def convert_candle1h(self,origin):

        logger.debug(f"convert_candle1h,{json.dumps(origin)}")

        (ts,o,h,l,c,v) = origin.get('candle')
        ts = iso8601.parse_date(ts).timestamp()
        
        return [ts,o,h,l,c,v]

    def convert_candle5m_rest(self,origin):

        logger.debug(f"convert_candle5m_rest,{json.dumps(origin)}")

        converted = []
        for item in origin:
            (ts,o,h,l,c,v) = item
            ts = iso8601.parse_date(ts).timestamp()
            converted.append([ts,o,h,l,c,v])
        return converted

    def convert_candle5m(self,origin):

        logger.debug(f"convert_candle5m,{json.dumps(origin)}")

        (ts,o,h,l,c,v) = origin.get('candle')
        ts = iso8601.parse_date(ts).timestamp()
        
        return [ts,o,h,l,c,v]

    def convert_ticker(self,origin):

        logger.debug(f"convert_ticker, {json.dumps(origin)}")

        last    = origin.get('last')
        bid = origin.get('best_bid')
        ask = origin.get('best_ask')
        ts  = origin.get('timestamp')

        ts = iso8601.parse_date(ts).timestamp()

        return {
            "last":last,
            "bid":bid,
            "ask":ask,
            "ts":ts
        }

    # subscribe channel without login
    #
    # swap/ticker // 行情数据频道
    # swap/candle60s // 1分钟k线数据频道
    # swap/candle180s // 3分钟k线数据频道
    # swap/candle300s // 5分钟k线数据频道
    # swap/candle900s // 15分钟k线数据频道
    # swap/candle1800s // 30分钟k线数据频道
    # swap/candle3600s // 1小时k线数据频道
    # swap/candle7200s // 2小时k线数据频道
    # swap/candle14400s // 4小时k线数据频道
    # swap/candle21600 // 6小时k线数据频道
    # swap/candle43200s // 12小时k线数据频道
    # swap/candle86400s // 1day k线数据频道
    # swap/candle604800s // 1week k线数据频道
    # swap/trade // 交易信息频道
    # swap/funding_rate//资金费率频道
    # swap/price_range//限价范围频道
    # swap/depth //深度数据频道，首次200档，后续增量
    # swap/depth5 //深度数据频道，每次返回前5档
    # swap/mark_price// 标记价格频道
    async def connect(self):


        try:

            for symbol_arr in self._symbols:

                candles = self.get_candles(symbol_arr[0],symbol_arr[1])


                converted = self.convert_candle5m_rest( candles )

                # self._listener.on_candle5m_snapshot(symbol_arr[0],symbol_arr[1],None,converted)

                self._listener.on_market_event(MarketEvent('candle5m',converted,'okex',symbol_arr[0],symbol_arr[1],EventType.snapshot))


                logger.info('candles: %s' , candles)
        except Exception as e :

            logger.error(traceback.format_exc())


        logger.info(f"okex,will connect to:{WS_URL}")

        async with websockets.connect(WS_URL) as websocket:

            last_ts = None
            current_ts = None

            self._listener.on_start()


            channels = []
            for symbol_arr in self._symbols:
                
                for item in self._channels:

                    channel = f"{ item }:{symbol_arr[0].upper()}-{symbol_arr[1].upper()}"

                    channels.append(channel)
            
            logger.info(f"okex,channels: {channels}")
            
                
            try:
                sub_param = {"op": "subscribe", "args": channels}
                sub_str = json.dumps(sub_param)
                await  websocket.send(sub_str)

                self._listener.on_sent(sub_str)

                async def ping():
                    await websocket.send("ping")
                    self._listener.on_sent('ping')

                    logger.info('okex,send ping ..')
                
                timer = Timer.interval(ping,10,10)
                
                logger.info('okex,start recv loop.')
                
                while True:
                    res = await websocket.recv()

                    timer.refresh()

                    plain = _inflate(res).decode('utf-8')

                    self._listener.on_recv(plain)

                    if "pong" == plain:
                        logger.info('okex,recv pong ..')
                
                        continue

                    obj = json.loads(plain)

                    table  = obj.get('table')
                    action = obj.get('action')
                    data   = obj.get('data')
    
                    if table == 'spot/ticker':

                        channel = Channel.ticker

                        for item in data:
                            (coin,currency) = item.get('instrument_id').lower().split('-')

                            # asks = item.get('asks')
                            # bids = item.get('bids')
                            ts = item.get('timestamp')

                            ts = iso8601.parse_date(ts).timestamp()
                            current_ts = int(ts/3600)

                            converted = self.convert_ticker(item)


                            self._listener.on_resolve(coin,currency,channel.value,None,ts,item)
                            # self._listener.on_ticker(coin,currency,ts,converted)
                            self._listener.on_market_event(MarketEvent('ticker',converted,'okex',coin,currency,EventType.snapshot))

                            rates.on_ticker(coin,currency,None, converted)


                    elif table == 'spot/depth':

                        channel = Channel.book

                        if action == 'partial': 

                            for item in data:
                                (coin,currency) = item.get('instrument_id').lower().split('-') 
                                asks = item.get('asks')
                                bids = item.get('bids')
                                ts = item.get('timestamp')
                                # ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                                ts = iso8601.parse_date(ts).timestamp()
                                current_ts = int(ts/3600)

                                converted = self.convert_book_snapshot(item)

                                self._listener.on_resolve(coin,currency,channel.value + '/snapshot',None,ts,item)
                                
                                book.books_snapshot(coin,currency,ts,converted)

                                # self._listener.on_book_snapshot(coin,currency,ts,converted)


     
                        elif action == 'update':
                            
                            for item in data:
                                (coin,currency) = item.get('instrument_id').lower().split('-') 
                                asks = item.get('asks')
                                bids = item.get('bids')
                                ts = item.get('timestamp')
                                # ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                                ts = iso8601.parse_date(ts).timestamp()
                                current_ts = int(ts/3600)

                                converted = self.convert_book_update(item)
                                
                                self._listener.on_resolve(coin,currency,channel.value + '/update',None,ts,item)
                                
                                book.books_update(coin,currency,ts,converted) 

                    elif table == 'spot/trade':


                        channel = Channel.trade

                        for item in data:

                            (coin,currency) = item.get('instrument_id').lower().split('-') 
                            
                            tid = item.get('trade_id')
                            ts = item.get('timestamp')
                            # ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                            ts = iso8601.parse_date(ts).timestamp()
                            current_ts = int(ts/3600)

                            converted = self.convert_trade(item)

                            self._listener.on_resolve(coin,currency,channel.value,tid,ts,item)
                            # self._listener.on_trade(coin,currency,ts,converted)
                            self._listener.on_market_event(MarketEvent('trade',converted,'okex',coin,currency,EventType.update))


                    elif table == 'spot/depth5':

                        channel = Channel.book5

                        for item in data:
                            (coin,currency) = item.get('instrument_id').lower().split('-')

                            asks = item.get('asks')
                            bids = item.get('bids')
                            ts = item.get('timestamp')

                            ts = iso8601.parse_date(ts).timestamp()
                            current_ts = int(ts/3600)

                            converted = self.convert_book5(item)


                            self._listener.on_resolve(coin,currency,channel.value,None,ts,item)
                            # self._listener.on_book5(coin,currency,ts,converted)
                            self._listener.on_market_event(MarketEvent('book5',converted,'okex',coin,currency,EventType.snapshot))


                    elif table == 'spot/candle3600s':

                        channel = Channel.candle1h

                        for item in data:
                            (coin,currency) = item.get('instrument_id').lower().split('-')

                            candle = item.get('candle')
                            # ts = item.get('timestamp')

                            # ts = iso8601.parse_date(ts).timestamp()
                            # current_ts = int(ts/3600)

                            converted = self.convert_candle1h(item)


                            self._listener.on_resolve(coin,currency,channel.value,None,None,item)
                            # self._listener.on_candle1h(coin,currency,ts,converted)

                    elif table == 'spot/candle300s':

                        channel = Channel.candle5m

                        for item in data:
                            (coin,currency) = item.get('instrument_id').lower().split('-')

                            candle = item.get('candle')
                            # ts = item.get('timestamp')

                            # ts = iso8601.parse_date(ts).timestamp()
                            # current_ts = int(ts/3600)

                            converted = self.convert_candle5m(item)


                            self._listener.on_resolve(coin,currency,channel.value,None,None,item)
                            # self._listener.on_candle5m(coin,currency,ts,converted)
                            self._listener.on_market_event(MarketEvent('candle5m',converted,'okex',coin,currency,EventType.update))


                    if last_ts and current_ts and current_ts > last_ts:

                            self._listener.on_flag(last_ts*3600)

                    last_ts = current_ts
            
            finally:

                self._listener.on_end()



    # unsubscribe channels
    async def unsubscribe_without_login(self,url, channels):
        async with websockets.connect(url) as websocket:
            sub_param = {"op": "unsubscribe", "args": channels}
            sub_str = json.dumps(sub_param)
            await  websocket.send(sub_str)
            # logger.debug(f"send: {sub_str}")

            res = await websocket.recv()
            res = _inflate(res)
            # logger.debug(f"{res}")



    def get_candles(self,coin,currency):

        instrument_id = ('%s-%s' % (coin,currency)).upper()
        try:
            spotApi = spot.SpotAPI('', '', '', True)

            result = spotApi.get_kline(instrument_id ,granularity=300  )
        
            return result
        except OkexAPIException as e:

            logger.error('OkexAPIException:%s, %s',e.status_code,e.response.text)

            obj = e.response.json()

            raise e





