from zipline.pipeline.filters import Filter
from zipline.pipeline.factors import Factor
from zipline.api import sid, symbol
from zipline.utils.numpy_utils import bool_dtype, repeat_first_axis

from functools import partial
from pprint import pprint # for debug only - remove for release
import numpy as np
import norgatedata 
import pandas as pd
import logbook

try:
    from multiprocessing import Process
except ImportError:
    _has_multiprocessing = False
else:
    _has_multiprocessing = True

logger = logbook.Logger('Norgate Data')

class NorgateDataIndexConstituent(Filter):
    """
    A Filter that computes True or False for whether a given asset was part of the index on a given day
    Parameters

    """
    window_length = 0
    inputs = []
    
    def __new__(cls, indexname):
        return super(NorgateDataIndexConstituent, cls).__new__(
            cls,
            indexname=indexname
        )    
    
    def _init (self, indexname, *args, **kwargs):
        self._indexname = indexname
        return super(NorgateDataIndexConstituent,self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, indexname, *args, **kwargs):
        return (
            super(NorgateDataIndexConstituent, cls)._static_identity(*args, **kwargs), indexname,
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info('Populating ' + self.__class__.__name__ + ' pipeline populating with ' + self._indexname + ' on ' + str(assets.size) + ' securities....' )
        norgatetimeseriesfunction = partial(norgatedata.index_constituent_timeseries,indexname=self._indexname)
        result = ConvertNorgateBoolTimeSeriesToFilter(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ' with ' + self._indexname + ': Done')
        return result




class NorgateDataMajorExchangeListed(Filter):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """
    window_length = 1
    inputs = []
    window_safe = True
    dependencies = {}
    
    def __new__(cls):
        return super(NorgateDataMajorExchangeListed, cls).__new__(
            cls
        )    
    
    def _init (self, *args, **kwargs):
        return super(NorgateDataMajorExchangeListed,self)._init(*args, **kwargs)
    
    @classmethod
    def _static_identity(cls,  *args, **kwargs):
        return (
            super(NorgateDataMajorExchangeListed, cls)._static_identity(*args, **kwargs)
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info('Pipeline ' + self.__class__.__name__ + ' populating on ' + str(assets.size) + ' securities' )
        norgatetimeseriesfunction = norgatedata.major_exchange_listed_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ': Done')
        return result

    #def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)	


class NorgateDataCapitalEvent(Filter):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """
    window_length = 1
    inputs = []
    window_safe = True
    dependencies = {}
    
    def __new__(cls):
        return super(NorgateDataCapitalEvent, cls).__new__(
            cls
        )    
    
    def _init (self, *args, **kwargs):
        return super(NorgateDataCapitalEvent,self)._init(*args, **kwargs)
    
    @classmethod
    def _static_identity(cls,  *args, **kwargs):
        return (
            super(NorgateDataCapitalEvent, cls)._static_identity(*args, **kwargs)
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info('Pipeline ' + self.__class__.__name__ + ' populating on ' + str(assets.size) + ' securities' )
        norgatetimeseriesfunction = norgatedata.capital_event_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ': Done')
        return result

    #def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)	


class NorgateDataPaddingStatus(Filter):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """
    window_length = 1
    inputs = []
    window_safe = True
    dependencies = {}
    
    def __new__(cls):
        return super(NorgateDataPaddingStatus, cls).__new__(
            cls
        )    
    
    def _init (self, *args, **kwargs):
        return super(NorgateDataPaddingStatus,self)._init(*args, **kwargs)
    
    @classmethod
    def _static_identity(cls,  *args, **kwargs):
        return (
            super(NorgateDataPaddingStatus, cls)._static_identity(*args, **kwargs)
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info('Pipeline ' + self.__class__.__name__ + ' populating on ' + str(assets.size) + ' securities' )
        norgatetimeseriesfunction = norgatedata.padding_status_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ': Done')
        return result

    #def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)	


class NorgateDataUnadjustedClose(Factor):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """
    window_length = 1
    dtype = np.float
    inputs = []
    window_safe = True
    def _compute(self, arrays, dates, assets, mask):
        logger.info('Pipeline ' + self.__class__.__name__ + ' populating on ' + str(assets.size) + ' securities' )
        norgatetimeseriesfunction = norgatedata.unadjusted_close_timeseries
        result = ConvertNorgateFloatTimeSeriesToFactor(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ': Done')
        return result

class NorgateDataDividendYield(Factor):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """
    window_length = 1
    dtype = np.float
    inputs = []
    window_safe = True
    def _compute(self, arrays, dates, assets, mask):
        logger.info('Pipeline ' + self.__class__.__name__ + ' populating on ' + str(assets.size) + ' securities' )
        norgatetimeseriesfunction = norgatedata.dividend_yield_timeseries
        result = ConvertNorgateFloatTimeSeriesToFactor(assets,norgatetimeseriesfunction,dates,mask)
        logger.info('Pipeline ' + self.__class__.__name__ + ': Done')
        return result

def ConvertNorgateBoolTimeSeriesToFilter(assets,norgatetimeseriesfunction,dates,mask):
    start_date = dates[0].to_pydatetime()
    end_date = dates[-1].to_pydatetime()
    # Raise an exception if `self._asset` does not exist for the entirety
    # of the timeframe over which we are computing.
    #if (is_my_asset.sum() != 1) or ((out & mask).sum() != len(mask)):
        #raise NonExistentAssetInTimeFrame(
        #    asset=self._asset, start_date=dates[0], end_date=dates[-1],
        #)
    out = np.full_like(mask,False,order='K') # Fill with false
    assetindexcounter = 0
    for zipline_assetid in assets:
        symbol = sid(zipline_assetid).symbol
        timeseries = norgatetimeseriesfunction(symbol=symbol,
            padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,
            format="numpy-recarray",
            start_date = start_date.strftime('%Y-%m-%d'),
            end_date = end_date.strftime('%Y-%m-%d') )
        column_name = timeseries.dtype.names[-1]
        counter = 0
        # TODO: Pythonize the following loop
        for x in dates:
            if counter > timeseries.size:
                break
            while counter < timeseries.size and pd.Timestamp(timeseries['Date'][counter],tz='UTC') < x:
                counter += 1
            if counter < timeseries.size and pd.Timestamp(timeseries['Date'][counter],tz='UTC') == x and timeseries[column_name][counter] == 1:
                out[counter][assetindexcounter] = True
        assetindexcounter+=1
    return out

def ConvertNorgateFloatTimeSeriesToFactor(assets,norgatetimeseriesfunction,dates,mask):
    start_date = dates[0].to_pydatetime()
    end_date = dates[-1].to_pydatetime()
    # Raise an exception if `self._asset` does not exist for the entirety
    # of the timeframe over which we are computing.
    #if (is_my_asset.sum() != 1) or ((out & mask).sum() != len(mask)):
        #raise NonExistentAssetInTimeFrame(
        #    asset=self._asset, start_date=dates[0], end_date=dates[-1],
        #)
    out = np.full_like(mask,np.nan,dtype=np.float,order='K') # Fill with NaN
    assetindexcounter = 0
    for zipline_assetid in assets:
        symbol = sid(zipline_assetid).symbol
        timeseries = norgatetimeseriesfunction(symbol=symbol,
            padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,
            format="numpy-recarray",
            start_date = start_date.strftime('%Y-%m-%d'),
            end_date = end_date.strftime('%Y-%m-%d') )
        column_name = timeseries.dtype.names[-1]
        # TODO: Pythonize the following loop
        counter = 0
        for x in dates:
            if counter > timeseries.size:
                break
            while counter < timeseries.size and pd.Timestamp(timeseries['Date'][counter],tz='UTC') < x:
                counter += 1
            if counter < timeseries.size and pd.Timestamp(timeseries['Date'][counter],tz='UTC') == x:
                out[counter][assetindexcounter] = timeseries[column_name][counter]
        assetindexcounter+=1
    return out
