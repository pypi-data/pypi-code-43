from typing import Optional, Union, Tuple, List
from mypy_extensions import TypedDict

import numpy as np

import matplotlib as mpl
from matplotlib.pyplot import cm
from matplotlib.patches import Patch


Color = Union[str, Tuple[float, float, float]]
Colorscale = TypedDict('Colorscale', {
    'norm': mpl.colors.Normalize,
    'cmap': mpl.colors.Colormap
})


def get_distinct_colors(num):
    """Return `num` colors from colormap."""
    return cm.rainbow(np.linspace(0, 1, num)).tolist()


def create_custom_legend(label_data, ax, **kwargs):
    """Auxiliary function for quick, custom legends."""
    ax.legend(handles=[Patch(facecolor=color, edgecolor=color, label=lbl)
                       for lbl, color in label_data], **kwargs)


def add_identity(ax, *line_args, **line_kwargs):
    """Add identity (y=x) line to given axes."""
    # line plot
    identity, = ax.plot([], [], *line_args, **line_kwargs)

    # react to layout/data changes
    def callback(ax):
        low_x, high_x = ax.get_xlim()
        low_y, high_y = ax.get_ylim()
        low = max(low_x, low_y)
        high = min(high_x, high_y)
        identity.set_data([low, high], [low, high])

    callback(ax)
    ax.callbacks.connect('xlim_changed', callback)
    ax.callbacks.connect('ylim_changed', callback)

    return ax


def create_ranged_colorscale(
    color_mapping: List[Tuple[Tuple[float, float], Color]],
    off_color: Color, bad_color: Optional[Color] = None,
    eps: float = 1e-10
) -> Colorscale:
    """Color data according to discrete mapping.

    Intervals include both boundaries, unless they are
    adjacent. Then the one to the right takes precedence.

    `norm` maps the data values to (0, 1).
    `cmap` maps (0, 1) to a color.
    """
    # prepare input
    levels: List[float] = []
    colors = []

    colors.append(off_color)

    for i in range(len(color_mapping)):
        (start, end), color = color_mapping[i]
        end += eps  # include right side

        if len(levels) == 0:
            levels.extend((start, end))
            colors.append(color)
        else:
            if levels[-1] == start:
                levels.append(end)
                colors.append(color)
            else:
                levels.append(start)
                colors.append(off_color)

                levels.append(end)
                colors.append(color)

    colors.append(off_color)

    # create matplotlib objects
    cmap, norm = mpl.colors.from_levels_and_colors(
        levels, colors, extend='both')

    if bad_color is not None:
        cmap.set_bad(bad_color)

    # make passing to other functions easy
    return {'norm': norm, 'cmap': cmap}


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    res = create_ranged_colorscale([
        ((-9, -8), 'yellow'),
        ((-5, -3), 'red'),
        ((-1, 2), 'green'),
        ((2, 7), 'blue'),
        ((9, 9), 'black')
    ], 'gray', bad_color='pink')

    data = np.r_[np.nan, np.arange(-10, 11, 1)]

    fig, axes = plt.subplots(ncols=data.size)
    for val, ax in zip(data, axes):
        ax.imshow([[val]], **res)
        ax.set_title(val)
        ax.axis('off')

    plt.show()
