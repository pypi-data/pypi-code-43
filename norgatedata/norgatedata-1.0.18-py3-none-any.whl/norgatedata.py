from norgatehelper import *
import urllib3
import urllib
import datetime
import sys
import numpy as np
import pandas as pd
from typing import TypeVar
from enum import Enum
#from logbook import Logger

# Enums

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


# Type Hints

assetid = TypeVar(int)
symbol = TypeVar(str)
field = TypeVar(str)
databasename = TypeVar(str)
level = TypeVar(int)
schemename = TypeVar(str)
indexfamilycode = TypeVar(str)
indexreturntype = TypeVar(str) # Might change to an enum
classificationresulttype = TypeVar(str) # Might change to an enum

#######################################################################################################
#                           SYMBOL METADATA
#######################################################################################################


def assetid(symbol):
    url = build_api_url('security',symbol + '/assetid',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return int(r.data);

def symbol(assetid):
    url = build_api_url('security',assetid + '/symbol',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("assetid" + str(assetid) + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def base_type(symbol):
    url = build_api_url('security',symbol + '/basetype',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);


def domicile(symbol):
    url = build_api_url('security',symbol + '/domicile',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def exchange_name(symbol):
    url = build_api_url('security',symbol + '/exchange',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def currency(symbol):
    url = build_api_url('security',symbol + '/currency',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        #log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);


def security_name(symbol):
    url = build_api_url('security',symbol + '/name',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def subtype1(symbol):
    url = build_api_url('security',symbol + '/subtype1',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def subtype2(symbol):
    url = build_api_url('security',symbol + '/subtype2',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def subtype3(symbol):
    url = build_api_url('security',symbol + '/subtype3',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def financial_summary(symbol):
    # TODO: Output date at the same time
    url = build_api_url('security',symbol + '/financialsummary',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);


def business_summary(symbol):
    # TODO: Output date at the same time
    url = build_api_url('security',symbol + '/businesssummary',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);


def last_quoted_date(symbol):
    # TODO - output as date?
    url = build_api_url('security',symbol + '/lastquoteddate',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def second_last_quoted_date(symbol):
    # TODO - output as date?
    url = build_api_url('security',symbol + '/secondlastquoteddate',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

#######################################################################################################
#                           FUTURES METADATA
#######################################################################################################

def lowest_ever_tick_size(symbol):
    url = build_api_url('security',symbol + '/lowesteverticksize',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def margin(symbol):
    url = build_api_url('security',symbol + '/margin',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def point_value(symbol):
    url = build_api_url('security' + '/pointvalue',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def tick_size(symbol):
    url = build_api_url('security' + '/ticksize',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);

def first_notice_date(symbol):
    url = build_api_url('security' + '/firstnoticedate',None);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol" + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    return str(r.data);



#######################################################################################################
#                           TIMESERIES
#######################################################################################################
def price_timeseries(symbol,
                          stock_price_adjustment_setting = StockPriceAdjustmentType.CAPITALSPECIAL,
                          padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit=-1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'stock_price_adjustment_setting':stock_price_adjustment_setting.name,
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('prices',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    equitydataType = [
        ('Open', 'f4'),
        ('High','f4'),
        ('Low', 'f4'),
        ('Close', 'f4'),
        ('Volume', 'f4'),
        ('Turnover', 'f4'),
        ('Unadjusted Close', 'f4'),
        ('Dividend', 'f4')
        ]
    npdata = np.frombuffer(r.data,equitydataType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf



###############
def capital_event_timeseries(symbol,
                          padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit = -1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('capitalevent',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    indicatorType = [
          ('Capital Event', 'i'),
        ]
    npdata = np.frombuffer(r.data,indicatorType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf

###############

def dividend_yield_timeseries(symbol,
                          padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit = -1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('dividendyield',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    indicatorType = [
      ('Dividend Yield', 'f4'),
     ]
    npdata = np.frombuffer(r.data,indicatorType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf

###############

def index_constituent_timeseries(symbol,
                          indexname,
                          padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit = -1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'indexname' : indexname,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('indexconstituent',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    indicatorType = [
      ('Index Constituent', 'i'),
     ]
    npdata = np.frombuffer(r.data,indicatorType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf


###############

def major_exchange_listed_timeseries(symbol,indexname,
                             padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit = -1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('majorexchangelisted',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    indicatorType = [
      ('Major Exchange Listed', 'i'),
     ]
    npdata = np.frombuffer(r.data,indicatorType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf

###############

def padding_status_timeseries(symbol,indexname,
                             padding_setting = PaddingType.NONE,
                          start_date = "1800-01-01",
                          end_date = "2999-01-01",
                          limit = -1):
    parameters = { 'start_date': start_date,
                    'end_date': end_date,
                    'limit':str(limit),
                    'padding_setting':padding_setting.name,
                    'format':'pandas' }
    url = build_api_url('paddingstatus',symbol,parameters);
    try:
        r = httppool.request('GET', url)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    recordcount = int(r.headers['X-Norgate-Data-Record-Count'])
    npdates = np.frombuffer(r.data,'datetime64[D]',recordcount)
    npdates = npdates.copy()
    indicatorType = [
      ('Padding Status', 'i'),
     ]
    npdata = np.frombuffer(r.data,indicatorType,-1,recordcount * 8)
    npdata = npdata.copy()
    pdf = pd.DataFrame(data=npdata,index=npdates)
    pdf.index.name='Date'
    return pdf

#######################################################################################################
#                           INFORMATIONAL - UPDATE RELATED
#######################################################################################################


def last_database_update_time(databasename):
    url = build_api_url('database',databasename + '/lastupdatetime',None);
    try:
        r = httppool.request('GET', url,fields)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Database " + databasename + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    result = str(r.data);
    return result

def last_price_update_time(symbol):
    url = build_api_url('security',symbol + '/lastupdatetime',None);
    try:
        r = httppool.request('GET', url,fields)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Symbol " + symbol + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    result = str(r.data);
    return result

#######################################################################################################
#                           WATCHLIST
#######################################################################################################


def watchlist_symbols(watchlistname):
    url = build_api_url('watchlist',watchlistname,None);
    try:
        r = httppool.request('GET', url,fields)
    except Exception:
        log.exception("Exception raised reading Norgate Data.")
        raise ValueError("Unable to obtain Norgate Data - perhaps NDU is not running?")
    if (r.status == 404):
        raise ValueError("Watchlist " + watchlistname + " was not found");
    if (r.status != 200):
        raise ValueError("Error in receiving Norgate Data - check paramters are correctly formatted");
    symbols = r.data.decode().splitlines()
    return symbols

#######################################################################################################
#                           FUNDAMENTALS
#######################################################################################################

def fundamental(symbol,field):  # This returns both the field and date
    return "TODO"

#######################################################################################################
#                           CLASSIFICATION RELATED
#######################################################################################################

def classification(symbol,schemename,classificationresulttype):
    return "TODO"

def classification_at_level(symbol,schemename,classificationresulttype,level):
    return "TODO"

def corresponding_industry_index(symbol,indexfamilycode,level,indexreturntype):
    return "TODO"




#######################################################################################################
# Ignore after this - just for test
#######################################################################################################

#print ('starting grab of 1000 GE from 20190101 onwards...')
#print(datetime.datetime.now())
#a = assetid('GE');
#print (a);

#for x in range(100):
#    pdf = price_timeseries(symbol="GE",
#                                stock_price_adjustment_setting=StockPriceAdjustmentType.CAPITALSPECIAL,
#                                padding_setting=PaddingType.NONE,
#                                start_date="2019-01-01",
#                                end_date="today")
#    print (pdf)

#print(datetime.datetime.now())

#datetime.datetime.now()
a = index_constituent_timeseries(symbol='GE',indexname='$SPX',limit=10)
print(a)
print('hi')
