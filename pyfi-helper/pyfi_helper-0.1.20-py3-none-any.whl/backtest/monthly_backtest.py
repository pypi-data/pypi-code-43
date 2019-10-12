from pyfi import WindHelper as w, line_graph, double_lines
from pyfi.common import Map
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

"""
performace
indicator
"""
maxdd = lambda eqd: (eqd.cumsum().expanding().max() - eqd.cumsum()).max()


def m_sharpe(eqd, bk=0.0):
    """monthly sharpe ratio"""
    try:
        if eqd.sum() == 0:
            return -100
        return ((eqd.mean() - bk / 12) / eqd.std()) * (12 ** 0.5)
    except BaseException as e:
        print(e)


def excess_msp(eqd, base_eqd, bk=0.0):
    return m_sharpe(eqd, bk) - m_sharpe(base_eqd, bk)


maxdd = lambda eqd: (eqd.cumsum().expanding().max() - eqd.cumsum()).max()


def m_sharpe(eqd, bk=0.0):
    """monthly sharpe ratio"""
    try:
        if eqd.sum() == 0:
            return -100
        return ((eqd.mean() - bk / 12) / eqd.std()) * (12 ** 0.5)
    except BaseException as e:
        print(e)


def excess_msp(eqd, base_eqd, bk=0.0):
    return m_sharpe(eqd, bk) - m_sharpe(base_eqd, bk)


EQUITY = "000300.SH"  # 沪深300
FIXEDINCOME = "CBA01552.CS"  # 净价指数


def delta_money_ind(score):
    begin_date = score.index[0]
    end_date = score.index[-1]
    r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    d_money_ind = (r007 / 100 / 12).shift(1).dropna()
    return d_money_ind


def excess_msp(eqd, base_eqd, bk=0.0):
    return m_sharpe(eqd, bk) - m_sharpe(base_eqd, bk)


def monthly_backtest(score, pattern=1, title="Monthly backtest with net value index", weight_bounds=[-1, 1],
                     bk_code=FIXEDINCOME):
    """
    分值为发布时间点,也就是建仓点,基于净价指数进行择时
    :param title: 回测模板的名称
    :param score:
    :param pattern: 1: [0,1,2]; 5: [0,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2.0]
    :return:
    """
    from pyfi.visual import init
    init()
    init_weight = (weight_bounds[0] + weight_bounds[1]) / 2.0
    low_weight = weight_bounds[0]
    up_weight = weight_bounds[1]
    begin_date = score.index[0]
    end_date = score.index[-1]
    ytm = w.edbm(codes=["gz10y"], begin_date=begin_date, end_date=end_date).iloc[:, 0]
    bond_ind = w.wsd(code=bk_code, begin_date=begin_date, end_date=end_date, paras=["close"]).iloc[:, 0].resample(
        "M").last()  # 1结尾为财富值， 2结尾为净价
    #    bond_ind = W.edb(["M0265833"], begin_date, end_date).iloc[:,0].resample("M").last()
    # 仓位设计部分开始
    if pattern > 1:
        pos = score.apply(lambda x: init_weight + (up_weight - low_weight) / 2.0 / pattern * x).shift(1)
    elif pattern == 1:
        pos = score.apply(lambda x: low_weight if x < 0 else (init_weight if x == 0 else up_weight)).shift(1)
    else:
        raise Exception("The pattern is invalid, man ~~ please reset it, OK??? Only 1 and 5 is permitted")
    # 仓位设计部分结束
    d_bond_ind = bond_ind.pct_change().dropna()
    benchmark = (1 + init_weight * d_bond_ind).cumprod()
    # pos_ = WindHelper.monthly_data_with_td(pos)
    port = (pos * d_bond_ind + 1).cumprod().dropna()
    alpha = port - benchmark
    # 看多时候的alpha & 看空时候的alpha
    d_alpha = alpha.diff()
    d_alpha[0] = alpha[0]
    alpha_long = d_alpha[pos > init_weight]  # pos不存在计算误差
    alpha_short = d_alpha[pos < init_weight]
    length_alpha_long = len(alpha_long) * 1.0  # 所有做多的时点数
    length_alpha_short = len(alpha_short) * 1.0  # 所有做空的时点数
    length_long_precise = len(alpha_long[alpha_long > 0]) * 1.0  # 持仓不同，一般不会存在误差，除非资产价格不动。
    length_short_precise = len(alpha_short[alpha_short > 0]) * 1.0
    # draw the graph
    fig = plt.figure(figsize=(10, 15))
    ax1 = plt.subplot(311)
    double_lines(series1=score, series2=ytm, title="ytm V.S. score",
                 lgd1="score", lgd2="10y ytm", ax=ax1, fig=fig)
    ax2 = plt.subplot(312)
    ax3 = ax2.twinx()
    line_graph([port, benchmark], legend_list=["port", "benchmark"],
               title="curve battle", ax=ax2, fig=fig)
    ax3.fill_between(alpha.index, 0, alpha.values, color="grey", alpha=0.3)
    ax4 = plt.subplot(313)
    line_graph([pos], legend_list=["position"],
               title="Check the position change frequencey", ax=ax4, fig=fig)
    plt.suptitle(title, fontsize=36)
    plt.show()
    d_port = port.pct_change().dropna()
    d_bench = benchmark.pct_change().dropna()
    port_yield = (port[-1] ** (1 / ((len(port)) / 12))) - 1
    benchmark_yield = (benchmark[-1] ** (1 / ((len(benchmark)) / 12))) - 1
    return Map({"score": score,
                "port": port,
                "pos": pos,
                "benchmark": benchmark,
                "alpha": alpha,
                "d_alpha": d_alpha,
                "ytm": ytm.resample("M").last(),
                "report": Map({
                    "最大回撤": maxdd(d_port),
                    "夏普比率": m_sharpe(d_port),
                    "超额夏普比率": excess_msp(d_port, d_bench),
                    "年化收益率": (port[-1] - 1) / ((len(port)) / 12),
                    "基准年化收益率": benchmark_yield,
                    "年均alpha": port_yield - benchmark_yield,
                    "alpha最大回撤": maxdd(d_alpha),
                    "信息比率": (port_yield - benchmark_yield) / (d_port.sub(d_bench).std() * np.sqrt(12)),
                    "calmar指标": (port[-1] ** (1 / (len(port) - 1) * 12) - 1) / maxdd(d_port),
                    "看多次数": length_alpha_long,
                    "看多准确率": np.nan if length_alpha_long == 0 else length_long_precise / length_alpha_long,
                    "看空次数": length_alpha_short,
                    "看空准确率": np.nan if length_alpha_short == 0 else length_short_precise / length_alpha_short,
                    "综合准确率": np.nan if (length_alpha_long + length_alpha_short) == 0 else (
                                                                                                  length_long_precise + length_short_precise) / (
                                                                                                  length_alpha_long + length_alpha_short),
                })
                })


