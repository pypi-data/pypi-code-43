import tushare as ts

from fundquant.util.dateutil import today_plus, today


def etf_daily(index_code, n_days):
    pro = ts.pro_api(token="65ff56dd66d10436614eefa5a87498c265acb97fdb8be9937c4f2d80")
    df = pro.fund_daily(ts_code=index_code, start_date=today_plus(-n_days), end_date=today())

    return df
