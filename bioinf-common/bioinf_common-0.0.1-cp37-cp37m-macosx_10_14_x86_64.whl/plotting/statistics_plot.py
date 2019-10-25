import itertools

from typing import Any, List, Mapping

from scipy.stats import mannwhitneyu  # ks_2samp

import seaborn as sns
import matplotlib.pyplot as plt


def _get_asteriks(
    pvalue: float,
    pthres: List[float] = [.05, .01, .001, .0001]
) -> str:
    txt = 'ns'
    for i, t in enumerate(sorted(pthres, reverse=True)):
        if pvalue <= t:
            txt = '*' * (i+1)
        else:
            break
    return txt


def annotated_boxplot(
    anno_kws: Mapping[str, Any] = None,
    **kwargs: Any
) -> None:
    anno_kws = anno_kws or {}

    # get default arguments
    pval_func = anno_kws.pop('pval_func', mannwhitneyu)
    show_asteriks = anno_kws.pop('show_asteriks', False)
    subset = anno_kws.pop('subset', None)
    label_size = anno_kws.pop('label_size', plt.rcParams['font.size'])
    if len(anno_kws) > 0:
        raise TypeError(f'Invalid parameters: {anno_kws.keys()}')

    x = kwargs['x']
    y = kwargs['y']
    data = kwargs['data']

    # draw standard boxplot
    g = sns.boxplot(**kwargs)

    # determine which distributions to compare
    if subset is None:
        subset = itertools.combinations(
            [l.get_text() for l in g.get_xticklabels()], 2)

    tick_idx_map = {l.get_text(): i
                    for i, l in zip(g.get_xticks(), g.get_xticklabels())}

    # commence plot
    y_offset = 0
    for col1, col2 in subset:
        x1 = tick_idx_map[col1]
        x2 = tick_idx_map[col2]

        # compute p-value
        series1 = data.loc[data[x] == col1, y]
        series2 = data.loc[data[x] == col2, y]
        _, pval = pval_func(series1, series2)

        # plot lines
        h = 2
        y_pos = data[y].max() + 2
        plt.plot(
            [x1, x1, x2, x2],
            [
                y_offset + y_pos, y_offset + y_pos + h,
                y_offset + y_pos + h, y_offset + y_pos
            ],
            lw=1.5, color='black')

        # generate and display label
        if show_asteriks:
            txt = _get_asteriks(pval)
        else:
            txt = round(pval, 3)

        plt.text(
            (x1 + x2) * .5, y_offset + y_pos + h,
            txt,
            ha='center', va='bottom',
            color='black', fontsize=label_size)

        # move to next lane
        y_offset += 10


def annotated_barplot(
    anno_kws: Mapping[str, Any] = None,
    **kwargs: Any
) -> None:
    anno_kws = anno_kws or {}

    label_offset = anno_kws.pop('label_offset', 20)
    label_size = anno_kws.pop('label_size', plt.rcParams['font.size'])
    if len(anno_kws) > 0:
        raise TypeError(f'Invalid parameters: {anno_kws.keys()}')

    g = sns.barplot(**kwargs)

    # for i, row in enumerate(kwargs['data'].itertuples()):
    #     g.annotate(
    #         f'{row.value:,.1f}', (i, row.value), xycoords='data',
    #         ha='center', xytext=(0, 3), textcoords='offset pixels')

    for p in g.patches:
        # handle custom baseline
        height = p.get_height() + kwargs.get('bottom', 0)

        g.annotate(
            f'{height:,.1f}',
            (p.get_x() + p.get_width() / 2., height),
            ha='center', va='center', color='gray', fontsize=label_size,
            xytext=(0, label_offset), textcoords='offset pixels')


if __name__ == '__main__':
    import numpy as np
    import pandas as pd

    # generate data
    np.random.seed(1)
    df = pd.DataFrame({
        'group': ['A'] * 10 + ['B'] * 10 + ['C'] * 10,
        'value': np.r_[
            np.random.normal(2, size=10),
            np.random.normal(3, size=10),
            np.random.normal(4, size=10)
        ]
    })
    print(df.head())

    # plot
    plt.subplot(121)
    annotated_boxplot(
        x='group', y='value', data=df,
        anno_kws=dict(show_asteriks=False, subset=[('A', 'B'), ('B', 'C')]))

    plt.subplot(122)
    annotated_barplot(
        x='group', y='value', data=df.groupby('group').mean().reset_index())

    plt.show()
