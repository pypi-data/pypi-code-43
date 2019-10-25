# import os, sys
#
# import sqlite3
# import pandas as pd
# from tqdm import tqdm
# from datetime import datetime
# from more_itertools import unique_everseen
# from calendar import monthrange
# import re
# from utils import get_project_dir, ks_stock_symbols
#
# IN_DIR = os.path.join(get_project_dir(), 'data', 'raw')
# OUT_DIR = os.path.join(get_project_dir(), 'data', 'processed')
#
# class DB:
#     def __init__(self, db_fname):
#         """
#         :param fname: ex) 'ohlcv.db'
#         """
#         self.db_path = os.path.join(OUT_DIR, db_fname)
#
#         if not os.path.isfile(self.db_path):
#             print(" [*] Creating {} ...".format(db_fname))
#
#         self.con = sqlite3.connect(self.db_path)
#         self.cursor = self.con.cursor()
#
#     def request(self, symbol, from_date, fields=["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]):
#         req_fields = ["DATES"] + fields
#
#         query = "SELECT {} FROM '{}' WHERE Dates >= '{}'" \
#                 "AND Dates  <= '{}'".format(', '.join(req_fields), symbol, from_date, datetime.now().date())
#
#         self.cursor.execute(query)
#
#         df = pd.DataFrame.from_records(data=self.cursor.fetchall(), columns=req_fields)
#         df = df.set_index('DATES')
#         df = df.apply(pd.to_numeric)
#         df.index = pd.to_datetime(df.index)
#         return df
#
#     def get_table_names(self):
#         query = "SELECT name FROM sqlite_master WHERE type='table';"
#         return [i[0] for i in self._fetch_data(query, fetch_type='all')]
#
#     def get_latest_date(self, symbol):
#         query = "SELECT max(Date) FROM '{}'".format(symbol)
#         return self._fetch_data(query, fetch_type='one')
#
#     def get_oldest_date(self, symbol):
#         query = "SELECT min(Date) FROM '{}'".format(symbol)
#         return self._fetch_data(query, fetch_type='one')
#
#     def _fetch_data(self, query, fetch_type='all'):
#         try:
#             self.cursor.execute(query)
#             if fetch_type == 'all':
#                 return self.cursor.fetchall()
#             elif fetch_type == 'one':
#                 return self.cursor.fetchone()[0]
#         except:
#             return False
#
#     def convert_to_db(self, raw_fname, out_columns=["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"],
#                       sheet_name='Sheet1', in_type='bloomberg', out_type='default'):
#         """
#         :param raw_fname: 변환할 파일이름
#         :param out_columns: 저장할 컬럼
#         :param sheet_name: 변환할 파일 시트
#         :param in_type: 변환할 파일 타입
#         :param out_type: 출력할 타입
#         """
#         self.in_type = in_type
#         self.out_type = out_type
#
#         raw_path = os.path.join(IN_DIR, raw_fname)
#
#         if self.in_type == 'bloomberg':
#             print(" [*] Converting Bloomberg File to DB File...")
#             self._convert_bloomberg(path=raw_path, sheet_name=sheet_name, out_columns=out_columns)
#
#         elif self.in_type == 'quantiwise':
#             print(" [*] Converting Quantiwise File to DB File...")
#             self._convert_quantiwise(path=raw_path, sheet_name=sheet_name, out_columns=out_columns)
#
#         elif self.in_type == 'non_time_series':
#             print(" [*] Converting Non-Time Series Xlsx File to DB File...")
#             self._convert_non_time_series(path=raw_path, sheet_name=sheet_name, out_columns=out_columns)
#
#         else:
#             raise Exception
#
#     def request_non_time_series(self, symbol, fields=["DIVIDEND_YIELD"]):
#         query = "SELECT {} FROM '{}'".format(', '.join(fields), symbol)
#         self.cursor.execute(query)
#         df = pd.DataFrame.from_records(data=self.cursor.fetchall(), columns=fields).iloc[0, :].to_dict()
#         return df
#
#     def _convert_non_time_series(self, path, sheet_name, out_columns):
#         # settings
#         data = pd.read_excel(path, sheet_name=sheet_name)
#         symbols = data.columns
#
#         with tqdm(total=len(symbols), file=sys.stdout) as pbar:
#             for i, symbol in enumerate(symbols):
#                 df = data[symbol]
#
#                 df = df.to_frame().T
#                 df.columns = out_columns
#
#                 if len(df) == 0:
#                     print(df)
#                     pass
#                 df.to_sql(symbol, con=self.con, if_exists='replace', index=False)
#                 pbar.update(1)
#
#     def _convert_bloomberg(self, path, sheet_name, out_columns):
#         # settings
#         n_features = len(out_columns)
#         symbols_idx = 0
#         features_idx = 1
#         data = pd.read_excel(path, sheet_name=sheet_name, header=None)
#
#         # get symbol lists
#         symbols = [data.ix[symbols_idx][i] for i in range(1, len(data.ix[symbols_idx]), n_features)]
#         data = pd.DataFrame(data.ix[features_idx + 1:, ])
#         data = data.set_index(0)
#         data.index.name = 'DATES'
#
#         k = 0
#         with tqdm(total=len(symbols), file=sys.stdout) as pbar:
#             for i in range(len(symbols)):
#                 symbol = symbols[i]
#                 df = pd.DataFrame(data.ix[:, i * n_features + k:i * n_features + n_features].values, index=data.index,
#                                   columns=out_columns)
#                 k = 1
#                 df.index = pd.to_datetime(df.index)
#                 df = df.dropna(how='all')
#                 if len(df) == 0:
#                     print(df)
#                     pass
#                 df.to_sql(symbol, con=self.con, if_exists='replace')
#                 pbar.update(1)
#
#     def _convert_quantiwise(self, path, sheet_name, out_columns):
#         """
#         :param data_path: raw data path
#         :param sheet_type: single, multiple
#         :return:
#         """
#         with pd.ExcelFile(path) as reader:
#             sheet = pd.read_excel(reader, sheet_name=sheet_name)
#             total_df, symbols = self._quantisheet_to_df(sheet, out_columns)
#
#             with tqdm(total=len(symbols), file=sys.stdout) as pbar:
#                 for symbol in symbols:
#                     df = total_df[symbol].dropna(how='all')
#                     df.to_sql(symbol, con=self.con, if_exists='replace')
#                     pbar.update(1)
#
#     def _quantisheet_to_df(self, sheet, out_columns):
#         symbols = list(unique_everseen(sheet.iloc[6, :]))
#         symbols.remove('Code')
#
#         converted_symbols = ks_stock_symbols(symbols, in_type=self.in_type, out_type=self.out_type)
#
#         sheet.columns = sheet.iloc[12, :]
#         sheet = sheet.iloc[13:, ]
#         sheet = sheet.set_index('D A T E')
#         sheet.index.name = 'DATES'
#
#         df = sheet.iloc[:-1, :]
#         df.columns = pd.MultiIndex.from_product([converted_symbols, out_columns])
#
#         return df, converted_symbols
#
#     def close(self):
#         self.con.close()
#
# def main():
#
#     DB(db_fname='ohlcvd.db').convert_to_db(raw_fname='CEF_ETF_ohlcvd.xlsx',
#                                                        out_columns=["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "DIVIDEND_YIELD"],
#                                                        sheet_name='Sheet1',
#                                                        in_type='bloomberg',
#                                                        out_type='default')
#
#     """
#     print(DB(db_fname='cp_ohlcv.db').convert_to_db(raw_fname='bloom_cp_dy.xlsx', out_columns=["DIVIDEND_YIELD"],
#                       sheet_name='Sheet1', in_type='non_time_series', out_type='default'))
#     """
#     #print(DB(db_fname='cp_dy.db').request_non_time_series("VLA FP Equity", fields=["DIVIDEND_YIELD", "TEST"]))
#
# if __name__ == '__main__':
#     main()