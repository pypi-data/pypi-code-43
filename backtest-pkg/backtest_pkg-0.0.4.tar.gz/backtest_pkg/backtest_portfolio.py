import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import warnings
from math import sqrt

def weight_drifting(initial_weight, price_data, rebalanced_weight=None, trading_status=None, end=None):
    '''
    initial_weight and rebalanced_weight should have same index and columns
    '''
    # Prepare end of drifting period:
    if end is None:
        end = max(price_data.index)
    assert end <= max(price_data.index), 'Invalid end date!'
    # Prepare trading status:
    if trading_status is None:
        trading_status = price_data.loc[initial_weight.index,:].notnull()
    else:
        trading_status = trading_status.loc[initial_weight.index, initial_weight.columns]
    
    assert initial_weight.shape[0]==1, 'Please specify only 1 initial weight!'
    assert trading_status.shape[0]==1
    assert (initial_weight.index == trading_status.index).all()
    assert (initial_weight.columns == trading_status.columns).all()

    # Rebalance:
    initial_weight = initial_weight.div(initial_weight.sum(axis=1), axis=0)  # Normalization
    if rebalanced_weight is None:
        weight = initial_weight
    else:
        assert rebalanced_weight.shape[0]==1, 'Please specify only 1 rebalanced weight!'
        assert (initial_weight.index == rebalanced_weight.index).all(), 'Please specify both weights in the same date!'
        assert (initial_weight.columns == rebalanced_weight.columns).all(), 'Please specify both weights in the same universe!'
        carry_weight = initial_weight.where(~trading_status, other=0)
        weight = carry_weight.copy()
        carry_weight_total = carry_weight.sum(axis=1)[0]
        if carry_weight_total<1:
            rebalanced_weight = rebalanced_weight.where(trading_status, other=0)
            rebalanced_weight = rebalanced_weight.div(rebalanced_weight.sum(axis=1), axis=0)*(1-carry_weight_total)
            weight.loc[:,:] = np.where(trading_status, rebalanced_weight, weight)
        else:
            weight = carry_weight

    # Drift:
    period = (price_data.index>=initial_weight.index[0]) & (price_data.index<=end)
    period_price = price_data.loc[period, :].ffill()
    period_price = period_price/period_price.values[0,:]
    period_price = period_price.fillna(0)
    drift_weight = period_price*weight.values
    drift_weight = drift_weight.div(drift_weight.sum(axis=1), axis=0)   #Normalization

    return drift_weight

def get_price_from_BB(tickers, start_date, end_date):
    'TBA'
    '''
    Download price data from Bloomberg. Ensusre a bloomberg connection is valid and the library pdblp is installed.
    tickers: a list of Bloomberg tickers in the universe.
    start_date: start date of the price data
    end_date: end date of the price data
    '''
    pass

def annualized_performance_metric(daily_ret_ts, tolerance=10**(-4), annual_trading_days=250):
    output = pd.Series()
    annualized_return= daily_ret_ts.prod()**(annual_trading_days/len(daily_ret_ts))-1
    output['Annualized_Return'] =annualized_return
    annualized_volatility = daily_ret_ts.std()*sqrt(annual_trading_days)
    if annualized_volatility < tolerance:
        annualized_volatility=np.nan
    output['Annualized_Volatility'] = annualized_volatility
    sharpe_ratio = annualized_return/annualized_volatility
    output['Annualized_Sharpe_Ratio'] = sharpe_ratio

    return output

def period_performance_metric(daily_ret_ts, tolerance=10**(-4)):
    output = pd.Series()
    period_return= daily_ret_ts.prod()-1
    output['Period_Return'] =period_return
    period_volatility = daily_ret_ts.std()*sqrt(len(daily_ret_ts))
    if period_volatility < tolerance:
        period_volatility=np.nan
    output['Period_Volatility'] = period_volatility
    sharpe_ratio = period_return/period_volatility
    output['Sharpe_Ratio'] = sharpe_ratio

    return output


