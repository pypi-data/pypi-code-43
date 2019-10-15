# -*- coding: utf-8 -*-
# Copyright (c) 2019 by Lars Klitzke, Lars.Klitzke@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tilemapbase
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle
from tilemapbase.tiles import build_OSM

from fasvautil import osm
from fasvautil.location import UTMLocation, GPSLocation


def format_float(value, decimals):
    """
    Format the given float value as str with the specified number of decimal places.
    Args:
        value (float|list[float]|tuple[float, ...]):  The value to format as string
        decimals (int): The number of decimal places

    Returns:
        str: The float value was string.
    """
    if not isinstance(value, (list, tuple, np.ndarray)):
        value = [value]

    return [format(v, ".{}f".format(decimals)) if v is not None else None for v in value]


def color_palette(color='deep', num_color=None):
    """
    Create a colorpalette with the given number of colors.

    Args:
        num_color (int): The number of colors

    Returns:
        list[tuple[float, float, float, float]]: A list of RGB values.

    """

    return sns.color_palette(color, num_color)


def set_seaborn_style(**kwargs):
    """
    Set the default style for all figures.
    """
    sns.set_style("whitegrid")

    sns.set_context('paper')

    palette = color_palette()
    sns.set_palette(palette)

    from matplotlib import rcParams
    rcParams.update(
        {
            # general figure
            'figure.figsize': (4, 3),
            'figure.dpi': 1200,

            # ticks
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,

            # label size
            'axes.labelsize': 10,

            # set the default style to a serif font used within IEEE papers
            'font.family': 'serif',
            'font.serif': 'Computer Modern Roman',

            # font in LaTeX math mode
            'text.usetex': True,

            'mathtext.fontset': 'cm',
            'mathtext.rm': 'MathJax_Math',
            'mathtext.it': 'MathJax_Math:italic',
            'mathtext.bf': 'MathJax_Math:bold'
        })

    if kwargs is not None:
        rcParams.update(kwargs)


def draw_tile(lat, lon, ax=None, style=build_OSM(), zoom=20):
    """
    Plot a OSM tile as background image into the given ax.
    Args:
        lat (tuple[int, int]):      latitude extend
        lon (tuple[int, int]):      longitude extend
        ax (plt.Axes):              The axes to draw the particles onto. By default, the current axes is used.
        style (tilemapbase.tiles):  The style of the tiles.
        zoom (int):                 The zoom level

    Returns:
        plt.Axes:   The axes with the minimap

    """

    if ax is None:
        _, ax = plt.subplots(1, 1)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    extent = tilemapbase.Extent.from_lonlat(lon[0], lon[1], lat[0], lat[1])

    plotter = tilemapbase.Plotter(extent, style, zoom=zoom)

    plotter.plot(ax, style)

    return ax


def mark_locations(locations, descriptions, sc_kwargs, ax, xoffset=0.01, **kwargs):
    """
    Mark locations in a plot.
    Args:
        locations (list[UTMLocation|GPSLocation]):   A list of UTMLocation to mark in the plot
        descriptions (list[str]):                       A short description of each location for the legend
        ax (plt.Axes):                                  The axes to plot onto
        sc_kwargs (list[dict]):                         A list of keyword arguments passed to `scatter()`
        xoffset (float):                                The offset in x
    """

    assert len(locations) == len(descriptions)
    assert len(locations) == len(sc_kwargs)

    right_edge = xoffset

    for idx, (location, description, kwargs) in enumerate(zip(locations, descriptions, sc_kwargs)):

        if 'ax' in kwargs:
            kwargs['ax'] = ax

        mark_location(location, ax=ax, **kwargs)

        # show the legend for the PF location
        ax.add_patch(Circle((right_edge, 0.96 - (0.04 * idx)), 0.01, fc=kwargs.get('color', None),
                            alpha=kwargs.get('alpha', 0.8), transform=ax.transAxes))

        ax.text(right_edge + 0.02, 0.95 - (0.04 * idx), description, fontsize=kwargs.get('fontsize', 8),
                transform=ax.transAxes)


def mark_location(location, project=True, **kwargs):
    """
    Mark the location on the Axes.

    Args:
        location (GPSLocation|UTMLocation):     The location to project
        project (bool):                         Project the location on the tilemap.
        **kwargs:

    Returns:

    """
    if isinstance(location, UTMLocation):
        location = location.as_gps()

    if project:
        x, y = osm.project(latitude=location.latitude, longitude=location.longitude)
    else:
        x, y = location.longitude, location.latitude

    if 'ax' in kwargs:
        ax = kwargs['ax']
        del kwargs['ax']
    else:
        ax = plt.gca()

    if 'marker' not in kwargs:
        kwargs['marker'] = 'o'
    ax.plot(x, y, **kwargs)


def rotate_xtick_labels(ax, rotation):
    """
    Rotates the labels of the ticks on the x axis by `rotation`.

    Args:
        ax (plt.Axes):      The axes
        rotation (float):   The rotation angle in radians

    """

    plt.setp(ax.get_xticklabels(), rotation=rotation, horizontalalignment='right')


def color_palette_to_cmap(palette):
    """
    Convert the given seaborn color palette to a matplotlib cmap
    Args:
        palette:

    Returns:
        list[float]: A list of colors
    """
    return ListedColormap(palette.as_hex())
