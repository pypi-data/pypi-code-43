import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numbers

def plot_colored_line(t, x, y, cmap='viridis', linewidth=3, ax=None,
                      colorbar=True):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = mpl.collections.LineCollection(segments, cmap=plt.get_cmap(cmap))
    lc.set_array(t)
    lc.set_linewidth(linewidth)

    if ax is None:
        fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.set_xlim(get_lim(x))
    ax.set_ylim(get_lim(y))

    if colorbar:
        cnorm = mpl.colors.Normalize(vmin=np.min(t), vmax=np.max(t))
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=cnorm)
        sm.set_array(t)
        # can't find a way to set a colorbar simply without grabbing the
        # current axis, so make sure we can restore what the "current axis"
        # was before we did this
        cax = plt.gca()
        plt.sca(ax)
        cbar = plt.colorbar(sm)
        plt.sca(cax)
    return ax

def get_lim(x, margin=0.1):
    min = np.min(x)
    max = np.max(x)
    dx = max - min
    return [min - margin*dx, max + margin*dx]


def cmap_from_list(labels, palette=None, log=False, vmin=None, vmax=None):
    # sequential colormap if numbers
    if isinstance(labels[0], numbers.Number):
        labels = np.array(labels)
        if vmin is None:
            vmin = labels.min()
        if vmax is None:
            vmax = labels.max()
        if log:
            cnorm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
        else:
            cnorm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        if palette is None:
            palette = 'viridis'
        cmap = mpl.cm.get_cmap(palette)
        return lambda l: cmap(cnorm(l))
    # otherwise categorical map
    else:
        if log:
            raise ValueError('LogNorm makes no sense for categorical labels.')
        labels = list(set(labels))
        n_labels = len(labels)
        pal = sns.color_palette(palette, n_colors=n_labels)
        cmap = {labels[i]: pal[i] for i in range(n_labels)}
        return lambda l: cmap[l]

