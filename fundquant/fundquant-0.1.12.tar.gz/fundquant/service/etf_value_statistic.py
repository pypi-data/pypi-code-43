import numpy as np
import pandas

from fundquant.data_get.jsl_data import JslEtf
from fundquant.domain.etf_track import EtfTrackConfig


class EtfStatistic:
    def __init__(self, etf_tack: EtfTrackConfig):
        self.etf_code = etf_tack.etf_code
        self.etf_name = etf_tack.etf_name
        self.index_code = etf_tack.index_code
        self.index_name = etf_tack.index_name
        self.track_days = etf_tack.track_days

        self.pe_median = None
        self.pe_mean = None
        self.percent = None
        self.rate_of_mean = None
        self.last_pe = None
        self.pe_less_prob = None  # 历史小于当前值的概率
        self.pb_less_prob = None
        self.real_years = None
        self.pe_volatility_1y = None

    def compute(self):
        hist_k_df = JslEtf().etf_data_from_db(self.etf_code, self.track_days)

        hist_k_df = hist_k_df.fillna(0)
        hist_k_df['pe'] = hist_k_df['pe'].apply(np.float)
        hist_k_df['pb'] = hist_k_df['pb'].apply(np.float)

        if hist_k_df.empty:
            return

        # pe pb 统计
        pe_df = hist_k_df[hist_k_df['pe'] > 0][['pe']].astype(np.float)
        pb_df = hist_k_df[hist_k_df['pb'] > 0][['pb']].astype(np.float)

        if pe_df.empty:
            return

        pe_min = pe_df.min()['pe']
        pe_max = pe_df.max()['pe']

        last_pe = pe_df.iloc[-1]['pe']
        pe_median = pe_df.median()['pe']
        pe_mean = pe_df.mean()['pe']
        rate_of_mean = last_pe / pe_mean
        percent = (last_pe - pe_min) / (pe_max - pe_min)
        real_years = len(pe_df) / 252
        pe_less_prob = len(pe_df[pe_df['pe'] <= pe_df.iloc[-1]['pe']]) / len(pe_df)
        pb_less_prob = len(pb_df[pb_df['pb'] <= pb_df.iloc[-1]['pb']]) / len(pb_df)
        pe_volatility_1y = self.volatility_daily(pe_df.iloc[-252:-1], 'pe')

        self.pe_median = round(pe_median, 2)
        self.pe_mean = round(pe_mean, 2)
        self.percent = round(percent, 2)
        self.last_pe = round(last_pe, 2)
        self.rate_of_mean = round(rate_of_mean, 2)
        self.pe_less_prob = round(pe_less_prob, 2)  # 历史小于当前值的概率
        self.pb_less_prob = round(pb_less_prob, 2)
        self.real_years = round(real_years, 2)
        self.pe_volatility_1y = round(pe_volatility_1y, 2)

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
    for config in EtfTrackConfig.get_etf_config():
        stat = EtfStatistic(config)
        stat.compute()

        if stat.pe_less_prob is not None and stat.pe_less_prob < 0.4:
            print(stat)
