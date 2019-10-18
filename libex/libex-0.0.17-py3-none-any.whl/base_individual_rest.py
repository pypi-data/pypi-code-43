from enum import Enum

class ClassLimitBuyRet(Enum):
    BALANCE_NOT_ENOUGH
    

class BaseIndividualRest(object):
    """docstring for BaseIndividualRest"""
    def __init__(self):
        super(BaseIndividualRest, self).__init__()
        

    def detect(self):
        pass

    def order_info(self,orderid,coin,currency):
        pass
    
    def limit_order(self, price ,amount , coin , currency ,side, coid=None ):
        pass
        

    def market_order(self, size , coin , currency ,side ,coid =None):
        pass
        

    def cancel_order(self, orderid, coin,currency ):
        pass