# -*- coding: utf-8 -*-
import os

import numpy as np
import pandas
import yagmail

from fundquant.data_get.xq_data import XqIndexData
from fundquant.domain.index_track import IndexTrackConfig
from fundquant.service.index_value_statistic import IndexStatistic


class IndexMonitor:
    def __init__(self):
        self.sender = '洪西洋@etf.com'
        self.receivers = ['murphyxiaoxi@outlook.com', '858776278@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        self.etf_columns = ['ETF代码', 'ETF名称', '买卖建议', 'PE下概率', 'PB下概率', 'ETF数据量', '指数代码', '跟踪指数', 'IDX下概率', '指数数据量']

    def monitor(self):
        etf_stat_df = self._etf_statistic_to_df(self._index_stat_list())

        try:
            etf_stat_df.to_excel('./指数统计指标.xlsx')

            yag = yagmail.SMTP('858776278@qq.com', 'uurpxchfekfebahj', host='smtp.qq.com', port='465')
            yag.send(self.receivers, '指数跟踪', '跟踪指标和买卖建议见附件', ['./指数统计指标.xlsx'])
        except Exception as e:
            print(e)
        finally:
            os.remove('./指数统计指标.xlsx')

    @staticmethod
    def _index_stat_list():
        stat_list = []

        for config in IndexTrackConfig.get_index_config(monitor=True):
            stat = IndexStatistic(config)
            stat.compute()
            if stat.real_year is None:
                continue
            if stat.pe_less_prob_10y is None:
                stat.pe_less_prob_10y = 100
            stat_list.append(stat)

        stat_list = list(sorted(stat_list, key=lambda x: x.pe_less_prob_10y))

        return stat_list

    @staticmethod
    def pe_prob_command(less_prob, low_prob=50, high_prob=80):
        if less_prob < low_prob:
            return '分批买入'
        elif less_prob > high_prob:
            return '分批卖出'
        else:
            return '量化买入'

    @staticmethod
    def percent_command(percent, low=50, high=75):
        if percent < low:
            return '建议买入'
        elif percent > high:
            return '建议卖出'
        else:
            return '量化买入'

    @staticmethod
    def position_command(percent, low=50, high=75):
        if percent < low:
            return '0.75以下'
        elif percent > high:
            return '0.15以上'
        else:
            return '量化持仓'

    def _etf_statistic_to_df(self, statistics: list) -> pandas.DataFrame:
        index_code = []
        index_name = []
        etf_code = []
        etf_name = []
        pe_less_prob_10y = []
        pb_less_prob_10y = []
        div_mean_10y = []
        div_min = []
        div_max = []
        pe_mean_10y = []
        pe_median_10y = []
        pe_last = []
        pe_min = []
        pe_max = []
        pe_volatility_10y = []
        real_year = []
        last_dt = []

        for stat in statistics:
            index_code.append(stat.index_code)
            index_name.append(stat.index_name)
            etf_code.append(stat.etf_code)
            etf_name.append(stat.etf_name)
            div_mean_10y.append(stat.div_mean_10y)
            div_min.append(stat.div_min)
            div_max.append(stat.div_max)
            pe_less_prob_10y.append(stat.pe_less_prob_10y)
            pb_less_prob_10y.append(stat.pb_less_prob_10y)
            pe_mean_10y.append(stat.pe_mean_10y)
            pe_median_10y.append(stat.pe_median_10y)
            pe_last.append(stat.last_pe)
            pe_min.append(stat.pe_min)
            pe_max.append(stat.pe_max)
            pe_volatility_10y.append(stat.pe_volatility_10y)
            real_year.append(stat.real_year)
            last_dt.append(stat.last_dt)

        df = pandas.DataFrame(
            data=np.array(
                [index_code, index_name, etf_code, etf_name, pe_less_prob_10y, pb_less_prob_10y, div_mean_10y, div_min,
                 div_max,
                 pe_last, real_year, last_dt]).T,
            columns=['代码', '名称', 'ETF代码', 'ETF名称', 'PE分位', 'PB分位', '除均值', '除最小', '除最大',
                     'PE', '跟踪年数', '最后日期'])
        return df

    @staticmethod
    def _etf_pe_df():
        df = pandas.DataFrame()

        for config in IndexTrackConfig.get_index_config(monitor=True):
            tp_df = XqIndexData().index_data_from_db(config.index_code, config.track_days)
            tp_df = tp_df[['pe']]
            tp_df['etf_name'] = pandas.Series(np.array([config.etf_name] * len(tp_df.index)), index=tp_df.index)

            df = pandas.concat([df, tp_df])

        return df


if __name__ == '__main__':
    monitor = IndexMonitor()
    monitor.monitor()
