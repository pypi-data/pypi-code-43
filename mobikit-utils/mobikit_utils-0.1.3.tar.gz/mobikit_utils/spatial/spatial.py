#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
import numpy as np
import geopandas as gd
from geopy.distance import great_circle, distance

from mobikit_utils.schema.points import constants
from mobikit_utils.schema.constants import srid
from mobikit_utils.spatial.constants import (
    speed_formats,
    distance_formats,
    angular_unit_conversions,
    derive_distance_methods,
    distance_unit_conversions,
)

outlier_stds = 1
time_delta = "time_delta"
low_speed_threshold = 0.5
trip_length_threshold = 5


def to_trips(df, tm, speed, point=constants.primary_spatial, device=None):
    """
    Function to derive trip_ids using basic heuristics, assuming the dataset does not come equipped with the IDs.
    """
    # sort frame
    if not (set([tm, point]).issubset(df.columns)):
        raise KeyError(
            "one or more of the arguments you passed in are not in the dataframe."
        )

    if device:
        sorted_df = _sort(df, device, tm)
    else:
        sorted_df = _sort(df, tm)

    # create time delta col
    sorted_df[time_delta] = _create_time_delta(sorted_df, tm)
    # flag rows where the previous row's speed was low (indicating the end of prev. trip)
    sorted_df = _low_speed_flag(sorted_df, point, speed)

    # flag rows where a new trip might've occurred
    sorted_df = _flag_trips(sorted_df, device)

    # remove trips of very short length. This will also handle idling
    sorted_df = _remove_idles(sorted_df, tm)

    # drop derived columns
    sorted_df = sorted_df.drop([time_delta, "trip_flag", "low_speed"], axis=1)
    # let the user know what's happening
    return sorted_df


def derive_speed(
    df, tm, point=constants.primary_spatial, device=None, trip=None, format="mph"
):
    """
    Derive speed from change in distance and change in time. Also allows for
    multiple output formats to be passed in. The final derived speeds are
    converted to this format before being outputted.
    Options are mph, kmh, and mps
    """

    # Determine the unit for distance derivation and the factor to convert
    # from mps to either mph or kmh
    if format == speed_formats.mph:
        unit = distance_formats.miles
        factor = distance_unit_conversions.mph
    elif format == speed_formats.kmh:
        unit = distance_formats.meters
        factor = distance_unit_conversions.kmh
    elif format == speed_formats.mps:
        unit = distance_formats.meters
        factor = distance_unit_conversions.mps
    else:
        raise KeyError("The format you specified is not mph, kmh, or mps")

    if device and trip:
        cols = [device, trip]
        df.loc[:, "dt"] = df[device].astype(str) + df[trip].astype(str)
    elif device and not trip:
        cols = [device]
        df.loc[:, "dt"] = df[device].astype(str)
    elif trip and not device:
        cols = [trip]
        df.loc[:, "dt"] = df[trip].astype(str)
    elif not trip and not device:
        cols = []
        df.loc[:, "dt"] = 0

    # Sort by the columns passed in
    df = _sort(df, *cols, tm)

    # Time delta in seconds
    # Drops the first row and re-adds a 0 row
    # This makes the distance and time_delta lists equal in length
    time_delta = _create_time_delta(df, tm).fillna(0)

    # Create seperate series for calculation
    series_a = pd.Series(df[point])
    series_b = series_a.shift(1).iloc[1:]
    series_a = series_a.iloc[1:]

    # Distance calculation
    distance = [0] + _derive_distance(
        series_a, series_b, method=derive_distance_methods.great_circle, unit=unit
    )

    # Speed (dist / time). Outputs unit / s, then multiplied by factor
    # to convert to the specific speed unit.
    df.loc[:, "speed_derived"] = (distance / time_delta) * factor

    # Group values by device and trip then multiply the speed to remove incorrect results
    df.loc[:, "speed_derived"] = df["speed_derived"] * (df["dt"] == df["dt"].shift(1))

    df = df.drop("dt", axis=1).fillna(0)

    return df


def _sort(df, *args):
    """
    General purpose sorting method for a dataframe. The sort is based on the ordering of the arguments passed.
    """
    return df.sort_values(by=list(args)).reset_index(drop=True)


