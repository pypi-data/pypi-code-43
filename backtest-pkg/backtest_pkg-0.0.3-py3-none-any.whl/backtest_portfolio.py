import pandas as pd

class portfolio:
    def __init__(self, weight=None, share=None, benchmark=None, end_date=None):
        '''
        weight: a df with row-names date, col-name security id, value the portfolio weight (not necessarily normalized) of col-security at row-date. 
        share: a df with row-names date, col-name security id, value the portfolio shares of col-security at row date. 
        benchmark: a df with row-names date, col-name security id, value the benchmark weight. 
        end_date: date to end backtest 
        '''
        self.weight = weight
        self.share = share
        self.benchmark = benchmark
        self.end_date = end_date


    def set_price(self, price_data):
        '''
        price_data: a df with row-names date, col-name security id, value the price of col-security at row date. 
        '''
        self.price = price_data

    def get_price(self, tickers, start_date, end_date):
        '''
        Download price data from Bloomberg. Ensusre a bloomberg connection is valid and the library pdblp is installed.
        tickers: a list of Bloomberg tickers in the universe.
        start_date: start date of the price data
        end_date: end date of the price data
        '''
        pass


    def backtest(self, price_data=None, trading_status=None, start_date=None, end_date=None):
        '''
        Backtest based on given price data over given period.
        price_data: a df with row-names date, col-name security id, value the price of col-security at row date. 
        trading_status: a df with row-names date, col-name security id, boolean value if the security is available for trade. 
        start_date: date to start the backtest. Default choice is the first date of self.weight.
        end_date: date to end the backtest. Default choice is the last date of price_date.
        '''
    
    def _weight_from_share(self, price_data=None):
        pass
    
    def _weight_extend(self):
        pass

    def performance_summary(self, start_date=None, end_date=None):
        '''
        Provide a table of total return, volitility, Sharpe ratio, max draw-down for portfoilo, benchmark and active weight.
        '''
        pass
    
    def performance_plot(self, start_date=None, end_date=None):
        '''
        Plot 2 figures:
        1. The portfolio return and benchmark return over backtest period.
        2. The active return over the backtest period.
        '''