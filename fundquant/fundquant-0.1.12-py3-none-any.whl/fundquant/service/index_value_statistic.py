import numpy as np
import pandas

from fundquant.data_get.xq_data import XqIndexData
from fundquant.domain.index_track import IndexTrackConfig


class IndexStatistic:
    def __init__(self, index_tack: IndexTrackConfig):
        self.index_code = index_tack.index_code
        self.index_name = index_tack.index_name
        self.etf_code = index_tack.etf_code
        self.etf_name = index_tack.etf_name
        self.track_days = index_tack.track_days

        # pe统计 最近10年
        self.div_mean_10y = None  # last / mean
        self.div_min = None  # last / min
        self.div_max = None  # last / max
        self.pe_less_prob_10y = None  # pe下探概率
        self.pb_less_prob_10y = None  # pb下探概率
        self.pe_median_10y = None
        self.pe_mean_10y = None
        self.last_pe = None
        self.pe_volatility_10y = None

        # 历史
        self.pe_min = None
        self.pe_max = None

        self.real_year = None
        self.last_dt = None

    def compute(self):
        hist_k_df = XqIndexData().index_data_from_db(self.index_code, self.track_days)
        hist_k_df = hist_k_df.fillna(0)
        hist_k_df['pe'] = hist_k_df['pe'].apply(np.float)
        hist_k_df['pb'] = hist_k_df['pb'].apply(np.float)

        if hist_k_df.empty:
            return

        last_dt = hist_k_df.index[-1]
        # pe pb 统计
        pe_df = hist_k_df[['pe']].astype(np.float)
        pb_df = hist_k_df[['pb']].astype(np.float)

        pe_min = pe_df.min()['pe']
        pe_max = pe_df.max()['pe']

        pe_df = pe_df.iloc[-2520:-1]
        pb_df = pb_df.iloc[-2520:-1]

        pe_less_prob_10y = len(pe_df[pe_df['pe'] <= pe_df.iloc[-1]['pe']]) / len(pe_df)
        pb_less_prob_10y = len(pb_df[pb_df['pb'] <= pb_df.iloc[-1]['pb']]) / len(pb_df)
        pe_median_10y = pe_df.median()['pe']
        pe_mean_10y = pe_df.mean()['pe']
        last_pe = pe_df.iloc[-1]['pe']
        pe_volatility_10y = self.volatility_daily(pe_df, 'pe')

        div_mean_10y = last_pe / pe_mean_10y
        div_min = last_pe / pe_min
        div_max = last_pe / pe_max

        self.div_mean_10y = round(div_mean_10y, 2)
        self.div_min = round(div_min, 2)
        self.div_max = round(div_max, 2)
        self.pe_less_prob_10y = round(pe_less_prob_10y * 100, 1)
        self.pb_less_prob_10y = round(pb_less_prob_10y * 100, 1)
        self.pe_median_10y = round(pe_median_10y, 1)
        self.pe_mean_10y = round(pe_mean_10y, 1)
        self.last_pe = round(last_pe, 1)
        self.pe_volatility_10y = round(pe_volatility_10y * 100, 1)
        self.pe_min = round(pe_min, 1)
        self.pe_max = round(pe_max, 1)
        self.real_year = round(len(pe_df) / 252, 1)
        self.last_dt = last_dt

    @staticmethod
    def volatility_daily(df: pandas.DataFrame, col) -> float:
        ln_price = np.log2(df[col])
        log_rets = np.diff(ln_price)
        log_rets_std = np.std(log_rets)
        # 单位状态下的波动率
        volatility_per = log_rets_std / log_rets.mean() / np.sqrt(1 / 252)
        # 年波动率
        volatility = log_rets_std * np.sqrt(252)

        return volatility


if __name__ == '__main__':
    for config in IndexTrackConfig.get_index_config():
        stat = IndexStatistic(config)
        stat.compute()

        if stat.pe_less_prob_10y < 40:
            print(stat)
