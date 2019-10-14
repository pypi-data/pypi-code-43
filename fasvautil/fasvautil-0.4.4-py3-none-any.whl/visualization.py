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
import pandas as pd
import seaborn as sns
import tilemapbase
import utm
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle
from utm import OutOfRangeError
from utm.conversion import K0, M1, R, P2, P3, P4, P5, _E, E, E_P2, zone_number_to_central_longitude

from fasvautil.location import UTMLocation, GPSLocation
from fasvautil.osm import project


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
            'figure.figsize' : (4, 3),
            'figure.dpi' : 1200,

            # ticks
            'xtick.labelsize' : 8,
            'ytick.labelsize': 8,

            # label size
            'axes.labelsize' : 10,

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


def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None, strict=True):
    """
    This function convert a list of UTM coordinates into Latitude and Longitude

    Args:

        easting (list[float]): Easting value of UTM coordinate
        northing (list[float]): Northing value of UTM coordinate
        zone number (int): Zone Number is represented with global map numbers of an UTM Zone Numbers Map.
                           More information see utmzones [1]_
        zone_letter (str): Zone Letter can be represented as string values. Where UTM Zone Designators
                           can be accessed in [1]_

        northern (bool): You can set True or False to set this parameter. Default is None


   .. _[1]: http://www.jaworski.ca/utmzones.htm

    """
    if not zone_letter and northern is None:
        raise ValueError('either zone_letter or northern needs to be set')

    elif zone_letter and northern is not None:
        raise ValueError('set either zone_letter or northern, but not both')

    if strict:
        valid_coordinates = np.all((easting > 100000, easting < 1000000, northing >= 0, northing <= 10000000), axis=0)

        easting = easting[valid_coordinates]
        northing = northing[valid_coordinates]

    if not 1 <= zone_number <= 60:
        raise OutOfRangeError('zone number out of range (must be between 1 and 60)')

    if zone_letter:
        zone_letter = zone_letter.upper()

        if not 'C' <= zone_letter <= 'X' or zone_letter in ['I', 'O']:
            raise OutOfRangeError('zone letter out of range (must be between C and X)')

        northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * np.sin(2 * mu) +
             P3 * np.sin(4 * mu) +
             P4 * np.sin(6 * mu) +
             P5 * np.sin(8 * mu))

    p_sin = np.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = np.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = np.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = np.power(_E * p_cos, 2)
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return (np.degrees(latitude),
            np.degrees(longitude) + zone_number_to_central_longitude(zone_number))


def draw_tile(lat, lon, ax=None, style=tilemapbase.tiles.Stamen_Toner, zoom=12):
    """
    Plot a OSM tile as background image into the given ax.
    Args:
        lat (tuple[int, int]):      latitude extend
        lon (tuple[int, int]):      longitude extend
        ax (plt.Axes):              The axes to draw the particles onto. By default, the current axes is used.
        style (tilemapbase.tiles):  The style of the tiles.

    Returns:

    """

    if ax is None:
        _, ax = plt.subplots(1, 1)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    extent = tilemapbase.Extent.from_lonlat(lon[0], lon[1], lat[0], lat[1])

    plotter = tilemapbase.Plotter(extent, style, zoom=zoom)

    plotter.plot(ax, style)

    return ax


def tilemap_project(particles, zone_number, zone_letter):
    """
    Project to the particle location onto the tilemap.


    Args:
        particles (np.ndarray):     A list of utm locations as N*2 array.
        zone_number (int):          The UTM zone number
        zone_letter (str):          The UTM zone letter

    Returns:
        list[float], list[float]:  Projected particle locations as two lists.
    """

    lat, lon = to_latlon(easting=particles[:, 0], northing=particles[:, 1], zone_number=zone_number,
                         zone_letter=zone_letter)

    return project(latitude=lat, longitude=lon)


