import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def init():
    """
    一些初始化设置，主要是为了显示负号和中文
    :return:
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()


def line_graph(series, title="multi lines graph", legend_list="", legend_config=(20, 0), fig=None, ax=None, save=False):
    """df_list的时间轴得一样
    :param legend_config:
    :param save: 保存图片
    :param series:
    :param title:
    :param legend_list:
    :param fig: 
    :param ax:
    """
    init()
    if fig is None:
        fig = plt.figure(figsize=(16, 6))
    if ax is None:
        ax = plt.subplot(111)
    ax.set_title(title, fontsize=14)
    ax.grid(axis="both", linestyle='--')
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.tick_params(axis='both', labelsize=16)
    # ax_list = [{}] * len(series_list)
    for i in range(len(series)):
        ax.plot(series[i].index.values, series[i].values, lw=2., linestyle="-")
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
    ax.legend(legend_list, fontsize=legend_config[0], loc=legend_config[1])
    if save:
        fig.savefig(title + ".jpg")


def double_lines(series1,
                 series2,
                 lgd1="series1",
                 lgd2="series2",
                 title="double axis graph",
                 colors=("grey", "red"),
                 figname="",
                 fig=None,
                 ax=None):
    """快速画出双线对比图
    :param series1:
    :param series2:
    :param lgd1:
    :param lgd2:
    :param title:
    :param colors:
    :param figname:
    :param fig:
    :param ax:
    """
    init()
    if fig is None:
        fig = plt.figure(figsize=(16, 9))
    if ax is None:
        ax1 = plt.subplot(111)
    else:
        ax1 = ax
    ax1.set_title(title, fontsize=18)
    ax1.grid(axis="both", linestyle='--')
    ax1.spines["top"].set_visible(False)
    ax1.spines["bottom"].set_visible(True)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(True)
    ax1.tick_params(axis='both', labelsize=16)
    if type(series1) is not list:
        ax1.plot(series1.index.values, series1.values, color=colors[0])
        ax1.legend([lgd1], fontsize=16, loc=2)
    else:
        for i in range(len(series1)):
            ax1.plot(series1[i].index.values, series1[i].values, lw=2., linestyle="-")
            ax1.legend(lgd1, fontsize=16, loc=2)
    ax2 = ax1.twinx()
    if type(series2) is not list:
        ax2.plot(series2.index.values, series2.values, color=colors[1])
        ax2.legend([lgd2], fontsize=16, loc=1)
    else:
        for i in range(len(series2)):
            ax2.plot(series2[i].index.values, series2[i].values, lw=2., linestyle="-")
            ax2.legend(lgd2, fontsize=16, loc=1)
    ax2.tick_params(axis='both', labelsize=16)
    if figname is not "":
        fig.savefig(figname)
    # plt.show()


def KDEplot(data, start, end, kde_bin, hist_bin):
    from scipy import stats
    import numpy as np
    ind = np.linspace(start, end, kde_bin)
    gkde = stats.gaussian_kde(data)
    kdepdf = gkde.evaluate(ind)
    plt.style.use('seaborn')
    fig, left_axis = plt.subplots(figsize=(20, 10))
    right_axis = left_axis.twinx()
    left_axis.hist(data, bins=hist_bin, label='hist')
    left_axis.grid(False)
    left_axis.legend(loc=2, prop={'size': 20})
    left_axis.tick_params(labelsize=15)
    left_axis.set_ylabel('historical frequency', fontsize=15)
    left_axis.grid(False)
    right_axis.plot(ind, kdepdf, label='kde', color="r")
    right_axis.grid(False)
    right_axis.legend(loc=1, prop={'size': 20})
    right_axis.tick_params(labelsize=15)
    right_axis.set_ylabel('kde probability', fontsize=15)


def multi_lines(data, cols=None, spacing=.1, figname="", **kwargs):
    
    from pandas import plotting
    import matplotlib.pyplot as plt
    init()

    def get_cmap(n, name='hsv'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
        return plt.cm.get_cmap(name, n)

    fig = plt.figure(figsize=(16, 9))
    if cols is None:
        cols = data.columns
    if len(cols) == 0:
        return
    # Get default color style from pandas - can be changed to any other color list
    # 老的方案要报错
   # colors = getattr(getattr(plotting, '_style'), '_get_standard_colors')(num_colors=len(cols))
   #  colors = get_cmap(len(cols))
    colors = ["grey", "red", "blue", "purple", "green"]

    # First axis
    ax = plt.subplot(111)
    ax = data.loc[:, cols[0]].plot(label=cols[0], color=colors[0], ax=ax, **kwargs)
    ax.set_ylabel(ylabel=cols[0])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        plt.grid(False)
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new, label=cols[n],color=colors[n % len(cols)])
        ax_new.set_ylabel(ylabel=cols[n])
        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label
    ax.legend(lines, labels, loc=0)
    if figname is not "":
        fig.savefig(figname)
    # plt.show()


def goodLegend(df,legend,unit='%',loc='best',outside=False,ax=False):
    '''提供更好的图例 在图例中加入序列最后一个指标的非nan值和趋势
    
    Parameters
    ----------
    df : pd.Series or pd.DataFrame
        图表中显示的数据
        data in chart
    legend : list
        可使用df.columns或者需要显示的图例 默认为%
        df.columns or legend needed, % if default
    unit : str or list
        图例后的单位 如果有多个单位可以按顺序写在list中
        unit after every legend, for different units can be write in list in order
    outside : bool
        如果图例太大可以显示在图表外部
        display outside the chart
    ax : False, ax
        为使用了ax的图表提供 传入fig,ax=plt.subplots()中使用的ax轴即可
        for chart used ax, input ax in fig,ax=plt.subplots()'''
    if type(df)!=pd.core.frame.DataFrame:
        df=pd.DataFrame(data=df.values,index=df.index)
    if len(legend)!=np.shape(df)[1]:
        K=np.min(len(legend),np.shape(df)[1])
    else:
        K=len(legend)
    L=list()
    for i in range(K):
        I=-1
        while np.isnan(df.iloc[I,i]):
            I=I-1
        tmp=legend[i]+': '+str(round(df.iloc[I,i],1))
        if type(unit)!=list:
            unit=[unit]
        unit=unit*20
        tmp=tmp+unit[i]
        if df.iloc[I,i]>df.iloc[I-1,i]:
            tmp=tmp+' ↑'
        elif df.iloc[I,i]<df.iloc[I-1,i]:
            tmp=tmp+' ↓'
        else:
            tmp=tmp+'  ='
        L.append(tmp)
    if outside:
        if ax==False:
            plt.legend(L,bbox_to_anchor=(1.0,0.7))
        else:
            ax.legend(L,bbox_to_anchor=(1.0,0.7))
    else:
        if ax==False:
            plt.legend(L,loc=loc)
        else:
            ax.legend(L,loc=loc)