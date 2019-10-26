import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import os
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import numpy as np
from SETTINGS import K_ARR, PLOT_XAXIS_N_LOCATOR
import matplotlib.dates as mdates
from utils import split_yearly

# Constants
FONT_SIZE = 8
LINE_WIDTH = 0.6
GRID_ALPHA = 0.3
DPI = 300
FIG_HEIGHT = 2.5

# Static Fonts 추가
font_dirs = [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts'), ]
font_files = fm.findSystemFonts(fontpaths=font_dirs, fontext='ttf')
font_list = fm.createFontList(font_files)
fm.fontManager.ttflist.extend(font_list)

# Default Settings
mpl.rcParams['figure.dpi'] = mpl.rcParams['savefig.dpi'] = DPI
mpl.rcParams['font.size'] = mpl.rcParams['legend.fontsize'] = mpl.rcParams['figure.titlesize'] = FONT_SIZE
mpl.rcParams['lines.linewidth'] = LINE_WIDTH
mpl.rcParams['axes.unicode_minus'] = False

mpl.rcParams['grid.alpha'] = GRID_ALPHA
mpl.rcParams['axes.grid'] = True

mpl.rcParams['xtick.labelsize'] = FONT_SIZE
mpl.rcParams['ytick.labelsize'] = FONT_SIZE
# Font
font_name = [(f.name, f.fname) for f in fm.fontManager.ttflist if 'Nanum' in f.name][0]
mpl.rc('font', family=font_name)
font = fm.FontProperties(family=font_name, size=FONT_SIZE)

method_category = {'diff': 'index',
                   'Ratio': 'index',
                   'ROsMA': 'spread',
                   'DROsMA': 'spread',
                   'OLS': 'spread',
                   'TLS': 'spread',
                   'KF': 'spread',
                   'NPI': 'spread',
                   'zscore': 'spread'}

class PairPlotLib():
    def __init__(self, pair, from_='2015-01-01', to_='2020-12-31'):
        self.pair = pair
        self.x_name = pair.x_asset.name
        self.y_name = pair.y_asset.name
        self.from_, self.to_ = from_, to_

    @staticmethod
    def plot_yearly(df, normalize=False, scale=False):
        yearly_df = split_yearly(df)
        fig = plt.figure(figsize=(7, FIG_HEIGHT), dpi=DPI)
        ax = fig.add_subplot(111)

        color_pallette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                          '#bcbd22', '#17becf']
        years = yearly_df.columns

        for year, color in zip(years, color_pallette):
            if year == years[0]:  # 첫 해 제거
                continue
            data = yearly_df[year]

            if normalize:
                std = np.std(data)
                mean = np.mean(data)
                data = (data - mean) / std

            if scale:  # 스케일링이 안 됨
                data = data / data[data.first_valid_index()]

            ax.plot(data, label=year, color=color)

            bbox_props = dict(boxstyle="larrow", pad=0.01, fc=color, ec="b", lw=0)
            plt.annotate(year + ': %.3f   ' % data[-1], xy=(1, data[-1]), xytext=(0, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                         bbox=bbox_props, color='white')

        ax.set_ylabel('Yearly Seasonality')
        ax.tick_params(bottom=False, labelbottom=True)
        #ax.tick_params(labelleft=False, labelright=True, left=False, right=True)

        fig.tight_layout()

        every_nth = 30
        for n, label in enumerate(ax.xaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)

        ax.xaxis.grid(False, which='both')
        plt.close(fig='all')
        return fig, ax, yearly_df


    @staticmethod
    def plot(x, title, label, from_='2015-01-01', to_='2020-12-31'):
        fig = plt.figure(figsize=(7, FIG_HEIGHT), dpi=DPI)
        ax = fig.add_subplot(111)
        x = x.loc[from_:to_]

        ax.plot(x, label=label, color='blue')

        ax.legend(loc='upper left')

        ax.set_ylabel(title)
        ax.tick_params(labelleft=False, labelright=True, left=False, right=True)

        fig.tight_layout()
        annotations = [[x, "C:", "blue"]]
        for annotation in annotations:
            data, prefix, box_color = annotation[0], annotation[1], annotation[2]
            if len(data) == 0:
                break
            bbox_props = dict(boxstyle="larrow", pad=0.01, fc=box_color, ec="b", lw=0)
            plt.annotate(prefix + '%.3f   ' % data[-1], xy=(1, data[-1]), xytext=(0, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                         bbox=bbox_props, color='white')

        plt.close(fig='all')
        return fig, ax

    def price(self, x, y, title='Price'):
        fig = plt.figure(figsize=(7, FIG_HEIGHT), dpi=DPI)
        ax = fig.add_subplot(111)
        x = x.loc[self.from_:self.to_]
        y = y.loc[self.from_:self.to_]

        ax.plot(x, label=self.x_name, color='red')
        ax.plot(y, label=self.y_name, color='blue')
        ax.legend(loc='upper left')

        ax.set_ylabel(title)
        ax.tick_params(labelleft=False, labelright=True, left=False, right=True)

        fig.tight_layout()
        annotations = [[x, "C:", "red"], [y, "C:", "blue"]]
        for annotation in annotations:
            data, prefix, box_color = annotation[0], annotation[1], annotation[2]
            if len(data) == 0:
                break
            bbox_props = dict(boxstyle="larrow", pad=0.01, fc=box_color, ec="b", lw=0)
            plt.annotate(prefix + '%.3f   '% data[-1], xy=(1, data[-1]), xytext=(0, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                         bbox=bbox_props, color='white')

        plt.close(fig='all')
        return fig, ax

    def spread_dist(self, method='ROsMA', ylabel='Spread'):
        figsize_x = 2.7
        figsize_y = FIG_HEIGHT

        fig = plt.figure(figsize=(figsize_x, figsize_y), dpi=DPI)
        ax = fig.add_subplot(111)

        spread = self.pair.spread[method]
        if len(spread) > 0:
            sns.distplot(np.array(spread), color='#539caf', label='{} Distribution'.format(method), ax=ax)
            # sns.kdeplot(tuple(np.array(spread)), shade=True, cut=0, color='#539caf', label='{} Spread Density'.format(method), ax=ax)
            sns.rugplot(np.array(spread), color='#539caf', ax=ax)

            ax.legend(loc='upper left')
            ax.axvline(x=spread[-1], color='red', linestyle='--')
            ax.set_ylabel(ylabel)

        plt.tight_layout()
        plt.close(fig='all')
        return fig, ax

    @staticmethod
    def annotate_divs(ax, dvd_dic, method, color='green', fontsize=6, div_yield=False, xytext=(0,10)):

        for x, value in dvd_dic.items():
            nearest = value['nearest']
            if div_yield == True:
                annotation = '{0:.2%}'.format(value['dividend_yield'])
            else:
                annotation = '{0:.2f}'.format(value['dividend_yield'])

            if method == 'Price':
                y = value['price']
            else:
                y = value[method]

            ax.annotate(annotation,
                        (mdates.date2num(nearest), y),
                        xytext=xytext,
                        textcoords='offset points',
                        arrowprops=dict(arrowstyle='-|>'),
                        ha='center',
                        fontsize=fontsize,
                        color=color)


        return ax

    def spread_box(self, method='ROsMA', y_label='Spread'):
        figsize_x = 2.7
        figsize_y = FIG_HEIGHT

        fig = plt.figure(figsize=(figsize_x, figsize_y), dpi=DPI)
        ax = fig.add_subplot(111)

        spread = self.pair.spread[method]

        if len(spread) > 0:
            ax.boxplot(spread)

            if len(self.pair.data[method + '_mean']) > 0:

                for i, k in enumerate(K_ARR):
                    ub_suffix = '_ub_' + str(k)
                    lb_suffix = '_lb_' + str(k)

                    ub_y = self.pair.data[method + ub_suffix][-1]
                    lb_y = self.pair.data[method + lb_suffix][-1]

                    ub_prefix = str(k).rjust(5) + 'σ :'
                    lb_prefix = str(-k).rjust(5) + 'σ :'

                    ub_bbox_props = dict(boxstyle='larrow', pad=0.01, fc='gray', ec="b", lw=0,
                                         alpha=1 / (len(K_ARR) + 1) * (i + 2))
                    lb_bbox_props = dict(boxstyle='larrow', pad=0.01, fc='#539caf', ec="b", lw=0,
                                         alpha=1 / (len(K_ARR) + 1) * (i + 2))

                    ub_text = ub_prefix + '%.3f' % ub_y
                    ax.annotate(ub_text.rjust(15), xy=(1, ub_y), xytext=(0, 0),
                                xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                                bbox=ub_bbox_props, color='white')

                    lb_text = lb_prefix + '%.3f' % lb_y
                    ax.annotate(lb_text.rjust(15), xy=(1, lb_y), xytext=(0, 0),
                                xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                                bbox=lb_bbox_props, color='white')

            ax.axhline(y=spread[-1], color='blue', linestyle='--')

        ax.set_ylabel(y_label)
        ax.set_xlabel(method)

        ax.tick_params(labelbottom=False)



        plt.tight_layout()
        plt.close(fig='all')
        return fig, ax

    def linear_regression(self, method='TLS'):
        log_x = self.pair.data['log_x']
        log_y = self.pair.data['log_y']
        rand_x = np.linspace(log_x.min(), log_x.max(), 100)

        figsize_x = 2.7
        figsize_y = FIG_HEIGHT

        fig = plt.figure(figsize=(figsize_x, figsize_y), dpi=DPI)
        ax = fig.add_subplot(111)

        slope = self.pair.hedge_ratio[method]
        intercept = self.pair.intercept[method]

        ax.scatter(x=log_x, y=log_y, c='black', alpha=0.5, linewidth=1, linestyle='-.', s=5, label='Observed')
        ax.plot(rand_x, rand_x * slope + intercept, color='red', label='y=%.3fx%+.3f' % (slope, intercept))

        ax.legend(loc='upper left')
        ax.set_ylabel(self.y_name)
        ax.set_xlabel(self.x_name)

        plt.tight_layout()
        plt.close(fig='all')
        return fig, ax

    @staticmethod
    def spread_staticmethod(spread_arr, methods, window=365, method_category='index', y_label='Spread', bollinger=True):
        n_fig = len(methods)
        figsize_x = 7
        figsize_y = n_fig * FIG_HEIGHT

        fig, axes = plt.subplots(nrows=n_fig, ncols=1, figsize=(figsize_x, figsize_y), dpi=DPI)

        axes = [axes, None] if len(methods) == 1 else axes  # padding for zip function

        for spread, method, ax in zip(spread_arr, methods, axes):
            if len(spread) > 0:
                ax.plot(spread, label=method, color='blue')

                if method_category == 'total_mean':
                    mean = spread.mean()
                    ax.axhline(mean, linestyle='--', color='red')
                elif method_category == 'spread':
                    ax.axhline(0, linestyle='--', color='red')
                else:
                    pass

                if bollinger is True:
                    rolling_spread = spread.rolling(window='{}D'.format(window), min_periods=int(window / 2))
                    rolling_mean = rolling_spread.mean().dropna()
                    rolling_std = rolling_spread.std().dropna()

                    ub_arr = {}
                    lb_arr = {}

                    for k in K_ARR:
                        ub_suffix = '_ub_' + str(k)
                        lb_suffix = '_lb_' + str(k)
                        ub_arr[method + ub_suffix] = rolling_mean + k * rolling_std
                        lb_arr[method + lb_suffix] = rolling_mean - k * rolling_std

                    rolling_mean = rolling_mean.dropna()
                    # mean
                    if len(rolling_mean) > 0 and method_category == 'dynamic':
                        ax.plot(rolling_mean, linestyle='--', label='Mean', color='red')

                    # bands (upper, lower)
                    ubs = [rolling_mean]
                    lbs = [rolling_mean]
                    for k in [0.5, 1, 1.5, 2]:
                        ub_suffix = '_ub_' + str(k)
                        lb_suffix = '_lb_' + str(k)
                        ubs.append(ub_arr[method + ub_suffix])
                        lbs.append(lb_arr[method + lb_suffix])

                    for i in range(len(ubs) - 1):
                        lower_ub = ubs[i]
                        upper_ub = ubs[i + 1]

                        upper_lb = lbs[i]
                        lower_lb = lbs[i + 1]

                        ax.fill_between(rolling_mean.index, upper_ub, lower_ub, color='lightgray',
                                        alpha=1 / len(ubs) * i)
                        ax.fill_between(rolling_mean.index, upper_lb, lower_lb, color='#539caf',
                                        alpha=1 / len(lbs) * i)

                ax.set_ylabel(y_label)
                ax.legend(loc='upper left')
                ax.tick_params(labelleft=False, labelright=True, left=False, right=True)
                annotations = [[spread.max(), "H:", "gray"], [spread.min(), "L:", "gray"], [spread[-1], "C:", "blue"]]

                if method_category == 'dynamic' and len(rolling_mean) > 0:
                    annotations = [[rolling_mean[-1], "A:", "red"]] + annotations
                elif method_category == 'total_mean':
                    annotations = [[mean, "A:", "red"]] + annotations
                else:
                    pass

                for annotation in annotations:
                    data, prefix, box_color = annotation[0], annotation[1], annotation[2]
                    bbox_props = dict(boxstyle='larrow', pad=0.01, fc=box_color, ec="b", lw=0)
                    ax.annotate(prefix + '%.3f   ' % data, xy=(1, data), xytext=(0, 0),
                                xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                                bbox=bbox_props, color='white')

        plt.tight_layout()
        plt.close(fig='all')
        return fig, axes

    def spread(self, method, y_label='Spread'):
        fig = plt.figure(figsize=(7, FIG_HEIGHT), dpi=DPI)
        ax = fig.add_subplot(111)

        spread = self.pair.spread[method].loc[self.from_:]
        if len(spread) > 0:
            if method == 'Ratio':
                ax.plot(spread, label='Ratio ({} / {})'.format(self.y_name, self.x_name), color='blue')
            else:
                ax.plot(spread, label=method, color='blue')

            # mean
            mean = self.pair.data[method + '_mean'].dropna().loc[self.from_:]
            if len(mean) > 0:
                if method_category[method] == 'index':
                    ax.plot(mean, linestyle='--', label='Mean', color='red')
                else:
                    ax.axhline(0, color='red', linestyle='--')

                # bands (upper, lower)
                ubs = [mean]
                lbs = [mean]
                for k in [0.5, 1, 1.5, 2]:
                    ub_suffix = '_ub_' + str(k)
                    lb_suffix = '_lb_' + str(k)
                    ubs.append(self.pair.data[method + ub_suffix].loc[self.from_:])
                    lbs.append(self.pair.data[method + lb_suffix].loc[self.from_:])

                for i in range(len(ubs) - 1):
                    lower_ub = ubs[i]
                    upper_ub = ubs[i + 1]

                    upper_lb = lbs[i]
                    lower_lb = lbs[i + 1]

                    ax.fill_between(mean.index, upper_ub, lower_ub, color='lightgray', alpha=1 / len(ubs) * i)
                    ax.fill_between(mean.index, upper_lb, lower_lb, color='#539caf', alpha=1 / len(lbs) * i)

            ax.set_ylabel(y_label)
            ax.legend(loc='upper left')
            ax.tick_params(labelleft=False, labelright=True, left=False, right=True)
            annotations = [[spread.max(), "H:", "gray"], [spread.min(), "L:", "gray"], [spread[-1], "C:", "blue"]]

            if len(mean) > 0:
                annotations = [[mean[-1], "A:", "red"]] + annotations

            for annotation in annotations:
                data, prefix, box_color = annotation[0], annotation[1], annotation[2]
                bbox_props = dict(boxstyle='larrow', pad=0.01, fc=box_color, ec="b", lw=0)
                ax.annotate(prefix + '%.3f   ' % data, xy=(1, data), xytext=(0, 0),
                            xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=FONT_SIZE,
                            bbox=bbox_props, color='white')

        plt.tight_layout()
        plt.close(fig='all')
        return fig, ax

