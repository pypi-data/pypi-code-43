# conduit.stream
# Utilities for working with BTrDB streams
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Mon Oct 14 10:19:56 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: stream.py [] benjamin@bengfort.com $

"""
Utilities for working with BTrDB streams
"""

##########################################################################
## Imports
##########################################################################

import pandas as pd

from btrdb.point import RawPoint, StatPoint


def points_to_series(points, datetime64_index=True, agg="mean", dtype=None, name=None):
    """
    Converts RawPoints into a pd.Series object with a time index.

    Note that this functionality exists in btrdb.StreamSet, but is implemented here as
    a helper function to wrap individual btrdb.Stream objects.

    Parameters
    ----------
    points : iterable of btrdb.RawPoint, btrdb.StatPoint, or tuple(point, version)
        The RawPoints to convert or, more likely, the result of a stream.values query,
        the tuple of (RawPoint, version) information that is returned.

    datetime64_index : bool, default: True
        Convert the timestamps into a datetime64 object, otherwise leave them as int64
        objects, nanoseconds after epoch.

    agg : str, default: "mean"
        Specify the StatPoint field (e.g. aggregating function) to create the Series
        from. Must be one of "minv", "meanv", "maxv", "count", or "stddev". This
        argument is ignored if RawPoint values are passed into the function.

    dtype : str, numpy.dtype, or ExtensionDtype, optional
        dtype for the output Series. If not specified, this will be inferred from the
        data, usually as np.float64.

    name : str, optional
        The label to assign the series. Generally the UUID or name of the stream.

    Examples
    --------
    >>> start, end = "2019-04-07T13:45:00.000", "2019-04-07T13:46:00.000"
    >>> series = points_to_series(stream.values(start, end), name=str(stream.uuid))
    >>> series.head()

    >>> series = points_to_series(
    ...     stream.windows(start, end, ns_delta(seconds=1), depth=38), agg="count")
    >>> series.head()
    """
    # create data structures for stream materialization
    times, values = [], []
    for point in points:
        # ignore version information returned from BTrDB queries
        if isinstance(point, (tuple, list)):
            point = point[0]

        if isinstance(point, RawPoint):
            times.append(point.time)
            values.append(point.value)

        elif isinstance(point, StatPoint):
            times.append(point.time)

            try:
                values.append(getattr(point, agg))
            except AttributeError as e:
                msg = (
                    "'{}' is not a btrdb.StatPoint aggregate field, "
                    "specifiy one of min, mean, max, count, or stddev"
                ).format(agg)
                raise ValueError(msg) from e

        else:
            raise ValueError("unknown point type '{}'".format(type(point)))

    # parse epoch time into datetime objects
    if datetime64_index:
        times = pd.Index(times, dtype='datetime64[ns]')

    return pd.Series(values, index=times, dtype=dtype, name=name)
