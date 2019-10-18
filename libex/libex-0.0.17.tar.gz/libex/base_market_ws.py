#!/usr/bin/env python3

import asyncio

import logging
import logging.handlers
                
import traceback
import websockets

from .common.timer import Timer

logger = logging.getLogger(__name__)
 

class BaseMarketWs(object):
    """记录程序，将各交易所的实时行情数据初步解析后记录成文件"""

    def __init__(self,exchange ,symbols ,channels,listener):
        super(BaseMarketWs, self).__init__()
        
        self._exchange = exchange
        
        self._symbols = symbols
        self._channels = channels

        self._listener = listener

    def run_task(self):
        try:
            asyncio.get_event_loop().run_until_complete(self.task())

        except Exception as e:
            logger.error( 'Adapter ERROR, %s ,%s' , e, traceback.format_exc() ) 

    async def task(self):

        logger.info('will connect to %s\'s market websocket server.' , self._exchange )

        while True:

            try:
                await self.connect()

            except TimeoutError as e:
                logger.error(f"{self._exchange},connect timeout,will reconnect,{e},{traceback.format_exc()}")

                asyncio.sleep(20)
            
            except websockets.ConnectionClosed as e:
                logger.error(f"{self._exchange},connect closed,will reconnect,{e},{traceback.format_exc()}")
                
            except websockets.WebSocketException as e:
                logger.error(f"{self._exchange},websockets exception,will reconnect,{e},{traceback.format_exc()}")
                
                asyncio.sleep(1)

            except Exception as e:
                logger.error(traceback.format_exc()) 
                
                raise


    def convert_trade(self,origin):
        """ 该方法需要子类实现 """
        pass

    def convert_book_snapshot(self,origin):
        """ 该方法需要子类实现 """
        pass

    def convert_book_update(self,origin):
        """ 该方法需要子类实现 """
        pass

    def convert_ticker(self,origin):
        """ 该方法需要子类实现 """
        pass

    def convert_book5(self,origin):
        """ 该方法需要子类实现 """
        pass

    def convert_candle1h(self,origin):
        """ 该方法需要子类实现 """
        pass
    async def connect(self):    
        """ 该方法需要子类实现 """
        pass
