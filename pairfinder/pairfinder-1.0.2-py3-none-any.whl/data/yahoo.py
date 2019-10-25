from yahoofinancials import YahooFinancials
import pandas as pd
from datetime import datetime
from utils import find_key_by_val

class YahooStockChart():
    def __init__(self):
        self.fields_dic = {"DATE": "formatted_date", "CLOSE": "adjclose", "OPEN": "open", "HIGH": "high", "LOW": "low",
                           "VOLUME": "volume"}

        self.freq_dic = {"1d": "daily", "1w": "weekly", "1m": "monethly"}

    def request(self, symbol, from_date='2015-01-01', to_date=datetime.now().strftime("%Y-%m-%d"), fields=["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"], freq="1d"):

        req_fields = ["formatted_date"] + [self.fields_dic[field] for field in fields]

        yahoo_financials = YahooFinancials([symbol])
        dataset_raw = yahoo_financials.get_historical_price_data(start_date=from_date,
                                                                 end_date=datetime.now().strftime("%Y-%m-%d"),
                                                                 time_interval='daily')
        dataset = pd.DataFrame.from_dict(dataset_raw[symbol]['prices'])
        dataset = dataset[req_fields]
        dataset.set_index('formatted_date', drop=True, inplace=True)
        dataset.index = pd.to_datetime(dataset.index)
        dataset.index.name = None
        dataset.columns = fields
        for column in dataset.columns:
            dataset[column] = pd.to_numeric(dataset[column])

        start_date = datetime.strptime(from_date, "%Y-%m-%d")
        dataset = dataset.loc[(start_date <= dataset.index) & (dataset.index <=to_date), fields]
        return dataset


class YahooEvents:
    def __init__(self):
        self.freq_dic = {
            "1d": "daily",
            "1w": "weekly",
            "1m": "monethly"
        }
        self.fields_dic = {
            'DIVIDENDS': 'dividends'
        }

    def request(self, symbol, from_date="1990-01-01", to_date=datetime.now().strftime("%Y-%m-%d"),
                field_arr=["DIVIDENDS"], freq="1d"):
        yahoo_financials = YahooFinancials([symbol])
        events_raw = \
            yahoo_financials.get_historical_price_data(start_date=from_date,
                                                       end_date=to_date,
                                                       time_interval=self.freq_dic[freq])[symbol]['eventsData']

        req_field_arr = [self.fields_dic[field] for field in field_arr]
        res = {}
        for req_field in req_field_arr:
            # res_dic = events_raw[req_field]
            # res[] = {k: v['amount'] for k, v in res_dic.items()}
            dividends = pd.DataFrame.from_dict(events_raw[req_field]).T

            dividends.set_index('formatted_date', drop=True, inplace=True)
            dividends = dividends[['amount']]

            dividends.columns = ['DIVIDENDS']
            dividends.index.name = None
            dividends.index = pd.to_datetime(dividends.index)
            dividends = dividends.sort_index()
            dividends['DIVIDENDS'] = pd.to_numeric(dividends['DIVIDENDS'])

            res[find_key_by_val(self.fields_dic, req_field)] = dividends
        return res


def main():
    yahoo = YahooStockChart()
    print(yahoo.request('CEM'))

if __name__ == '__main__':
    main()