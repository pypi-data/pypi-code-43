import time
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class BaseMarketListener(object):
    """ 市场数据Websocket监听器的示例类.
        调用者可以参照该类的方法来创建自己的监听器类。
    """
    def __init__(self,ex):
        super(BaseMarketListener, self).__init__()
       
        self._exchange = ex

    def on_sent(self,plain):
        
        logger.info(f"{self._exchange},send:{plain}")

    def on_recv(self,plain):

        logger.info(f"{self._exchange},recv:{plain}" )
        
    def on_start(self):

        logger.info(f"{self._exchange},connected" )
        
    def on_end(self):

        logger.info(f"{self._exchange},disconnect")

    def on_resolve(self,coin,currency,channel,cid,ts,detail):

        logger.info(f"{self._exchange},{coin},{currency},{channel},{cid},{ts},{detail}" )

 
    def on_market_event(self,event):
        
        logger.debug(f"{self._exchange},{event}")
        
    def on_flag(self,ts):

        logger.debug(f"running flag,{self._exchange},{ts}" )