def active_performance_metric(port_ret_ts, bm_ret_ts, tolerance=10**(-4)):
    assert (port_ret_ts.index == bm_ret_ts.index).all(), 'Two time series should be in the same period!'
    output = pd.Series()
    output['Active_Return'] = port_ret_ts.prod() - bm_ret_ts.prod()
    active_risk = (port_ret_ts-bm_ret_ts).std()*sqrt(len(port_ret_ts)) 
    if active_risk < tolerance:
        active_risk = np.nan
    output['Active_Risk'] = active_risk
    output['Information_Ratio'] = output['Active_Return']/output['Active_Risk']

    return output

class portfolio:
    '''
    The universe and the valid testing period will be defined by the price data.
    '''
    def __init__(self, weight=None, share=None, benchmark=None, end_date=None, name='Portfolio', benchmark_name='Benchmark'):
        '''
        weight: a df with row-names date, col-name security id, value the portfolio weight (not necessarily normalized) of col-security at row-date. 
        share: a df with row-names date, col-name security id, value the portfolio shares of col-security at row date. 
        benchmark: a df with row-names date, col-name security id, value the benchmark weight. 
        end_date: date to end backtest 
        name: the name of the portfolio
        '''
        self._weight = weight
        self.share = share
        # Construct a portfolio object if benchmark is given by weights:
        if isinstance(benchmark, pd.DataFrame):
            self.benchmark = portfolio(weight=benchmark, end_date=end_date, name=benchmark_name)
        elif isinstance(benchmark, portfolio) or (benchmark is None):
            self.benchmark = benchmark
        else:
            warnings.warn('Unknown benchmark type!')
            self.benchmark = None
        self._end_date = end_date
        self.name = name
        self.benchmark_name = benchmark_name

    @property
    def weight(self):
        '''
        Lazy calculate _weight given share and __price.
        '''
        if self._weight is None:
            # Default choice of share and price_data:
            price_data = self.__price.copy()
            assert price_data is not None, 'No price data!'        
            share = self.share.copy()
            assert share is not None, 'No share data!'

            # Check if the dates and tickers are valid:
            out_range_date = share.index.difference(price_data.index)
            if len(out_range_date)>0:
                warnings.warn(f'Skipping dates:\n{out_range_date.values}')
            unknown_ticker = share.columns.difference(price_data.columns)
            if len(unknown_ticker)>0:
                warnings.warn(f'Unkown tickers:\n{unknown_ticker.values}')
            # Only take intersection parts:
            share = share.loc[share.index & price_data.index, share.columns & price_data.columns]
            price_data = price_data.loc[share.index & price_data.index, share.columns & price_data.columns]

            # Construct the weights:
            weight = share * price_data
            weight = weight.div(weight.sum(axis=1), axis=0)
            self._weight = weight

        return self._weight

    @property
    def end_date(self):
        if self._end_date is None:
            self._end_date = max(self.__price.index)
        return self._end_date
    @end_date.setter 
    def end_date(self, value):
        self._end_date = value

    #########################    Price and related attributes   ############################
    def set_price(self, price_data, trading_status=None):
        '''
        price_data: a df with row-names date, col-name security id, value the price of col-security at row date. 
        trading_status: a df with row-names date, col-name security id, boolean value indicate if col-security is tradable at row-date. 
        '''
        # Price for backtesting is private attribute.
        self.__price = price_data
        self._trading_status = trading_status
        if self.benchmark:
            self.benchmark.__price = price_data
            self.benchmark._trading_status = trading_status

    @property
    def daily_ret(self):
        '''
        Lazy calculate _daily_ret from __price attribute.
        '''
        try:
            return self._daily_ret
        except AttributeError:
            self._daily_ret = self.__price.ffill()/self.__price.ffill().shift(1)
            self._daily_ret.iloc[0, :] = 1
            return self._daily_ret

    @property
    def trading_status(self): 
        '''
        Lazy calcuate _trading_status from __price.
        '''
        if self._trading_status is None:
            self._trading_status = self.__price.notnull() # Valid for trade only if price exists 
        return self._trading_status
    @trading_status.setter
    def trading_status(self, value):
        self._trading_status = value

    #####################  Backtesting methods   ####################
    @property
    def ex_weight(self):

        '''
        Drift the weight over given period.
        weight: The weight to extend, represented a df with row-names date, col-name security id, value the portfolio weight (not necessarily normalized) of col-security at row-date. Default choice is the weight of the portfolio.
        end_date: date to end the extension. Default choice is the end_date of the portfolio or the last date of price_data.
        '''
        try:
            return self._ex_weight
        except AttributeError:
            # Default weight and end_date:
            weight = self.weight.copy()
            end_date = self.end_date
            price_data = self.__price.copy()
            assert weight is not None, 'No weight data!'
            assert end_date is not None, 'Please specify the end of testing period!'
            assert price_data is not None, 'No price data!'

            # Prepare weight:
            out_range_date = weight.index.difference(price_data.index)
            if len(out_range_date)>0:
                warnings.warn(f'Skipping dates:\n{out_range_date.values}')
            unknown_ticker = weight.columns.difference(self.__price.columns)
            if len(unknown_ticker)>0:
                warnings.warn(f'Unkown tickers:\n{unknown_ticker.values}')
            rebalance_date = weight.index & price_data.index
            weight = weight.loc[rebalance_date, weight.columns&price_data.columns]

            # Prepare  price, trading_status, daily return:
            valid_period = price_data.index[(price_data.index>=min(rebalance_date)) & (price_data.index<=end_date)]
            price_data = price_data.loc[valid_period, weight.columns&price_data.columns]
            trading_status=self.trading_status.loc[price_data.index, price_data.columns]
            daily_ret=self.daily_ret.loc[price_data.index, price_data.columns]
            assert price_data.shape == trading_status.shape
            assert price_data.shape == daily_ret.shape

            # Extend weight:
            drifted_weight = weight.iloc[[0], :]
            for i in range(len(rebalance_date)):
                start = rebalance_date[i]
                if i+1<len(rebalance_date):
                    end = rebalance_date[i+1] 
                else:
                    end = end_date
                period_weight = weight_drifting(initial_weight=drifted_weight.tail(1), price_data=price_data, rebalanced_weight=weight.loc[[start], :], trading_status=trading_status.loc[[start], :],  end = end)
                drifted_weight = pd.concat([drifted_weight.iloc[:-1, :], period_weight], sort=False)

            self._ex_weight = drifted_weight
            return self._ex_weight

    @property
    def port_daily_ret(self):
        try:
            return self._port_daily_ret
        except AttributeError:
            daily_ret = self.daily_ret.copy()
            ex_weight = self.ex_weight
            daily_ret = daily_ret.loc[daily_ret.index&ex_weight.index, daily_ret.columns&ex_weight.columns]
            # Calculate portfolio daily return: 
            port_daily_ret = (ex_weight.shift(1)*daily_ret).sum(axis = 1)
            port_daily_ret[0] = 1
            self._port_daiy_ret = port_daily_ret
            return port_daily_ret
        
    @property 
    def port_total_ret(self):
        try:
            return self._port_total_ret
        except AttributeError:
            self._port_total_ret = self.port_daily_ret.cumprod()
            return self._port_total_ret

    def backtest(self, plot=False):
        '''
        Backtest portfolio performance over given period.
        '''
        # Setup price and trading status:
        port_total_ret_df = self.port_total_ret.to_frame(name=self.name)-1
        if self.benchmark:
            bm_total_ret_df = self.benchmark.port_total_ret.to_frame(name=self.benchmark.name)-1
        else:
            bm_total_ret_df = pd.DataFrame(0, index=port_total_ret_df.index, columns='Empty Portfolio')

        result = pd.concat([port_total_ret_df, bm_total_ret_df], axis=1, sort=False)
        result['Active Weight'] = result.iloc[:,0] - result.iloc[:,1]
        self.backtest_result = result
        
        if plot:
            self.performance_plot()

        return self.backtest_result
        

    ####################   Performance output   ##############################
    def performance_plot(self):
        '''
        Plot 2 figures:
        1. The portfolio return and benchmark return over backtest period.
        2. The active return over the backtest period.
        '''
        result = self.backtest_result
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (7, 10))
        # make a little extra space between the subplots
        fig.subplots_adjust(hspace=0.5)

        # Upper figure for total return:
        ax1.plot(result.iloc[:, 0], label=result.columns[0])
        ax1.plot(result.iloc[:, 1], label=result.columns[1])
        ax1.tick_params(axis='x', rotation=25)
        ax1.grid(color='grey', ls='--')
        ax1.legend()
        ax1.set_title('Total Return')
        # Lower figure for active return:
        ax2.plot(result.iloc[:, 2])
        ax2.tick_params(axis='x', rotation=25)
        ax2.grid(color='grey', ls='--')
        ax2.set_title('Active Return')

        plt.show() 
        # return fig    
    
    @property
    def performance_summary(self):
        '''
        Provide a table of total return, volitility, Sharpe ratio for portfoilo, benchmark and active weight.
        '''
        try:
            return self._performance_summary
        except AttributeError:
            summary_table=pd.DataFrame(columns=['Return', 'Volatility', 'Sharpe_Ratio'])
            port_metric = period_performance_metric(self.port_daily_ret)
            port_metric.index = summary_table.columns
            summary_table.loc[self.name, :] = port_metric
            bm_metric = period_performance_metric(self.benchmark.port_daily_ret) 
            bm_metric.index = summary_table.columns
            summary_table.loc[self.benchmark.name, :] = bm_metric
            active_metric = active_performance_metric(self.port_daily_ret, self.benchmark.port_daily_ret) 
            active_metric.index = summary_table.columns
            summary_table.loc['Active', :] = active_metric
            # Formatting before output:
            summary_table = summary_table.style.format({
                'Return': '{:,.2%}'.format,
                'Volatility': '{:,.2%}'.format,
                'Sharpe_Ratio': '{:,.2f}'.format,
            })

            self._performance_summary = summary_table
            return self._performance_summary

    @property
    def period_performance(self):
        try:
            return self._period_performance
        except AttributeError:
            # Prepare portfolio, benchmark, active return:
            port_ret= self.port_daily_ret
            bm_ret = self.benchmark.port_daily_ret
            daily_active_ret = port_ret - bm_ret
            # Label each period by rebalance date from weight attribute:
            period_ts = pd.Series(port_ret.index.map(lambda s: (s>self.weight.index).sum()), index=port_ret.index)
            period_ts.name = 'Period'
            # Calculate performance metric on each period:
            period_result = pd.DataFrame()
            period_result[self.name] = port_ret.groupby(period_ts).agg('prod') -1
            period_result[self.benchmark.name] = bm_ret.groupby(period_ts).agg('prod') -1
            period_result['Active Return'] = period_result[self.name] - period_result[self.benchmark.name]
            active_risk =  daily_active_ret.groupby(period_ts).agg(lambda s:s.std()*len(s) )
            tolerance = 10**(-5)
            active_risk[active_risk<tolerance] = np.nan
            period_result['Active Risk'] = active_risk
            period_result['Information Ratio'] = period_result['Active Return']/period_result['Active Risk']
            period_result = period_result.drop(index = 0)
            period_result = period_result.style.format('{:.2%}'.format)
            period_result = period_result.format({'Information Ratio': '{:,.2f}'.format})
            self._period_performance = period_result

            return self._period_performance

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

