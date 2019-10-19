import datetime
import time

import pandas
import pandas as pd
import numpy as np
import pymysql

from fundquant.data_get.xq_data import XqApi
from fundquant.util import dateutil
from sqlalchemy import create_engine


class IndexBufDump:
    def __init__(self):
        # 初始化数据库连接，使用pymysql模块
        self.engine = create_engine('mysql+pymysql://root:@localhost:3306/quant')

    def monitor_etf(self) -> pandas.DataFrame:
        etf_list_df = pd.read_sql_query(
            'select index_code, index_name from index_track_list where monitor = 1 order by index_code',
            self.engine)

        index_df = pd.read_sql_query('select index_code, dt, pe from index_data where pe > 0 order by index_code, dt',
                                     self.engine)

        df = etf_list_df.merge(index_df, on='index_code', how='inner')

        return df


f = IndexBufDump()
df = f.monitor_etf()
df.to_csv('./tmp.csv', index=False)
