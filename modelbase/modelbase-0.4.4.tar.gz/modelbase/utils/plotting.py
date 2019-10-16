import numpy as _np
import matplotlib.pyplot as _plt
from matplotlib.colors import colorConverter as _colorConverter


def relative_luminance(color):
    """Calculate the relative luminance of a color"""
    rgb = _colorConverter.to_rgba_array(color)[:, :3]

    # If RsRGB <= 0.03928 then R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4
    rsrgb = _np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

    # L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    rel_luminance = _np.matmul(rsrgb, [0.2126, 0.7152, 0.0722])
    return rel_luminance[0]


def heatmap_from_dataframe(
    df,
    title=None,
    xlabel=None,
    ylabel=None,
    annotate=True,
    colorbar=True,
    ax=None,
    cax=None,
):
    """Create a heatmap of the coefficients"""
    data = df.values
    rows = df.index
    columns = df.columns

    if ax is None:
        fig, ax = _plt.subplots()
    else:
        fig = ax.get_figure()

    # Create heatmap
    hm = ax.pcolormesh(data)

    # Despine axis
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_visible(False)

    # Set the axis limits
    ax.set(xlim=(0, data.shape[1]), ylim=(0, data.shape[0]))

    # Set ticks and ticklabels
    ax.set_xticks(_np.arange(len(columns)) + 0.5)
    ax.set_xticklabels(columns)

    ax.set_yticks(_np.arange(len(rows)) + 0.5)
    ax.set_yticklabels(rows)

    # Set title and axis labels
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if annotate:
        text_kwargs = {"ha": "center", "va": "center"}
        hm.update_scalarmappable()  # So that get_facecolor is an array
        xpos, ypos = _np.meshgrid(_np.arange(len(columns)), _np.arange(len(rows)))
        for x, y, val, color in zip(
            xpos.flat, ypos.flat, hm.get_array(), hm.get_facecolor()
        ):
            text_kwargs["color"] = (
                "black" if relative_luminance(color) > 0.45 else "white"
            )
            ax.text(x + 0.5, y + 0.5, f"{val:.2g}", **text_kwargs)

    if colorbar:
        # Add a colorbar
        cb = ax.figure.colorbar(hm, cax, ax)
        cb.outline.set_linewidth(0)

    # Invert the y axis to show the plot in matrix form
    ax.invert_yaxis()
    return fig, ax, hm
