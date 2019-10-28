"""This is the Norgate Data Python interface
"""

__version__ = '1.0.24'
__author__ = 'NorgateData Pty Ltd'

from .norgatehelper import *
import csv
from enum import Enum
import sys
import logbook
from datetime import datetime

__all__ = ['StockPriceAdjustmentType','PaddingType',
           'assetid','symbol','base_type','domicile','currency','exchange_name','exchange_name_full','security_name','subtype1','subtype2','subtype3','financial_summary',
           'business_summary','last_quoted_date','second_last_quoted_date',
           'lowest_ever_tick_size','margin','point_value','tick_size','first_notice_date','base_symbol','futures_market_name','futures_market_session_name',
           'futures_market_session_symbols',
           'futures_market_session_symbol','futures_market_symbol','futures_market_session_contracts',
           'price_timeseries','capital_event_timeseries','dividend_yield_timeseries','index_constituent_timeseries','major_exchange_listed_timeseries',
           'padding_status_timeseries','unadjusted_close_timeseries',
           'last_database_update_time','last_price_update_time','status',
           'watchlist_symbols','watchlist','watchlists',
           'fundamental',
           'classification','classification_at_level','corresponding_industry_index',
           '__version__','__author__'] 

logbook.StreamHandler(sys.stdout).push_application()  # required for Jupyter to output
logger = logbook.Logger('Norgate Data')


class StockPriceAdjustmentType(Enum):
    NONE = 0
    CAPITAL = 1
    CAPITALSPECIAL = 2
    TOTALRETURN = 3

class PaddingType(Enum):
    NONE = 0
    ALLMARKETDAYS = 3
    ALLWEEKDAYS = 4
    ALLCALENDARDAYS = 5

checkstatus()
version_checker(__version__,'norgatedata')

#######################################################################################################
#                           SYMBOL METADATA
#######################################################################################################


def assetid(symbol):
    r = get_api_data('security',str(symbol) + '/assetid',None)
    validate_api_response(r,symbol)
    return int(bytes.decode(r.data))