def monthly_backtest_with_repo(score, pattern=1, init_weight=1, bk_code=FIXEDINCOME):
    """
    分值为发布时间点,也就是建仓点
    """
    import matplotlib.pyplot as plt
    from pyfi.visual import init
    init()
    b_weight = init_weight
    begin_date = score.index[0]
    end_date = score.index[-1]
    if pattern > 1:
        pos = score.apply(lambda x: b_weight + (b_weight / pattern) * x).shift(1)
    elif pattern == 1:
        pos = score.apply(lambda x: 0 if x < 0 else (b_weight if x == 0 else 2 * b_weight)).shift(1)
    else:
        raise Exception("The pattern is invalid, man ~~ please reset it, OK??? Only 1 and 5 is permitted")
    ytm = w.edbm(codes=["gz10y"], begin_date=begin_date, end_date=end_date).iloc[:, 0]
    # r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    bond_ind = w.wsd(bk_code, ["close"], begin_date, end_date).iloc[:, 0] \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    d_bond_ind = bond_ind.pct_change().dropna()
    r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    # money_ind = (r007 / 100 / 12 + 1).cumprod().shift(1).dropna()
    d_money_ind = (r007 / 100 / 12).shift(1).dropna()
    # establish the benchmark
    benchmark = (d_bond_ind * b_weight + (d_money_ind * (1 - b_weight)) + 1).cumprod()
    # pos_ = WindHelper.monthly_data_with_td(pos)
    port = (pos * d_bond_ind + (1 - pos) * d_money_ind + 1).cumprod().dropna()
    alpha = port - benchmark
    # 看多时候的alpha & 看空时候的alpha
    d_alpha = alpha.diff()
    d_alpha[0] = alpha[0]
    alpha_long = d_alpha[pos > init_weight]  # pos不存在计算误差
    alpha_short = d_alpha[pos < init_weight]
    length_alpha_long = len(alpha_long) * 1.0  # 所有做多的时点数
    length_alpha_short = len(alpha_short) * 1.0  # 所有做空的时点数
    length_long_precise = len(alpha_long[alpha_long > 0]) * 1.0  # 持仓不同，一般不会存在误差，除非资产价格不动。
    length_short_precise = len(alpha_short[alpha_short > 0]) * 1.0
    # draw the picture
    fig = plt.figure(figsize=(10, 15))
    ax1 = plt.subplot(311)
    double_lines(series1=score, series2=ytm, title="ytm V.S. score",
                 lgd1="score", lgd2="10y ytm", ax=ax1, fig=fig)
    ax2 = plt.subplot(312)
    ax3 = ax2.twinx()
    line_graph([port, benchmark], legend_list=["port", "benchmark"],
               title="curve battle", ax=ax2, fig=fig)
    ax3.fill_between(alpha.index, 0, alpha.values, color="grey", alpha=0.3)
    ax4 = plt.subplot(313)
    line_graph([pos], legend_list=["position"],
               title="Check the position change frequencey", ax=ax4, fig=fig)
    plt.suptitle("Monthly Backtest with wealth index", fontsize=36)
    plt.show()
    d_port = port.pct_change().dropna()
    d_bench = benchmark.pct_change().dropna()
    port_yield = (port[-1] ** (1 / ((len(port)) / 12))) - 1
    benchmark_yield = (benchmark[-1] ** (1 / ((len(benchmark)) / 12))) - 1
    return Map({"score": score,
                "port": port,
                "pos": pos,
                "benchmark": benchmark,
                "alpha": alpha,
                "ytm": ytm.resample("M").last(),
                "report": Map({
                    "最大回撤": maxdd(d_port),
                    "夏普比率": m_sharpe(d_port),
                    "超额夏普比率": excess_msp(d_port, d_bench),
                    "年化收益率": port_yield,
                    "基准年化收益率": benchmark_yield,
                    "年均alpha": port_yield - benchmark_yield,
                    "alpha最大回撤": maxdd(d_alpha),
                    "信息比率": (d_port.sub(d_bench)).mean() / (d_port.sub(d_bench).std()),
                    "calmar指标": (port[-1] ** (1 / (len(port) - 1) * 12) - 1) / maxdd(d_port),
                    "看多次数": length_alpha_long,
                    "看多准确率": np.nan if length_alpha_long == 0 else length_long_precise / length_alpha_long,
                    "看空次数": length_alpha_short,
                    "看空准确率": np.nan if length_alpha_short == 0 else length_short_precise / length_alpha_short,
                    "综合准确率": np.nan if (length_alpha_long + length_alpha_short) == 0 else (
                                                                                                  length_long_precise + length_short_precise) / (
                                                                                                  length_alpha_long + length_alpha_short),

                })
                })


