import os
import math
from builds.asset import asset_factory
import pandas as pd

def bloomberg2asset(bloomberg_symbol, name=None, filter_ks=True):
    str = bloomberg_symbol.split()
    symbol, exchange = str[0], str[1]
    source = 'naver' if exchange == 'KS' and filter_ks == True else 'yahoo'
    symbol = symbol.replace("/", "-")
    asset = asset_factory(symbol=symbol, exchange=exchange, source=source) if name is None \
        else asset_factory(symbol=symbol, exchange=exchange, source=source, name=name)
    return asset


def extract_years(df):
    current_year = int(df.index[0].strftime("%Y"))
    last_year = int(df.index[-1].strftime("%Y"))

    years = []

    while current_year <= last_year:
        years.append(current_year)
        current_year += 1

    return years

def split_yearly(df, method='ffill'):
    years = extract_years(df)

    date_range = pd.date_range('1999-01-01', '1999-12-31')
    yearly_data = pd.DataFrame(index=[date.strftime("%m-%d") for date in date_range])

    for year in years:
        single_year_data = df.loc['{}-01-01'.format(year): '{}-01-01'.format(year + 1)]
        for idx, row in single_year_data.iteritems():
            yearly_data.loc[yearly_data.index == idx.strftime("%m-%d"), str(year)] = row

    return yearly_data.fillna(method=method)

def convert_str2num(string):
    try:
        return float(string.replace(',', ''))
    except:
        if '%' in string:
            return float(string.strip('%')) / 100
        else:
            return string

def find_key_by_val(dic, val):
    for key, value in dic.items():
        if val == value:
            return key
    return "key doesn't exist"

def get_project_dir():
    return os.path.dirname(os.path.realpath(__file__))

def ks_stock_symbols(symbols, in_type='default', out_type='bloomberg'):
    """
    Symbol을 Bloomberg 혹은 Quantiwise(Cybos) Symbol로 변환
    """
    if in_type == 'default':
        if out_type == 'padding': # Zero padding
            for i, code in enumerate(symbols):
                n_str = len(str(code))
                for _ in range(6-n_str):
                    symbols[i] = "0" + symbols[i]
            return symbols
    elif in_type == 'bloomberg':
        symbols = [symbol[:6] for symbol in symbols]

    elif in_type == 'quantiwise':
        symbols = [symbol[1:] for symbol in symbols]

    else:
        raise Exception

    if out_type == 'default':
        pass

    elif out_type == 'bloomberg':
        symbols = ['{} KS Equity'.format(symbol[:]) for symbol in symbols]

    elif out_type == 'quantiwise':
        symbols = ['A{}'.format(symbol[:]) for symbol in symbols]

    else:
        raise Exception

    return symbols

def is_nan(x):
    return isinstance(x, float) and math.isnan(x)

def is_inf(x):
    return isinstance(x, float) and math.isinf(x)
