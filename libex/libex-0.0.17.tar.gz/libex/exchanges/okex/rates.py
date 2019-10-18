import json
import logging

from ...events import EventType,MarketEvent
from .const import CURRENCIES , STABLE


logger = logging.getLogger(__name__)

rates = {}
events = {}

def register_event(event,cb):

    if 'rates' != event :

        return False

    events[event] = cb

def on_ticker(coin,currency,timestamp,detail):

    key = "%s_%s" % (coin,currency)


    if coin in CURRENCIES and currency == STABLE:
        rates[key] = detail.get('last')
        
        rates_cb = events.get('rates')

        if rates_cb:
        
            rates_cb( MarketEvent('rates',rates, 'okex' ))