def monthly_backtest_with_repo2(score, pattern=1):
    """
    保持仓位始终不变，防止前期的alpha对后期的alpha带来增益的影响
    分值为发布时间点,也就是建仓点

    """
    b_weight = 1
    import matplotlib.pyplot as plt
    begin_date = score.index[0]
    end_date = score.index[-1]
    if pattern == 5:
        pos = score.apply(lambda x: b_weight + (b_weight / pattern) * x).shift(1)
    elif pattern == 1:
        pos = score.apply(lambda x: 0 if x < 0 else (1 if x == 0 else 2)).shift(1)
    else:
        raise Exception("The pattern is invalid, man ~~ please reset it, OK??? Only 1 and 5 is permitted")
    ytm = w.edbm(codes=["gz10y"], begin_date=begin_date, end_date=end_date).iloc[:, 0]
    r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    bond_ind = w.wsd("CBA01551.CS", ["close"], begin_date, end_date).iloc[:, 0] \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    d_bond_ind = bond_ind.pct_change().dropna()
    r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    # money_ind = (r007 / 100 / 12 + 1).cumprod().shift(1).dropna()
    d_money_ind = (r007 / 100 / 12).shift(1).dropna()
    # establish the benchmark
    benchmark = 1 + (d_bond_ind * b_weight + (d_money_ind * (1 - b_weight))).cumsum()
    # pos_ = WindHelper.monthly_data_with_td(pos)
    port = 1 + (pos * d_bond_ind + (1 - pos) * d_money_ind).cumsum().dropna()
    alpha = port - benchmark
    # draw the picture
    fig = plt.figure(figsize=(10, 15))
    ax1 = plt.subplot(311)
    double_lines(series1=score, series2=ytm, title="ytm V.S. score",
                 lgd1="score", lgd2="10y ytm", ax=ax1, fig=fig)
    ax2 = plt.subplot(312)
    ax3 = ax2.twinx()
    line_graph([port, benchmark], legend_list=["port", "benchmark"],
               title="curve battle", ax=ax2, fig=fig)
    ax3.fill_between(alpha.index, 0, alpha.values, color="grey", alpha=0.3)
    ax4 = plt.subplot(313)
    line_graph([pos], legend_list=["position"],
               title="Check the position change frequencey", ax=ax4, fig=fig)
    plt.suptitle("Monthly Backtest with wealth index(No cum)", fontsize=36)
    plt.show()
    return {"score": score,
            "port": port,
            "pos": pos,
            "benchmark": benchmark,
            "alpha": alpha,
            "ytm": ytm.resample("M").last()
            }


