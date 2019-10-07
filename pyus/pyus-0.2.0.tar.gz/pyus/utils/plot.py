import matplotlib.ticker as mticker
from matplotlib.axis import Axis
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D


def format_axes(
        axes: Axes, scale: float, decimals: int = 1, minus: str = '−'
) -> None:

    if not isinstance(axes, Axes):
        raise TypeError('Must be a matplotlib Axes object')

    if isinstance(axes, Axes3D):
        raise NotImplementedError('Axes3D not supported')

    format_axis(axis=axes.xaxis, scale=scale, decimals=decimals, minus=minus)
    format_axis(axis=axes.yaxis, scale=scale, decimals=decimals, minus=minus)


def format_axis(
        axis: Axis, scale: float, decimals: int = 1, minus: str = '−'
) -> None:
    # Inspired from: https://stackoverflow.com/a/17816809
    # TODO(@dperdios): what happens if LaTeX typeset used?
    if not isinstance(axis, Axis):
        raise TypeError('Must be a matplotlib Axis object')

    if not isinstance(decimals, int) or decimals < 0:
        raise TypeError('Must be a positive integer')

    fmt = '{{:.{:d}f}}'.format(decimals)
    ticks = mticker.FuncFormatter(
        lambda x, pos: fmt.format(x * scale).replace('-', minus)
    )
    axis.set_major_formatter(ticks)

    # # Inspired from:
    # #   https://matplotlib.org/_modules/matplotlib/axis.html#Axis.iter_ticks
    # major_locs = axis.major.locator()
    # major_ticks = axis.get_major_ticks(len(major_locs))
    # axis.major.formatter.set_locs(major_locs)
    # major_labels = [
    #     axis.major.formatter(val, i) for i, val in enumerate(major_locs)
    # ]
    #
    # # Convert str labels to float
    # # Note: need to replace the minus '-' with matplotlib minus '−' to be
    # #   consistent
    # maj_lbl_float = np.array(
    #     [float(lbl.replace('-', '−')) for lbl in major_labels]
    # )
    #
    # # Scale labels
    # maj_lbl_float *= scale
    #
    # # Update ticks


