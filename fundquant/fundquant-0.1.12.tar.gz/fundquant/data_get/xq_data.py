import json
import time
from datetime import datetime as datetime_type
from datetime import timedelta
from typing import List

import numpy as np
import pandas
import pymysql
import requests
from fundquant.util import dateutil
from requests.cookies import RequestsCookieJar

# 代码页加入以下这个
import requests.packages.urllib3
# 禁用安全请求警告
from urllib3.exceptions import InsecureRequestWarning

from fundquant.domain.index_track import IndexTrackConfig

requests.urllib3.disable_warnings(InsecureRequestWarning)


def get_xueqiu_cookies() -> RequestsCookieJar:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Origin": "https://xueqiu.com",
        "Accept-Encoding": "br, gzip, deflate",
        "Host": "xueqiu.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
        "Accept-Language": "en-us",
        "Referer": "https://xueqiu.com/",
        "Connection": "keep-alive"
    }

    return requests.get(url="https://xueqiu.com", headers=headers, timeout=30, verify=False).cookies


class XqApi(object):
    """
    雪球股票数据
    """

    def __init__(self):
        self._init_cookies_jar = get_xueqiu_cookies()
        self._default_indicator = ['kline']
        self.__default_column = ['symbol', 'date', "timestamp", 'volume', 'open', 'high', 'low', 'close', 'chg',
                                 'percent', 'turnoverrate', 'amount', 'pe', 'pb']

    def get_his_k_data(
            self,
            symbol: str,
            start_date_str: str,
            end_date_str: str,
            period: str = 'day',
            return_column: List[str] = None,
            log_flag: bool = False
    ) -> pandas.DataFrame:
        """
        default kline
        all [kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance]
        :param symbol: 代码
        :param start_date_str: 起始时间 20190310
        :param end_date_str: 结束时间 20190320
        :param period: day week month quarter year
        :param log_flag

        :param return_column: 需要返回的列
        :return: 返回列数据
                 symbol:标的物
                 timestamp:时间戳,
                 volume:成交量(手),
                 open:开盘价
                 high:最高价
                 low:最低价
                 close:收盘价
                 chg:涨跌额
                 percent:涨跌幅度 25.0%
                 pe:市盈率
                 pb:市净率
        """
        if return_column is None:
            return_column = self.__default_column
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://xueqiu.com",
            "Accept-Encoding": "br, gzip, deflate",
            "Host": "stock.xueqiu.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
            "Accept-Language": "en-us",
            # "Referer": "https://xueqiu.com/S/SH510300",
            "Connection": "keep-alive"
        }

        start_of_today = datetime_type.strptime(start_date_str, "%Y%m%d") + timedelta(minutes=1)
        end_of_today = datetime_type.strptime(end_date_str, "%Y%m%d") + timedelta(days=1) - timedelta(minutes=1)

        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?" \
              "symbol=" + str(symbol) + \
              "&begin=" + str(int(start_of_today.timestamp() * 1000)) + \
              "&end=" + str(int(end_of_today.timestamp() * 1000)) + \
              "&period=" + str(period) + \
              "&type=before" + \
              "&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        if log_flag:
            print("request url:%s", url)
        r = requests.get(url, headers=headers, cookies=get_xueqiu_cookies(), timeout=30, verify=False)
        result = json.loads(r.text)

        # if log_flag:
        #     print(result)
        if result['error_code'] == 1:
            raise BaseException(result['error_description'])

        data = result['data']
        if len(data) == 0:
            return pandas.DataFrame()

        if data['symbol'] != symbol:
            raise BaseException("返回symbol与目标symbol不一致")
        column = data['column']
        if len(data['item']) == 0:
            return pandas.DataFrame()
        df = pandas.DataFrame(data=data['item'], columns=column)
        df['symbol'] = pandas.Series(data=[symbol for i in range(df.size)])
        df['date'] = df['timestamp'].apply(lambda ts: time.strftime("%Y-%m-%d", time.localtime(int(ts / 1000))))
        df.set_index(keys=['date'], inplace=True)
        df['date'] = df.index

        return df[return_column]


class XqIndexData:
    def __init__(self):
        self.api = XqApi()

    @staticmethod
    def _upsert_index_data(index_code, dt, close_value):
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into index_data(`index_code`, `dt`, `close_value`) " \
                  "values('{}', '{}', {}) " \
                .format(index_code, dt, close_value)

            cursor.execute(sql)
        except:
            cursor = conn.cursor()
            sql = "update index_data set close_value={} where index_code='{}' and dt='{}' " \
                .format(close_value, index_code, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    def persist_all_data(self, n_days):
        for config in IndexTrackConfig.get_index_config():
            df = self.api.get_his_k_data(config.code_prefix + config.index_code,
                                         dateutil.today_plus(-n_days - 1), dateutil.today_plus(0),
                                         return_column=['symbol', 'date', 'close'])
            for item in df.values:
                dt = item[1]
                close_value = float(item[2])
                self._upsert_index_data(config.index_code, dt, close_value)
            time.sleep(60)

    @staticmethod
    def index_data_from_db(index_code, n_days):
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        index_code_list = []
        dt = []
        close_value = []
        pe = []
        pb = []
        try:
            cursor = conn.cursor()

            sql = "select index_code, dt, close_value, pe, pb from index_data " \
                  "where index_code='{}' and dt>='{}' and dt<='{}' and pe > 0 order by dt " \
                .format(index_code, dateutil.today_plus(-n_days, '%Y-%m-%d'), dateutil.today_plus(0, '%Y-%m-%d'))

            cursor.execute(sql)
            conn.commit()

            for item in cursor.fetchall():
                index_code_list.append(item[0])
                dt.append(item[1])
                close_value.append(item[2])
                pe.append(item[3])
                pb.append(item[4])

            df = pandas.DataFrame(data=np.array([index_code_list, dt, close_value, pe, pb]).T,
                                  columns=['index_code', 'dt', 'close_value', 'pe', 'pb'])
            return df.set_index('dt')
        except:
            pass


if __name__ == '__main__':
    q = XqIndexData()
    q.persist_all_data(3600)