def _create_time_delta(df, tm):
    """
    General purpose time-frequency generator. Returns the number of seconds between points.
    """
    datetime_df = pd.to_datetime(df[tm])

    return (datetime_df - datetime_df.shift(1)).dt.total_seconds()


def _low_speed_flag(df, point, speed):
    """
    Flags "low speed" points. Threshold is based on the mean speed.
    """
    low_speed_flag = df[speed].mean() * low_speed_threshold
    df["low_speed"] = df[speed].shift(1) <= low_speed_flag

    return df


def _derive_distance(point_a, point_b, method="geodesic", unit="mi"):
    """
    Derives distance between points.

    Parameters
    ----------
    point_a : pandas.Series
        First series
    point_b : pandas.Series
        Second series
    method : str, {"geodesic", "great_circle", "euclidean"}
        Method for computing distance
    unit : str, {"km", "m", "mi"}
        Distance to convert to before returning.

    Returns
    -------
    List of distances between point_a and point_b, in unit

    Notes
    -----
    Sines is not implemented yet due to use cases. It should be faster than great_circle
    and geodesic but slower than euclidean, but also more accurate than euclidean
    and less accurate than great_circle and geodesic. Its a good algorithm to implement
    later, but there isn't a use for it right now.
    """

    if unit not in angular_unit_conversions.__dict__.keys():
        raise KeyError("The unit requested is not currenly supported.")

    if method not in derive_distance_methods.__dict__.values():
        raise KeyError(
            "The method requested is not currently supported. Please try geodesic, great_circle, or euclidean"
        )

    if method == derive_distance_methods.geodesic:
        distance = _geodesic(point_a, point_b, unit)
    elif method == derive_distance_methods.great_circle:
        distance = _great_circle(point_a, point_b, unit)
    elif method == derive_distance_methods.euclidean:
        distance = _euclidean(point_a, point_b, unit)

    return distance


def _geodesic(point_a, point_b, unit):
    """
    Calculates the geodesic distance between two coordinate points
    Returns a distance based on unit
    """

    return [
        getattr(distance((coord_a.x, coord_a.y), (coord_b.x, coord_b.y)), unit)
        for coord_a, coord_b in zip(point_a, point_b)
    ]


def _great_circle(point_a, point_b, unit):
    """
    Calculates the great_circle distance between two coordinate points.
    Returns a distance based on unit
    """

    return [
        getattr(great_circle((coord_a.x, coord_a.y), (coord_b.x, coord_b.y)), unit)
        for coord_a, coord_b in zip(point_a, point_b)
    ]


def _euclidean(point_a, point_b, unit):
    """
    Calculates the euclidean distance between two spatial points.
    Uses Shapely's euclidean distance function which returns angular
    distance. The result is multiplied to convert to the specified unit
    Returns a distance based on unit
    """

    return [
        (coord_a.distance(coord_b) * getattr(angular_unit_conversions, unit))
        for coord_a, coord_b in zip(point_a, point_b)
    ]


def _flag_trips(df, device=None):
    """
    flag trips based on previous criteria.
    """
    outlier_threshold = df[time_delta].median() + outlier_stds * df[time_delta].mad()
    outlier_flag = (df[time_delta] > outlier_threshold) & (df["low_speed"])
    if device:
        df["trip_flag"] = (
            outlier_flag | (df[time_delta] < 0.0) | (df[device] != df[device].shift(1))
        )
    else:
        df["trip_flag"] = outlier_flag | (df[time_delta] < 0.0)

    return df


def _remove_idles(df, tm):
    """
    Remove long lapses in time.
    """
    # replace trip flags with unique trip_ids (before )
    df["trip_id_derived"] = df["trip_flag"].cumsum()
    # group trips and flag trips that are sufficiently long
    trip_groups = df.groupby("trip_id_derived").count()
    short_trips = set(trip_groups[trip_groups[tm] < trip_length_threshold].index)
    long_trip_flag = ~(df["trip_id_derived"].isin(short_trips))
    # remove trips that are too short. and reset the trip flags
    df["trip_id_derived"] = (df["trip_flag"] & long_trip_flag).cumsum()

    return df
