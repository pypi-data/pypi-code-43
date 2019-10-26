import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from utils import convert_str2num, find_key_by_val

class NaverEvents:
    def __init__(self):
        self.URL = "https://finance.naver.com/item/main.nhn?code="
        self.fields_dic = {"DIVIDEND_YIELD": "배당수익률", "SHARESOUT": "상장주식수", "PER": "PER", "EPS": "EPS"}

    def request(self, symbol, fields=["DIVIDEND_YIELD", "SHARESOUT"], freq="1d"):
        req_fields = [self.fields_dic[field] for field in fields]
        req_URL = self.URL + str(symbol)
        dataset_raw = requests.get(req_URL)
        soup = BeautifulSoup(dataset_raw.text, 'html.parser')
        response = {}
        try:
            dataset_raw = soup.select('div.tab_con1')[0]

            th_data = []
            th_data_raw = [item.get_text().strip().split('\n')[0] for item in dataset_raw.select('th')]

            for th_raw in th_data_raw:
                if 'l' in th_raw:
                    splitted = th_raw.split('l')
                    th_data.append(splitted[0])
                    if '배당수익률' not in th_raw:
                        th_data.append(splitted[1])
                else:
                    th_data.append(th_raw)

            em_data = [item.get_text().strip().split('\n')[0] for item in dataset_raw.select('em')]

            for key, value in zip(th_data, em_data):
                if key in req_fields:
                    response[find_key_by_val(self.fields_dic, key)] = convert_str2num(value)
        except:
            for field in fields:
                response[field] = 999
        return response
    

class NaverStockChart():
    def __init__(self):
        self.URL = "https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count={}&requestType=0"

    def request(self, symbol, from_date='2015-01-01', to_date=datetime.now().strftime("%Y-%m-%d"), fields=["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]):
        limit = (datetime.strptime(to_date, '%Y-%m-%d') - datetime.strptime(from_date, '%Y-%m-%d')).days
        req_URL = self.URL.format(str(symbol), limit)

        res = requests.get(req_URL)
        soap = BeautifulSoup(res.text, "html.parser")
        items = soap.find_all("item")

        matrix = []

        for item in items:
            row = item['data'].split('|')
            matrix.append(row)

        df = pd.DataFrame(data=matrix, columns=['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'])
        df.set_index(keys='DATE', drop=True, inplace=True)
        df = df[fields]

        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        df = df.sort_index(ascending=True)

        cond1 = df.index >= from_date
        cond2 = df.index <= to_date

        for column in df.columns:
            df[column] = pd.to_numeric(df[column])

        return df.loc[cond1 & cond2, :]

if __name__ == '__main__':
    res = NaverStockChart().request(symbol='005380', to_date="2018-01-01")
    print(res)