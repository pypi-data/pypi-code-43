import time

import pandas
import numpy as np
import pymysql
import requests
from fundquant.util import dateutil


class JslEtf:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Host": "www.jisilu.cn",
        "Accept-Language": "en-us",
        "Origin": "https://www.jisilu.cn",
        "Connection": "keep-alive",
        "Accept-Encoding": "br, gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
    }

    def _etf_list_online(self, page=1, page_size=50):
        url = "https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___t={}&page={}&rp={}".format(int(time.time() * 1000),
                                                                                                page, page_size)
        r = requests.get(url=url, headers=self.headers).json()
        return r['rows']

    @staticmethod
    def _etf_data_online(etf_code, page=1, page_size=50):
        url = "https://www.jisilu.cn/data/etf/detail_hists/?___jsl=LST___t={}".format(int(time.time() * 1000))
        post_data = {
            'is_search': 1, 'fund_id': etf_code,
            'rp': page_size, 'page': page
        }

        r = requests.post(url, data=post_data).json()['rows']
        return r

    def persist_etf_list(self):
        list = self._etf_list_online(1, 500)
        for etf in list:
            cell = etf['cell']
            etf_code = cell['fund_id']
            etf_name = cell['fund_nm']
            index_id = cell['index_id']
            index_name = cell['index_nm']

            self._upsert_etf2db(etf_code, etf_name, index_id, index_name)

    @staticmethod
    def _upsert_etf2db(etf_code, etf_name, index_id, index_name):
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        try:
            cursor = conn.cursor()

            sql = "insert into jsl_etf_list(`etf_code`, `etf_name`, `index_id`, `index_name`) " \
                  "values('{}', '{}', '{}', '{}')" \
                .format(etf_code, etf_name, index_id, index_name)

            cursor.execute(sql)
        except:
            cursor = conn.cursor()
            sql = "update jsl_etf_list set etf_name='{}', index_id='{}', index_name='{}' " \
                  "where etf_code='{}' " \
                .format(etf_name, index_id, index_name, etf_code)
            cursor.execute(sql)
        finally:
            conn.commit()

    @staticmethod
    def _upsert_etf_data2db(etf_code, index_id, dt, close_price, fund_nav, discount_rt, incr_rate, pe, pb):
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        # 更新etf_data
        try:
            cursor = conn.cursor()

            sql = "insert into jsl_etf_data(`etf_code`, `dt`, `close_price`, `fund_nav`, `discount_rt`, " \
                  " `incr_rt`, `pe`, `pb`) " \
                  "values('{}', '{}', {}, {}, '{}', '{}', {}, {})" \
                .format(etf_code, dt, close_price, fund_nav, discount_rt, incr_rate, pe, pb)

            cursor.execute(sql)
        except:
            cursor = conn.cursor()
            sql = "update jsl_etf_data set close_price={}, fund_nav={}, discount_rt='{}', incr_rt='{}', pe={}, pb={} " \
                  "where etf_code='{}' and dt='{}' " \
                .format(close_price, fund_nav, discount_rt, incr_rate, pe, pb, etf_code, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

        # 更新index_data
        if index_id is None or index_id == '':
            return

        try:
            cursor = conn.cursor()

            sql = "insert into index_data(`index_code`, `dt`, `pe`, `pb`) " \
                  "values('{}', '{}', {}, {})" \
                .format(index_id, dt, pe, pb)

            cursor.execute(sql)
        except:
            cursor = conn.cursor()
            sql = "update index_data set pe={}, pb={} " \
                  "where index_code='{}' and dt='{}' " \
                .format(pe, pb, index_id, dt)
            cursor.execute(sql)
        finally:
            conn.commit()

    def persist_etf_data(self, etf_code, index_id, page=1, page_size=50):
        etf_data = self._etf_data_online(etf_code, page, page_size)
        for l in etf_data:
            cell = l['cell']
            dt = cell['hist_dt']
            close_price = float(cell['trade_price']) if cell['trade_price'] is not None else 0
            fund_nav = float(cell['fund_nav']) if cell['fund_nav'] is not None else 0
            discount_rt = str(cell['discount_rt'])
            incr_rate = str(cell['idx_incr_rt'])
            pe = float(cell['idx_pe']) if cell['idx_pe'] is not None else 0
            pb = float(cell['idx_pb']) if cell['idx_pb'] is not None else 0
            self._upsert_etf_data2db(etf_code, index_id, dt, close_price, fund_nav, discount_rt, incr_rate, pe, pb)

    def persist_all_data(self):
        self.persist_etf_list()
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        cursor = conn.cursor()
        sql = 'select etf_code, index_id from jsl_etf_list'
        cursor.execute(sql)
        for item in cursor.fetchall():
            self.persist_etf_data(item[0], item[1])

    @staticmethod
    def etf_data_from_db(etf_code, n_days=7200):
        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        etf_code_list = []
        dt = []
        close_price = []
        fund_nav = []
        discount_rt = []
        incr_rt = []
        pe = []
        pb = []
        try:
            cursor = conn.cursor()

            sql = "select etf_code, dt, close_price, fund_nav, discount_rt, incr_rt, pe, pb from jsl_etf_data " \
                  "where etf_code='{}' and dt>='{}' and dt<='{}' order by dt " \
                .format(etf_code, dateutil.today_plus(-n_days, '%Y-%m-%d'), dateutil.today_plus(0, '%Y-%m-%d'))

            cursor.execute(sql)
            conn.commit()

            for item in cursor.fetchall():
                etf_code_list.append(item[0])
                dt.append(item[1])
                close_price.append(item[2])
                fund_nav.append(item[3])
                discount_rt.append(item[4])
                incr_rt.append(item[5])
                pe.append(item[6])
                pb.append(item[7])

            df = pandas.DataFrame(
                data=np.array([etf_code_list, dt, close_price, fund_nav, discount_rt, incr_rt, pe, pb]).T,
                columns=['etf_code', 'dt', 'close_price', 'fund_nav', 'discount_rt', 'incr_rt', 'pe', 'pb'])
            return df.set_index('dt')
        except:
            pass


if __name__ == '__main__':
    j = JslEtf()
    data = j._etf_data_online('159920')
    print(data)