def extend_from_utm(easting, northing, utm_zone, padding=25):
    """
    Get the plotting extend from the utm coordinates

    Args:
        easting (list[float]):        UTM easting coordinates
        northing (list[float]):       UTM northing coordinates
        utm_zone ((int, str)):  The UTM zone
        padding (int):          Padding around the UTM location

    Returns:

    """
    east = int(np.min(easting)) - padding, int(np.max(easting)) + padding
    north = int(np.min(northing)) - padding, int(np.max(northing)) + padding

    lat_min, lon_min = utm.to_latlon(east[0], north[0], *utm_zone)

    lat_max, lon_max = utm.to_latlon(east[1], north[1], *utm_zone)

    return [lat_min, lat_max], [lon_min, lon_max]


def plot_particles(particles, orientation, utm_zone, ax, weight=None):
    """
    Draw the particles as arrows

    Args:
        particles (np.ndarray):     A list of utm locations as N*2 array.
        orientation (np.ndarray):   A list of particle orientation as radians.
        utm_zone (tuple[int, str]): The UTM zone number and letter as tuple.
        ax (plt.Axes):              The axes to draw the particles onto. By default, the current axes is used.
        weight (None|np.ndarray):   A list if particle weights.

    Returns:

    """

    lat, lon = to_latlon(particles[:, 0], particles[:, 1], *utm_zone)

    x, y = project(latitude=lat, longitude=lon)

    if weight is not None:
        ax.quiver(x,
                  y,
                  np.cos(orientation) * 1,
                  np.sin(orientation) * 1,
                  weight,
                  cmap=sns.cubehelix_palette(8, start=.5, rot=-.75, as_cmap=True),
                  units='width')
    else:
        ax.quiver(x,
                  y,
                  np.cos(orientation) * 1,
                  np.sin(orientation) * 1,
                  cmap=sns.cubehelix_palette(8, start=.5, rot=-.75, as_cmap=True),
                  units='width')


def plot_particles_on_osm(particles, orientations, utm_zone, weight=None, zoom=20,  ax=None, extend=None):
    """
    Plot the particles on a OSM map.

    Args:
        particles (np.ndarray):                                     A list of utm locations as N*2 array.
        orientations (np.ndarray):                                  A list of particle orientation as radians.
        utm_zone (tuple[int, str]):                                 The UTM zone number and letter as tuple.
        weight  (np.ndarray):                                       A list of particle weights.
        zoom (int):                                                 OpenStreetmap zoom level
        ax (plt.Axes):                                              The Axe to draw into
        extend (tuple[tuple(float, float), tuple(float, float)]):   The extend of the region to draw.

    Returns:
        plt.Axes:                   The new axe plotted onto

    """

    if ax is None:
        _, ax = plt.subplots(1, 1)

    if extend is None:
        # get the view extend
        extend = extend_from_utm(particles[:, 0], particles[:, 1], utm_zone)

    # draw the background
    draw_tile(lat=extend[0], lon=extend[1], zoom=zoom, ax=ax)

    # plot the particle location including their orientation
    plot_particles(particles, orientations, utm_zone, ax=ax, weight=weight)

    return ax


def plot_way(ax, way, **kwargs):
    """
    Plots the given `way` on the specified `ax` with the specified `color`.

    Args:
        ax (plt.Axes): The pyplot Axes.
        way (list[tuple[float, float]]): The overpy.Node coordinates
        color (tuple[float, float, float, float]): A RGBA color.

    Returns:

    """
    xs = []
    ys = []
    for w in way:
        x, y = tilemapbase.project(latitude=w[0], longitude=w[1])

        xs.append(x)
        ys.append(y)

    return ax.plot(xs, ys, zorder=1002, **kwargs)


def mark_locations(locations, descriptions, sc_kwargs, ax, xoffset=0.01):
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

        ax.text(right_edge + 0.02, 0.95 - (0.04 * idx), description, fontsize=8, transform=ax.transAxes)


