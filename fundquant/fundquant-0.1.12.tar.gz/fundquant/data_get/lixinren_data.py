import json
import typing

import pymysql
import requests

from fundquant.util import dateutil


class LixinrenData:
    def __init__(self, cookie: str = ''):
        if cookie == '':
            self.cookie = 'Hm_lpvt_ec0ee7e5c8bed46d4fdf3f338afc08f5=1570366339; Hm_lvt_ec0ee7e5c8bed46d4fdf3f338afc08f5=1570365687,1570365703; jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1Y2IxNzIxNzIzM2RiNTc3MzIwMGFkZGIiLCJpYXQiOjE1NzAzNjU3MDIsImV4cCI6MTU3MTU3NTMwMn0.AuG8gVS0qK82XMOT47vmPGQn940J0GdGgHBABV9pqjU'
        else:
            self.cookie = cookie

        self.headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Cookie": self.cookie,
            "Accept": "application/json, text/plain, */*",
            "Host": "www.lixinger.com",
            "Accept-Language": "zh-cn",
            "Origin": "https://www.lixinger.com",
            "Connection": "keep-alive",
            "Accept-Encoding": "br, gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15",
            "Refer": "https://www.lixinger.com/analytics/indice/sh/000300/detail/value"
        }

    def get_index_data(self, stock_id: int, metrics: list = ['pe_ttm', 'pb'], granularity='y_5'):
        """

        :param stock_id: int
        :param metrics: default ['pe_ttm', 'pb']
        :param 全部:f_s 10年:y_10 5年:y_5 3年:y_3
        :return:
        """
        url = 'https://www.lixinger.com/api/analyt/stock-collection/price-metrics/load'

        # post_data = {"stockIds": [stock_id], "granularity": "f_s", "metricTypes": ["weightedAvg"],
        #              "leftMetricNames": [metrics], "rightMetricNames": ["cp"]}

        post_data = {"stockIds": [stock_id], "dateFlag": "day", "granularity": granularity,
                     "metricNames": ["pe_ttm", "pb"], "metricTypes": ["weightedAvg"]}

        r = requests.post(url, headers=self.headers, data=json.dumps(post_data)).json()
        return r

    def get_all_index_code(self):
        url = 'https://www.lixinger.com/api/analyt/stock-collection/price-metrics/indices/latest'

        post_data = {"metricNames": ["pe_ttm", "pb", "ps_ttm", "dyr"], "granularities": ["f_s"],
                     "metricTypes": ["weightedAvg"]}

        r = requests.post(url, headers=self.headers, data=json.dumps(post_data)).json()
        return r

    def get_macro_debt(self, n_years: int = 10):
        url = 'https://www.lixinger.com/api/analyt/macro'

        start_date = dateutil.today_plus(-n_years * 365, '%Y-%m-%dT%H:%M:%S.000Z')
        end_date = dateutil.today_plus(0, '%Y-%m-%dT%H:%M:%S.000Z')

        post_data = {"startDate": start_date, "endDate": end_date,
                     "type": "national_debt",
                     "metricNames": ["interestRate1y", "interestRate3y", "interestRate5y", "interestRate10y"]}

        r = requests.post(url, headers=self.headers, data=json.dumps(post_data)).json()
        return r

    def get_macro_m2(self, n_years: int = 10) -> typing.List[typing.Dict]:
        url = 'https://www.lixinger.com/api/analyt/macro'

        start_date = dateutil.today_plus(-n_years * 365, '%Y-%m-%dT%H:%M:%S.000Z')
        end_date = dateutil.today_plus(0, '%Y-%m-%dT%H:%M:%S.000Z')

        post_data = {"startDate": start_date, "endDate": end_date,
                     "type": "statistics_office", "metricNames": ["m2", "m1", "m0"]}

        r = requests.post(url, headers=self.headers, data=json.dumps(post_data)).json()
        return r

    def get_macro_price_indexs(self, n_years: int = 10) -> typing.List[typing.Dict]:
        url = 'https://www.lixinger.com/api/analyt/macro'

        start_date = dateutil.today_plus(-n_years * 365, '%Y-%m-%dT%H:%M:%S.000Z')
        end_date = dateutil.today_plus(0, '%Y-%m-%dT%H:%M:%S.000Z')

        post_data = {"startDate": start_date, "endDate": end_date,
                     "type": "statistics_office",
                     "metricNames": ["hci", "rrci", "urci", "cpi", "ucpi", "rcpi", "ppi", "pppi", "mi_pmi", "c_pmi"]}

        r = requests.post(url, headers=self.headers, data=json.dumps(post_data)).json()
        return r


