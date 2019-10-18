import json
from enum import Enum

class EventType(Enum):
     
    snapshot = 'snapshot'
    update   = 'update'



class Event(object):
    """docstring for Event"""
    def __init__(self, name, message):
        super(Event, self).__init__()
        self.name = name
        self.message = message

    
    def __str__(self):
        return self.name + " , " + json.dumps(self.message )
class MarketEvent(Event):
    """docstring for EventModel"""
    def __init__(self,name,message,exchange,coin=None,currency=None,type=EventType.snapshot):
        super(MarketEvent, self).__init__(name,message)
        
        self.exchange = exchange
        self.coin = coin
        self.currency = currency
        self.type = type


    def __str__(self):

        return f"{self.name} , {json.dumps(self.message)} , \
            {self.exchange} , {self.coin} , {self.currency} , {self.type.value}" 

class IndividualEvent(Event):
    """docstring for InvividualEvent"""
    def __init__(self, name,message,exchange,apikey):
        super(IndividualEvent, self).__init__(name ,message)

        self.exchange = exchange
        self.apikey = apikey

    def __str__(self):

        return self.name + " , <<<" +   json.dumps(self.message)[:1024]  + '>>> , ' + self.exchange + " , " + self.apikey 
class IndividualOrderEvent(IndividualEvent):
    """docstring for IndividualOrderEvent"""
    def __init__(self, name,message,exchange,apikey,coin,currency,type):
        super(IndividualOrderEvent, self).__init__(name,message,exchange,apikey)
        
        self.coin = coin
        self.currency = currency
        self.type = type

    def __str__(self):

        return self.name + " , <<< " +   json.dumps(self.message)[:1024]  + '>>> , ' + self.exchange + " , " + self.apikey + ' , ' + self.coin + ' , ' + self.currency + ' , ' + self.type.value
    
class IndividualBalanceEvent(IndividualEvent):
    """docstring for IndividualBalanceEvent"""
    def __init__(self, name,message,exchange,apikey,type):
        super(IndividualBalanceEvent, self).__init__(name,message,exchange,apikey)
        self.type = type
        

    def __str__(self):

        return self.name + " , <<<" +   json.dumps(self.message)[:1024]  + '>>> , ' + self.exchange + " , " + self.apikey + ' , ' + self.type.value