def mark_location(location, project=True, **kwargs):
    """

    Args:
        location (GPSLocation|UTMLocation):
        project (bool): Project the location on a tile.
        **kwargs:

    Returns:

    """
    if isinstance(location, UTMLocation):
        location = location.as_gps()

    if project:
        x, y = tilemapbase.project(latitude=location.latitude, longitude=location.longitude)
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


def plot_orientation_dist(weights, ax=None):
    """
    Plot the weight distribution in `ax`.

    Args:
        weights (np.ndarray):       A list of particle weights
        ax (plt.Axes):              The axe to plot into

    Returns:

    """

    w_ax = sns.distplot(weights, ax=ax, norm_hist=True)
    w_ax.set_title('Distribution of particle orientations')
    w_ax.set(xlabel='Orientations in radians')
    w_ax.set_xlim([-0.8, 8.8])

    return w_ax


def rotate_xtick_labels(ax, rotation):
    """
    Rotates the labels of the ticks on the x axis by `rotation`.

    Args:
        ax (plt.Axes):      The axes
        rotation (float):   The rotation angle in radians

    """

    plt.setp(ax.get_xticklabels(), rotation=rotation, horizontalalignment='right')


def draw_trajectory(trajectory, ax=None, **kwargs):
    """
    Draw the given trajectory

    Args:
        trajectory (list[tuple[GPSLocation, wayid]]): The trajectory as a list of GPSLocations and its mapped way id.

    Returns:

    """

    if ax is None:
        _, ax = plt.subplots()

    padding = 0.005

    points = np.asarray([t[0].position for t in trajectory])

    draw_tile(
        lat=(np.min(points[:, 0]) - padding, np.max(points[:, 0]) + padding),
        lon=(np.min(points[:, 1]) - padding, np.max(points[:, 1]) + padding),
        ax=ax
    )

    return ax, plot_way(ax, points, **kwargs)


def show_trajectory(trajectory, osm=False, ax=None, **kwargs):
    """
    Show the trajectory and optionally on a OpenStreetMap.

    Args:
        trajectory (pd.DataFrame):  The trajectory as a pandas dataframe.
        osm (bool):                 To indicate if the trajectory should be drawn onto a OSM map.
        ax (plt.Axes):              An optional axes to plot onto. Otherwise, a new axes is created.
        **kwargs:                   Additional arguments passed to plt.plot.

    """

    way_ids = pd.unique(trajectory['wayid'])

    colors = color_palette(way_ids.size)

    if osm:
        padding = 0.005

        min_ = lambda x, y: min([z.position[y] for z in x['location']])
        max_ = lambda x, y: max([z.position[y] for z in x['location']])

        lat_min, lat_max, lon_min, lon_max = min_(trajectory, 0), max_(trajectory, 0), \
                                             min_(trajectory, 1), max_(trajectory, 1)

        ax = draw_tile(
            lat=(lat_min - padding, lat_max + padding),
            lon=(lon_min - padding, lon_max + padding),
            ax=ax
        )

    for idx, w in enumerate(way_ids):

        entries = trajectory[trajectory.wayid == w]

        if len(entries) == 1:
            # pass

            mark_location(entries.location.item(), marker='o', markersize=1, fillstyle='full',
                          markerfacecolor=colors[idx], project=osm, ax=None)
        else:
            points = np.asarray([t[0].position for t in list(entries.itertuples(index=False, name=None))])

            if 'linestyle' not in kwargs:
                kwargs['linestyle'] = '-'

            if 'linewidth' not in kwargs:
                kwargs['linewidth'] = 1

            plot_way(ax, points, **kwargs, color=colors[idx])


def color_palette_to_cmap(palette):
    """
    Convert the given seaborn color palette to a matplotlib cmap
    Args:
        palette:

    Returns:
        list[float]: A list of colors
    """
    return ListedColormap(palette.as_hex())