class LixinrenPersist:
    def __init__(self, cookie: str = ''):
        self.api = LixinrenData(cookie)

    @staticmethod
    def _get_recur(dic: dict, default, *keys_recurse):
        for k in keys_recurse:
            if dic.get(k) is None:
                return default
            dic = dic.get(k)

        if dic is None:
            return default
        return dic

    @staticmethod
    def _upsert_pe_pb(index_code: str, dt: str, pe: float, pb: float):
        """

        :param index_code:
        :param dt:
        :param pe:
        :param pb:
        :return:
        """
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into index_data(`index_code`, `dt`, `pe`, `pb`) " \
                  "values('{}', '{}', {}, {}) " \
                .format(index_code, dt, pe, pb)

            cursor.execute(sql)
        except Exception as e:
            cursor = conn.cursor()
            sql = "update index_data set pe={}, pb={} where index_code='{}' and dt='{}' " \
                .format(pe, pb, index_code, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    @staticmethod
    def _upsert_index_track(stock_id: int, index_code: str, index_name: str, exchange: str):
        """

        :param stock_id:
        :param index_code:
        :param index_name:
        :param exchange:
        :return:
        """
        if exchange is not None:
            exchange = exchange.upper()

        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into index_track_list(`index_code`, `index_name`, `lixinren_stock_id`, `exchange`) " \
                  "values('{}', '{}', {}, '{}') " \
                .format(index_code, index_name, stock_id, exchange)

            cursor.execute(sql)
        except Exception as e:
            cursor = conn.cursor()
            sql = "update index_track_list set index_name='{}', lixinren_stock_id={}, exchange='{}' " \
                  "where index_code='{}' " \
                .format(index_name, stock_id, exchange, index_code)
            cursor.execute(sql)
        finally:
            conn.commit()

    @staticmethod
    def _upsert_macro_debt(dt: str, rate_1y: float, rate_3y: float, rate_5y: float, rate_10y: float,
                           debt_type: str = 'national_debt'):
        """

        :param dt:
        :param rate_1y:
        :param rate_3y:
        :param rate_5y:
        :param rate_10y:
        :param debt_type:
        :return:
        """
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into macro_debt(`type`, `dt`, `interest_rate_1y`, `interest_rate_3y`, " \
                  " `interest_rate_5y`, `interest_rate_10y`) " \
                  "values('{}', '{}', {}, {}, {}, {}) " \
                .format(debt_type, dt, rate_1y, rate_3y, rate_5y, rate_10y)

            cursor.execute(sql)
        except Exception as e:
            cursor = conn.cursor()
            sql = "update macro_debt set interest_rate_1y={}, interest_rate_1y={}, " \
                  " interest_rate_1y={}, interest_rate_1y={} " \
                  "where type='{}' and dt='{}' " \
                .format(rate_1y, rate_3y, rate_5y, rate_10y, debt_type, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    @staticmethod
    def _upsert_macro_m2(dt: str, m2: float, m1: float, m0: float, m_type: str = 'statistics_office'):
        """

        :param dt:
        :param m2:
        :param m1:
        :param m0:
        :param m_type:
        :return:
        """
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into macro_m2(`type`, `dt`, `m2`, `m1`, `m0`) " \
                  "values('{}', '{}', {}, {}, {}) " \
                .format(m_type, dt, m2, m1, m0)

            cursor.execute(sql)
        except Exception as e:
            cursor = conn.cursor()
            sql = "update macro_m2 set m2={}, m1={}, m0={} " \
                  "where type='{}' and dt='{}' " \
                .format(m2, m1, m0, m_type, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    @staticmethod
    def _upsert_macro_price_indexs(dt: str, cpi: float, ucpi: float, rcpi: float, ppi: float, pppi: float,
                                   mi_pmi: float, c_pmi, item, m_type: str = 'statistics_office'):
        """

        :param dt:
        :param cpi:
        :param ucpi:
        :param rcpi:
        :param ppi:
        :param pppi:
        :param mi_pmi:
        :param c_pmi:
        :param m_type:
        :return:
        """
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into macro_price_indexs(`type`, `dt`, `cpi`, `ucpi`, `rcpi`, `ppi`, " \
                  " `pppi`, `mi_pmi`, `c_pmi`) " \
                  "values('{}', '{}', {}, {}, {}, {}, {}, {}, {}) " \
                .format(m_type, dt, cpi, ucpi, rcpi, ppi, pppi, mi_pmi, c_pmi)

            cursor.execute(sql)
        except Exception as e:

            c_pmi = LixinrenPersist._get_recur(item, 0, 'c_pmi', 'month', 'c')
            cursor = conn.cursor()
            sql = "update macro_price_indexs set cpi={}, ucpi={}, rcpi={}, ppi={}, pppi={}, mi_pmi={}, c_pmi={} " \
                  "where type='{}' and dt='{}' " \
                .format(cpi, ucpi, rcpi, ppi, pppi, mi_pmi, c_pmi, m_type, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    def _persist_index_data(self, stock_id: int, index_code: str, index_name: str, exchange: str):
        """

        :param stock_id:
        :param index_code:
        :param index_name:
        :param exchange:
        :return:
        """
        lists = self.api.get_index_data(stock_id)
        for item in lists:
            dt = item['date'][0:10]
            pe = self._get_recur(item, 0, 'pe_ttm', 'weightedAvg')
            pb = self._get_recur(item, 0, 'pb', 'weightedAvg')
            self._upsert_pe_pb(index_code, dt, pe, pb)
            self._upsert_index_track(stock_id, index_code, index_name, exchange)

    def persist_all_index_data(self):
        code_list = self.api.get_all_index_code()
        for item in code_list:
            try:
                stockId = item['stockId']
                index_code = item['stockCode']
                index_name = item['cnName']
                exchange = item['exchange']

                self._persist_index_data(stockId, index_code, index_name, exchange)
                print('persist:', index_code)
            except Exception as e:
                print(item)
                print(e)

    def persist_macro_debt(self):
        debt_list = self.api.get_macro_debt(20)
        for item in debt_list:
            dt = item['date'][0:10]
            debt_type = item['type']
            rate_1y = item['interestRate1y']
            rate_3y = item['interestRate3y']
            rate_5y = item['interestRate5y']
            rate_10y = item['interestRate10y']
            self._upsert_macro_debt(dt, rate_1y, rate_3y, rate_5y, rate_10y, debt_type)

    def persist_macro_m2(self):
        m2_list = self.api.get_macro_m2(20)
        for item in m2_list:
            dt = item['date'][0:10]
            m_type = item['type']

            if item.get('m2') is None:
                continue

            m2 = item['m2']['month']['t_y2y']
            m1 = item['m1']['month']['t_y2y']
            m0 = item['m0']['month']['t_y2y']
            self._upsert_macro_m2(dt, m2, m1, m0, m_type)

    def persist_macro_price_indexs(self):
        m2_list = self.api.get_macro_price_indexs(20)
        for item in m2_list:
            dt = item['date'][0:10]
            m_type = item['type']

            if item.get('cpi') is None:
                continue

            cpi = self._get_recur(item, 0, 'cpi', 'month', 'c_y2y')
            ucpi = self._get_recur(item, 0, 'ucpi', 'month', 'c_y2y')
            rcpi = self._get_recur(item, 0, 'rcpi', 'month', 'c_y2y')
            ppi = self._get_recur(item, 0, 'ppi', 'month', 'c_y2y')
            pppi = self._get_recur(item, 0, 'pppi', 'month', 'c_y2y')
            mi_pmi = self._get_recur(item, 0, 'mi_pmi', 'month', 'c')
            c_pmi = self._get_recur(item, 0, 'c_pmi', 'month', 'c')

            self._upsert_macro_price_indexs(dt, cpi, ucpi, rcpi, ppi, pppi, mi_pmi, c_pmi, item, m_type)


def persist_all_data_hand(cookie):
    lxr = LixinrenPersist(cookie)
    lxr.persist_all_index_data()
    lxr.persist_macro_debt()
    lxr.persist_macro_m2()
    lxr.persist_macro_price_indexs()


if __name__ == '__main__':
    p = LixinrenPersist()
    p.persist_macro_debt()
    p.persist_macro_m2()
    p.persist_macro_price_indexs()
    p.persist_all_index_data()