def symbol(assetid):
    r = get_api_data('security',str(assetid) + '/symbol',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def base_type(symbol):
    r = get_api_data('security',str(symbol) + '/basetype',None)
    return bytes.decode(r.data)

def domicile(symbol):
    r = get_api_data('security',str(symbol) + '/domicile',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def exchange_name(symbol):
    r = get_api_data('security',str(symbol) + '/exchange',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def exchange_name_full(symbol):
    r = get_api_data('security',str(symbol) + '/exchangenamefull',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def currency(symbol):
    r = get_api_data('security',str(symbol) + '/currency',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def security_name(symbol):
    r = get_api_data('security',str(symbol) + '/name',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def futures_market_name(symbol):
    r = get_api_data('futuresmarket',str(symbol) + '/name',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def futures_market_session_name(symbol):
    r = get_api_data('futuresmarket',str(symbol) + '/sessionname',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def subtype1(symbol):
    r = get_api_data('security',str(symbol) + '/subtype1',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def subtype2(symbol):
    r = get_api_data('security',str(symbol) + '/subtype2',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def subtype3(symbol):
    r = get_api_data('security',str(symbol) + '/subtype3',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def financial_summary(symbol):
    # TODO: Output date at the same time ?
    r = get_api_data('security',str(symbol) + '/financialsummary',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def business_summary(symbol):
    # TODO: Output date at the same time ?
    r = get_api_data('security',str(symbol) + '/businesssummary',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def last_quoted_date(symbol):
    r = get_api_data('security',str(symbol) + '/lastquoteddate',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def second_last_quoted_date(symbol):
    r = get_api_data('security',str(symbol) + '/secondlastquoteddate',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)



#######################################################################################################
#                           FUTURES METADATA
#######################################################################################################
def lowest_ever_tick_size(symbol):
    r = get_api_data('security',str(symbol) + '/lowesteverticksize',None)
    validate_api_response(r,symbol)
    return float(r.data)

def margin(symbol):
    r = get_api_data('security',str(symbol) + '/margin',None)
    validate_api_response(r,symbol)
    return float(r.data)

def point_value(symbol):
    r = get_api_data('security',str(symbol) + '/pointvalue',None)
    validate_api_response(r,symbol)
    return float(r.data)

def tick_size(symbol):
    r = get_api_data('security',str(symbol) + '/ticksize',None)
    validate_api_response(r,symbol)
    return float(r.data)

def first_notice_date(symbol):
    r = get_api_data('security',str(symbol) + '/firstnoticedate',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def base_symbol(symbol):
    logger.warn("base_symbol deprecated, use futures_market_session_symbol instead")
    r = get_api_data('security',str(symbol) + '/basesymbol',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def futures_market_session_symbol(symbol):
    r = get_api_data('security',str(symbol) + '/futuresmarketsessionsymbol',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def futures_market_symbol(symbol):
    r = get_api_data('security',str(symbol) + '/futuresmarketsymbol',None)
    validate_api_response(r,symbol)
    return bytes.decode(r.data)

def futures_market_session_symbols():
    r = get_api_data('futuresmarket',"sessionsymbols",None)
    validate_api_response(r,'sessionsymbols')
    symbols = r.data.decode().splitlines()
    return symbols

def futures_market_session_contracts(session_symbol):
    r = get_api_data('futuresmarketsession',str(session_symbol) + "/sessioncontracts",None)
    validate_api_response(r,'session_symbol')
    symbols = r.data.decode().splitlines()
    return symbols

#######################################################################################################
#                           TIMESERIES
#######################################################################################################
def price_timeseries(symbol,
                          stock_price_adjustment_setting=StockPriceAdjustmentType.CAPITALSPECIAL,
                          padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format='numpy-recarray'):
    lowercase_columns = False
    if format == 'pandas-dataframe-zipline':
        format = 'pandas-dataframe'
        lowercase_columns = True
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'stock_price_adjustment_setting':stock_price_adjustment_setting.name,
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('prices',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,None)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,None,lowercase_columns)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,None)


###############
def capital_event_timeseries(symbol,
                          padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None,):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('capitalevent',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)

###############

def unadjusted_close_timeseries(symbol,
                          padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None,):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('unadjustedclose',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)


#####

def dividend_yield_timeseries(symbol,
                          padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None,):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('dividendyield',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)


###############



def index_constituent_timeseries(symbol,
                          indexname,
                          padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None,):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)

    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'indexname' : indexname,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('indexconstituent',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)



###############
def major_exchange_listed_timeseries(symbol,
                             padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)

    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('majorexchangelisted',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)

###############
def padding_status_timeseries(symbol,
                             padding_setting=PaddingType.NONE,
                          start_date="1800-01-01",
                          end_date="2999-01-01",
                          limit=-1,
                          format="numpy-recarray",
                          pandas_dataframe=None,
                          numpy_ndarray=None,
                          numpy_recarray=None,):
    if pandas_dataframe is not None or numpy_ndarray is not None or numpy_recarray is not None:
        start_date,end_date,limit = validate_existing_array(pandas_dataframe,numpy_ndarray,numpy_recarray,format)
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':format }
    r = get_api_data('paddingstatus',str(symbol),parameters)
    validate_api_response(r,symbol)
    if format == 'numpy-recarray':
        return create_numpy_recarray(r,numpy_recarray)
    if format == "pandas-dataframe":
        return create_pandas_dataframe(symbol,r,pandas_dataframe)
    if format == 'numpy-ndarray':
        return create_numpy_ndarray(r,numpy_ndarray)

#######################################################################################################
#                           INFORMATIONAL - UPDATE RELATED
#######################################################################################################

def last_database_update_time(databasename):
    r = get_api_data('database',databasename + '/lastupdatetime',None)
    validate_api_response(r,databasename)
    result = datetime.strptime(r.data.decode().replace(':',''),'%Y-%m-%dT%H%M%S%z')
    return result

def last_price_update_time(symbol):
    r = get_api_data('security',str(symbol) + '/lastupdatetime',None)
    validate_api_response(r,symbol)
    result = datetime.strptime(r.data.decode().replace(':',''),'%Y-%m-%dT%H%M%S%z')
    return result

def status():
    return checkstatus()

#######################################################################################################
#                           WATCHLIST
#######################################################################################################

def watchlist(watchlistname):
    parameters = { 'format':'csv' }
    r = get_api_data('watchlist',watchlistname,parameters)
    validate_api_response(r,watchlistname)
    txtlines = r.data.decode().splitlines()
    lines = csv.reader(txtlines, delimiter=',')
    symbols = []
    for line in lines:
        if line[0] == 'Symbol':
            continue
        symbols.append({ 'symbol':line[0], 'assetid':int(line[1]), 'securityname':line[2] })
    return symbols

def watchlist_symbols(watchlistname):
    parameters = { 'format':'symbolsonly' }
    r = get_api_data('watchlist',watchlistname,parameters)
    validate_api_response(r,watchlistname)
    symbols = r.data.decode().splitlines()
    return symbols

def watchlists():
    r = get_api_data('watchlists',None,None)
    validate_api_response(r,'watchlists')
    symbols = r.data.decode().splitlines()
    return symbols




#######################################################################################################
#                           FUNDAMENTALS
#######################################################################################################
def fundamental(symbol,field):  
    # Returns both the field value and date
    r = get_api_data('fundamental',str(symbol) + '/' + field,None)
    validate_api_response(r,symbol)
    if len(r.data) == 0:
        return None,None
    fundamentalresult,fundadate = r.data.decode().split(',')
    # result = bytes.decode(r.data);
    return fundamentalresult,fundadate 


#######################################################################################################
#                           CLASSIFICATION RELATED
#######################################################################################################
def classification(symbol,schemename,classificationresulttype):
    parameters = { 'schemename': schemename,
                    'classificationresulttype': classificationresulttype }
    r = get_api_data('security',str(symbol) + '/classification',parameters)
    validate_api_response(r,symbol)
    if len(r.data) == 0:
        return None
    result = bytes.decode(r.data)
    return result

def classification_at_level(symbol,schemename,classificationresulttype,level):
    parameters = { 'schemename': schemename,
                    'classificationresulttype': classificationresulttype,
                    'level': level }
    r = get_api_data('security',str(symbol) + '/classification',parameters)
    validate_api_response(r,symbol)
    if len(r.data) == 0:
        return None
    result = bytes.decode(r.data)
    return result

def corresponding_industry_index(symbol,indexfamilycode,level,indexreturntype):
    parameters = { 'indexfamilycode': indexfamilycode,
                    'level': level,
                    'indexreturntype' : indexreturntype }
    r = get_api_data('security',str(symbol) + '/correspondingindustryindex',parameters)
    validate_api_response(r,symbol + ' or ' + indexfamilycode )
    if len(r.data) == 0:
        return None
    result = bytes.decode(r.data)
    return result

logger.info('NorgateData package v' + __version__ + ': Init complete')
