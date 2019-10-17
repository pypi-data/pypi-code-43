text1 = """
import requests
import pprint
import tushare
import pandas as pd
'''
Tushare金融大数据接口调用代码
接口网址：https: // tushare.pro/document/2
'''
# 格式化输出
pp = pprint.PrettyPrinter(width=80)
# apiURL
url = 'http://api.waditu.com'
token = '6cb93350f16e743007b2499fdea415eb456f9430254441ee110c5d12'
def get_info(api_name, params, fields_en, fields_zh):
    '''
获得接口数据
'''
    data = {
        'api_name': api_name,
        'token': token,
        'params': params,
        'fields': fields_en,
    }
    # 获得数据
    info = requests.post(url, json=data)
    # pp.pprint(info.json()['data']['items'])
    fields = info.json()['data']['fields']
    # pp.pprint(info.json()['data']['items'])
    data = info.json()['data']['items']
    # 初始化数据帧
    df = pd.DataFrame(data, columns=fields_zh)
    # df = pd.DataFrame(data, columns=fields)
    print(df)
    return df
def pd2excel(df):
    df.to_excel('output.xlsx', na_rep='', index=False)
    return
if __name__ == '__main__':
    # 接口名称
    api_name = 'monthly'
    # 输入参数
    params = {
        'ts_code': '601588.SH',
        'trade_date': '20171229',
    }
    # 字段列表
    fields_en = "ts_code,trade_date,close"
    fields_zh = ['股票代码', '交易日期', '月收盘价']
    df = get_info(api_name, params, fields_en, fields_zh)
    # 向excel输出
    pd2excel(df)
"""
text2 = """
import tushare as ts
import pandas as pd
import pprint

pro = ts.pro_api('your token')


def get_info(ts_code):
    # df = pro.index_monthly(ts_code=ts_code, start_date='20130101', end_date='20171231', fields='ts_code,trade_date,close')
    # df = pro.monthly(ts_code=ts_code, start_date='20070101', end_date='20071231', fields='ts_code,trade_date,close')
    # df = ts.pro_bar(ts_code=ts_code, freq='M', adj='hfq', start_date='20130101', end_date='20171231')
    df = pro.daily(ts_code=ts_code, start_date='20171201',end_date='20180101', fields='ts_code,trade_date,close,vol,amount')
    # df = pro.hk_hold(ts_code=ts_code,trade_date='20151231', exchange='SH')
    return df


def pd2excel(df):
    df.to_excel('output.xlsx', na_rep='', index=False)
    return


if __name__ == '__main__':
    ts_code = "600177.SH"
    df = get_info(ts_code)
    pprint.pprint(df)
    pd2excel(df)
"""
