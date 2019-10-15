import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import math

from hexagonmodel.coordinates import oddq_to_square_grid


def plot_leaf_axes(leaf, figsize, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.get_figure()
    ax.set_aspect("equal")

    c, r = leaf.cells.shape
    x_lower = -1
    x_upper = 1 + 3 / 2 * (c - 1)
    y_lower = -math.sqrt(3) * 0.5
    y_upper = math.sqrt(3) * r
    ax.set_xlim(x_lower, x_upper)
    ax.set_ylim(y_lower, y_upper)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def plot_leaf_cells(
    leaf, ax, concentrations, min_conc=None, max_conc=None, alpha=None, **kwargs
):
    if concentrations is None:
        concentrations = np.ones(leaf.gridsize)
        min_conc = 0
        max_conc = 1
    else:
        if min_conc is None:
            min_conc = np.min(
                concentrations[leaf.cells != 0]
            )  # Otherwise this is always 0
        if max_conc is None:
            max_conc = np.max(concentrations)
        if min_conc == max_conc:
            max_conc += 0.1
    normalized_concentrations = (concentrations - min_conc) / (max_conc - min_conc)

    def add_hexagon(c, r, color, alpha, ax=ax):
        ax.add_patch(
            patches.RegularPolygon(
                oddq_to_square_grid((c, r)),
                numVertices=6,
                radius=1,
                facecolor=color,
                alpha=alpha,
                orientation=np.radians(30),
                edgecolor="k",
            )
        )

    # Photosynthetic cells
    for c, r in zip(*np.where(leaf.cells == 1)):
        if alpha is None:
            al = max(normalized_concentrations[c, r], 0.05)
        else:
            al = alpha
        add_hexagon(c, r, "green", al)

    # Veins
    for c, r in zip(*np.where(leaf.cells == 2)):
        if alpha is None:
            al = max(normalized_concentrations[c, r], 0.05)
        else:
            al = alpha
        add_hexagon(c, r, "brown", al)

    # Stoma
    for c, r in zip(*np.where(leaf.cells == 3)):
        if alpha is None:
            al = max(normalized_concentrations[c, r], 0.05)
        else:
            al = alpha
        add_hexagon(c, r, "blue", al)
    return ax


def plot_leaf_cell_annotations(leaf, ax, concentrations, **kwargs):
    local_kwargs = {"ha": "center", "fontsize": 12}
    if kwargs:
        local_kwargs.update(kwargs)
    for c, r in zip(*np.where(leaf.cells != 0)):
        ax.annotate(
            f"{concentrations[c, r]:.2g}", oddq_to_square_grid((c, r)), **local_kwargs
        )


def plot_leaf_cell_coordinates(leaf, ax):
    for c, r in zip(*np.where(leaf.cells != 0)):
        ax.annotate(f"{c, r}", oddq_to_square_grid((c, r)), ha="center")


def plot_leaf(
    leaf,
    concentrations=None,
    min_conc=None,
    max_conc=None,
    figsize=(10, 10),
    ax=None,
    annotate=False,
    alpha=None,
    **kwargs,
):
    fig, ax = plot_leaf_axes(leaf, figsize=figsize, ax=ax)
    ax = plot_leaf_cells(leaf, ax, concentrations, min_conc, max_conc, alpha, **kwargs)
    if annotate:
        ax = plot_leaf_cell_annotations(leaf, ax, concentrations, **kwargs)
    return fig, ax


def time_lapse(leaf, y, filename=None, figsize=(10, 10), ffmpeg_path="/usr/bin/ffmpeg"):
    plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path
    fig, ax = plot_leaf_axes(leaf=leaf, figsize=figsize)
    plt.close()

    def init():
        ax.patches = []
        return fig, ax

    def update_func(frame):
        ax.patches = []
        ax.texts = []
        y_current = y[frame]
        plot_leaf_cells(leaf=leaf, ax=ax, concentrations=y_current)
        plot_leaf_cell_annotations(leaf=leaf, ax=ax, concentrations=y_current)
        return None

    anim = animation.FuncAnimation(
        fig, update_func, frames=list(range(len(y) // 2)), init_func=init, repeat=False
    )
    return anim