def monthly_backtest_with_structure(score,
                                    struct_scores=None,
                                    pattern=1, init_weight=0.5,
                                    init_duration_allocation=[0.25, 0.25, 0.25, 0.25]):
    """
    输入久期打分，输入品种打分，输入模式，输入初始权重,基准权重
    注意：score的最后一个分值，是不会考虑到回测中的
    分值越高，权重越大
    :param score: 久期择时打分
    :param struct_scores: 期限结构打分，DataFrame 格式, 0-5分
    :param pattern: 调仓模式
    :param init_weight: 中性仓位
    :param init_duration_allocation：基准的久期的权重分配
    :return:
    """
    # 输入参数校验
    # 确定基准久期结构
    benchmark_struct = pd.DataFrame([init_duration_allocation] * len(score), index=score.index,
                                    columns=["3y", "5y", "7y", "10y"])
    if struct_scores is not None:
        if len(score) > len(struct_scores):
            struct_scores = pd.DataFrame(struct_scores, index=score.index)
            for i in range(len(score)):
                if struct_scores.iloc[i, :].isnull().any():
                    struct_scores.iloc[i, :] = np.array(init_duration_allocation)

    else:
        struct_scores = benchmark_struct
    # 确定久期
    begin_date = score.index[0]
    end_date = score.index[-1]

    one_to_three = w.wsd("CBA01521.CS", ["close", "duration"], begin_date=begin_date, end_date=end_date) \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    three_to_five = w.wsd("CBA01531.CS", ["close", "duration"], begin_date=begin_date, end_date=end_date) \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    five_to_seven = w.wsd("CBA01541.CS", ["close", "duration"], begin_date=begin_date, end_date=end_date) \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    seven_to_ten = w.wsd("CBA01551.CS", ["close", "duration"], begin_date=begin_date, end_date=end_date) \
        .resample("M").last()  # 1结尾为财富值， 2结尾为净价
    # 资金净值曲线
    r007 = w.edb(codes=["M0041653"], begin_date=begin_date, end_date=end_date).iloc[:, 0].resample("M").last()
    # money_ind = (r007 / 100 / 12 + 1).cumprod().shift(1).dropna()
    d_money_ind = (r007 / 100 / 12).shift(1).dropna()
    # 十年国债收益率
    ytm = w.edbm(codes=["gz10y"], begin_date=begin_date, end_date=end_date).iloc[:, 0]
    # 子指数的每个月的收益率
    d_one_to_three = one_to_three.close.pct_change().dropna()  # shift1
    d_three_to_five = three_to_five.close.pct_change().dropna()  # shift1
    d_five_to_seven = five_to_seven.close.pct_change().dropna()  # shift1
    d_seven_to_ten = seven_to_ten.close.pct_change().dropna()  # shift1
    # 生成基准中的债券组合部分
    bond_ind = pd.Series(index=score.index)  # shift0
    bond_duration = pd.Series(index=score.index)  # shift0
    for i in range(len(bond_ind)):
        if i == 0:
            bond_ind[0] = 1.0
            continue
        tmp_struct_durations = np.array([one_to_three.duration[i - 1],  # 最后一个久期数据无效
                                         three_to_five.duration[i - 1],
                                         five_to_seven.duration[i - 1],
                                         seven_to_ten.duration[i - 1]])
        d_tmp_struct = np.array([d_one_to_three[i - 1],
                                 d_three_to_five[i - 1],
                                 d_five_to_seven[i - 1],
                                 d_seven_to_ten[i - 1]])
        lmda = 1.0 / ((np.array(init_duration_allocation) / tmp_struct_durations).sum())
        tmp_struct_weights = np.array(init_duration_allocation) / tmp_struct_durations * lmda
        bond_ind[i] = (1 + (tmp_struct_weights * d_tmp_struct).sum()) * bond_ind[i - 1]
        bond_duration[i - 1] = (tmp_struct_weights * tmp_struct_durations).sum()  # shfit0
    d_bond_ind = bond_ind.pct_change().dropna()  # shift1
    # 构建加入资金权重的基准
    benchmark = (d_bond_ind * init_weight + (d_money_ind * (1 - init_weight)) + 1).cumprod()
    if pattern == 5:
        pos = score.apply(lambda x: init_weight + (init_weight / pattern) * x).shift(0)  # shift0坐标
    elif pattern == 1:
        pos = (score.apply(lambda x: 0 if x < 0 else (1 if x == 0 else 2)) * init_weight).shift(0)  # shift0坐标
    else:
        raise Exception("The pattern is invalid, man ~~ please reset it, OK??? Only 1 and 5 is permitted")
    port_duration = bond_duration * pos  # shift0
    pos = pos.shift(1).dropna()
    # port1 无结构优化
    port1 = (pos * d_bond_ind + (1 - pos) * d_money_ind + 1).cumprod().dropna()  # 都会shift1
    alpha1 = port1 - benchmark

    if struct_scores is not None:
        struct_scores = struct_scores.loc[(struct_scores.index >= begin_date) & (struct_scores.index <= end_date),
                        :].shift(1).dropna()
        struct_pos = pd.DataFrame(columns=struct_scores.columns, index=pos.index)
        struct_durations = pd.DataFrame(columns=struct_scores.columns, index=port_duration.index)  # shift0
        # port2 结构优化
        port2 = pd.Series(index=port1.index)  # shift1
        d_port2 = pd.Series(index=port1.index)  # shift1
        try:
            for i in range(len(port2)):
                # 确定当天的无结构优化组合的久期
                tmp_duration = port_duration[i]  # 标量, shift0
                # 确定给整体比率
                lmda = tmp_duration / (struct_scores.iloc[i, :].sum())  # 标量， struct_scores已经shift, 注意这里是shift1
                tmp_struct_durations = np.array([one_to_three.duration[i],
                                                 three_to_five.duration[i],
                                                 five_to_seven.duration[i],
                                                 seven_to_ten.duration[i]])  # shift0
                struct_durations.iloc[i, :] = tmp_struct_durations  # N*4 shift0
                tmp_struct_weights = (struct_scores.iloc[i, :] * lmda) / tmp_struct_durations
                tmp_pos = tmp_struct_weights.sum()  # 标量
                # print(tmp_pos)
                struct_pos.iloc[i, :] = tmp_struct_weights  # shift1
                bond_return = (tmp_struct_weights * np.array([d_one_to_three[i],
                                                              d_three_to_five[i],
                                                              d_five_to_seven[i],
                                                              d_seven_to_ten[i]])).sum()  # 实际计算的是shift1的第一个时点
                port_return = bond_return + (1 - tmp_pos) * d_money_ind[i]
                d_port2[i] = port_return
                if i == 0:
                    port2[i] = 1 * (port_return + 1)
                else:
                    port2[i] = port2[i - 1] * (port_return + 1)
        except IndexError as e:
            print(pos.index[i])
            raise e
        alpha2 = port2 - benchmark
        port = port2
    else:
        alpha2 = alpha1
        port = port1
        port2 = port1
    alpha = port - benchmark
    # 开始画图
    fig = plt.figure(figsize=(10, 15))
    ax1 = plt.subplot(311)
    double_lines(series1=score, series2=ytm, title="ytm V.S. score",
                 lgd1="score", lgd2="10y ytm", ax=ax1, fig=fig)
    ax2 = plt.subplot(312)
    ax3 = ax2.twinx()
    line_graph([port1, port2, benchmark], legend_list=["duration", "structural duration", "benchmark"],
               title="curve battle", ax=ax2, fig=fig)
    ax3.fill_between(alpha.index, 0, alpha.values, color="grey", alpha=0.3)
    ax4 = plt.subplot(313)
    line_graph([pos], legend_list=["position"],
               title="Check the position change frequencey", ax=ax4, fig=fig)
    plt.suptitle("Monthly Backtest with wealth index", fontsize=36)
    plt.show()
    d_port = port.pct_change().dropna()
    d_bench = benchmark.pct_change().dropna()
    return Map({"score": score,
                "port1": port1,
                "port2": port2,
                "pos": pos,
                "struct_pos": struct_pos,
                "struct_durations": struct_durations,
                "port_duration": port_duration,
                "benchmark": benchmark,
                "alpha": alpha,
                "ytm": ytm.resample("M").last(),
                "report": Map({
                    "最大回撤": maxdd(d_port),
                    "夏普比率": m_sharpe(d_port),
                    "最终alpha1": alpha1[-1],
                    "最终alpha2": alpha2[-1],
                    "久期结构alpha": alpha2[-1] - alpha1[-1],
                    "超额夏普比率": excess_msp(d_port, d_bench),
                    "年均alpha": alpha[-1] / ((len(port) - 1) / 12),
                    "calmar指标": (port[-1] ** (1 / (len(port) - 1) * 12) - 1) / maxdd(d_port),
                })
                })
