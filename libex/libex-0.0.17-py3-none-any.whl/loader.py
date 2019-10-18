import logging 
import importlib


logger = logging.getLogger(__name__)

 

def load_individual_rest(ex , apikey, secrets ):
 
    mstr = 'libex.exchanges.' + ex + '.individual_rest'

    logger.debug('load class: ' + mstr)

    m = importlib.import_module(mstr) 

    ex_class = getattr (m, 'IndividualRest')

    ex_rest = ex_class( secrets)

    return ex_rest

def load_individual_ws(ex , secrets ,symbols,coins,listener ):
 
    mstr = 'libex.exchanges.' + ex + '.individual_ws'

    logger.info('load class: ' + mstr)

    m = importlib.import_module(mstr) 

    ex_class = getattr (m, 'IndividualWs')

    ex_ws = ex_class(ex ,secrets , symbols, coins , listener)

    return ex_ws

def load_market_ws(ex , symbols ,channels , listener ):
 
    mstr = 'libex.exchanges.' + ex + '.market_ws'

    logger.debug('load class: ' + mstr)

    m = importlib.import_module(mstr) 

    ex_class = getattr (m, 'MarketWs')

    ex_ws = ex_class(ex , symbols, channels , listener)

    return ex_ws