from fundquant.service.index_value_statistic import IndexStatistic

from fundquant.domain.index_track import IndexTrackConfig


def signal(index_conf: IndexTrackConfig) -> int:
    """

    :param index_conf:
    :return: 1买 -1卖 0持仓
    """
    stat = IndexStatistic(index_conf)
    hist_k = stat.compute()

    today_value = hist_k.iloc[-1]['close_value']

    if today_value < stat.std_low_value:
        return 1

    elif today_value > stat.std_high_value:
        return -1

    else:
        return 0
