import matplotlib.pyplot as plt


def initPlot(mn, labels, lim, figSize=(16, 9), share=('none', 'none'),
        spkw=None, gskw=None):
    '''
    Initialize a plot with both axis label and tick shown

    Parameters
    ----------
    mn: 2-tuple, (number of rows, number of columns)
    labels: list of 2-tuple str, string for x and y axis. Allow latex.
    lim: list of 2-tuple, limit for x and y axis.
    figSize: 2-tuple, default (16, 9). Size of the figure in inch. DPI is fixed
             at 300.
    share: 2-tuple, default ('none', 'none'). Whether to share x or y axis.
    spkw: dict, keywords to pass to add_subplot
    gskw: dict, keywords to pass to GridSpec

    Returns
    -------
    fig: matplotlib.pyplot.Figure, the figure itself
    ax: matplotlib.pyplot.axes, the axes in 2D array
    '''
    # Set up the Figure and axes
    fig, ax = plt.subplots(nrows=mn[0], ncols=mn[1], sharex=share[0],
            sharey=share[1], squeeze=False, subplot_kw=spkw, gridspec_kw=gskw,
            figsize=figSize, dpi=300)
    # Set up the limit and labels for each axes
    for i in range(mn[0]):
        for j in range(mn[1]):
            num = i * mn[1] + j
            ax[i][j].set_xlabel(labels[num][0], fontsize=24)
            ax[i][j].set_xlim(lim[num][0])
            ax[i][j].set_ylabel(labels[num][1], fontsize=24)
            ax[i][j].set_ylim(lim[num][1])
            ax[i][j].tick_params(axis='both', which='major', labelsize=20)
    return fig, ax


def plotLine(ax, x=None, y=None, lw=2, ls='--', c='#000000FF', label=None):
    '''
    Plot a line

    Parameters
    ----------
    ax: matplotlib.pyplot.axes, the axes to plot on
    x: int/float, default None. x coord
    y: int/float, default None. y coord
    lw: int, default 2. Width of the line
    ls: str, default '--'. String for linestyle
    c: str, default '#000000FF'. Hex colorcode with transparency.
    label: str, default None. Legend

    Returns
    -------
    None
    '''
    if x is not None:
        ax.plot([x, x], [-65535.0, 65535.0], ls=ls, c=c, label=label,
                marker='None', lw=lw)
    if y is not None:
        ax.plot([-65535.0, 65535.0], [y, y], ls=ls, c=c, label=label,
                marker='None', lw=lw)


def formatColorBar(cb, cblabel):
    '''
    Format the color bar by adding a fontsize=24 label and changing the tick
    label to size 20.

    Parameters
    ----------
    cb: matplolib.colorbar intance, the color bar to modify
    cblabel: str, label for the color bar

    Returns
    -------
    None
    '''
    cb.set_label(cblabel, fontsize=24)
    cb.ax.tick_params(labelsize=20)
