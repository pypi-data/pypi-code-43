# conduit.base
# Base classes for Conduit classes and stream set wrappers
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Thu Jun 20 15:27:56 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: base.py [] benjamin@bengfort.com $

"""
Base classes for Conduit classes and stream set wrappers
"""

##########################################################################
## Imports
##########################################################################

import uuid
import numpy as np
import pandas as pd

from tabulate import tabulate
from btrdb.stream import StreamSet
from collections import defaultdict

from .constants import LABEL, PHASE, UNIT


##########################################################################
## Conduit
##########################################################################

class Conduit(object):
    """
    A Conduit is the base-class for all stream-related data transformations.
    It wraps a py:class:`~btrdb.stream.StreamSet` to coordinate both data
    and metadata related operations. Conduits can be composed of one stream
    or multiple streams - more specific Conduits such as Phasors coordinate
    very specific interactions between streams of different units.

    Conduit objects validate the streams that are passed to them - ensuring
    that the stream composition will allow for valid downstream computations.

    Parameters
    ----------
    streams : list of `~btrdb.stream.Stream` objects
        The stream objects whose computations are managed together.

    version : int, default=0
        Snapshot all queries to the specified version. By default the Conduit
        simply queries the latest version of the streams.

    njobs : int, default=1
        Use joblib to increase the performance of conduit transformations by
        parallelizing operations across the specified number of workers.

    Example
    -------
    >>> db = btrdb.connect()
    >>> conduit = Conduit(db.streams(uuid1, uuid2, uuid3))
    """

    @classmethod
    def from_streamset(klass, streamset, **kwargs):
        return klass(*[s for s in streamset], **kwargs)

    def __init__(self, *streams, version=0, njobs=1):
        self.version = version
        self.njobs = njobs
        self._streams = StreamSet(streams)
        self._transformers = defaultdict(list)

    def apply(self, transformer, mask=None):
        """
        Apply a transformation to the streams in the conduit when fetching
        data. If a mask is specified, apply the transfomer only to the
        streams that match the index of the mask.
        """
        if mask is None:
            mask = np.ones(len(self), dtype=np.bool)

        for idx in np.where(mask)[0]:
            self._transformers[idx].append(transformer)

    def _apply_stream_transformations(self, idx, stream, times, values, datetime64_index=True):
        """
        A helper function for values, windows, and aligned_windows to create
        the pd.Series object with all transformations applied.
        """
        if datetime64_index:
            times = pd.Index(times, dtype='datetime64[ns]')

        series = pd.Series(data=values, index=times, name=stream.uuid)
        meta, _ = stream.annotations()
        tags = stream.tags()

        # Apply all of the transformations belonging to the stream
        for transformer in self._transformers[idx]:
            series = transformer(series, tags=tags, annotations=meta)

        return series

    def values(self, start, end, datetime64_index=True):
        """
        Returns a dataframe with the raw values of the streams between
        the start and end time and all transformations applied to the data.

        TODO: Handle stream versions in values selection
        """
        data = []
        for idx, stream in enumerate(self):
            times, values = [], []
            for point, _ in stream.values(start, end, version=0):
                times.append(point.time)
                values.append(point.value)

            data.append(self._apply_stream_transformations(
                idx, stream, times, values, datetime64_index=datetime64_index
            ))

        return pd.concat(data, axis=1)

    def windows(self, start, end, width, depth=0, agg="mean", datetime64_index=True):
        """
        Returns a dataframe with window based aggregates applied. The
        values are the specified agg, e.g. mean, max, min, etc.

        TODO: Handle stream versions in windows query
        """
        data = []
        for idx, stream in enumerate(self):
            times, values = [], []
            for point, _ in stream.windows(start, end, width, depth=depth, version=0):
                times.append(point.time)
                values.append(getattr(point, agg))

            data.append(self._apply_stream_transformations(
                idx, stream, times, values, datetime64_index=datetime64_index
            ))

        return pd.concat(data, axis=1)

    def aligned_windows(self, start, end, pointwidth, agg="mean", datetime64_index=True):
        """
        Returns a dataframe with window based aggregates applied. The
        values are the specified agg, e.g. mean, max, min, etc.

        TODO: Handle stream versions in windows query
        """
        data = []
        for idx, stream in enumerate(self):
            times, values = [], []
            for point, _ in stream.aligned_windows(start, end, pointwidth, version=0):
                times.append(point.time)
                values.append(getattr(point, agg))

            data.append(self._apply_stream_transformations(
                idx, stream, times, values, datetime64_index=datetime64_index
            ))

        return pd.concat(data, axis=1)

    def describe(self):
        """
        Returns a table that describes the streams composed by the conduit.
        """
        table = [["UUID", "Collection", "Label", "Phase", "Units"]]
        for stream in self._streams:
            tags = stream.tags()
            meta, _ = stream.annotations()
            table.append([
                str(stream.uuid),
                stream.collection,
                meta.get(LABEL, ""),
                meta.get(PHASE, ""),
                tags.get(UNIT, ""),
            ])
        return tabulate(table, headers="firstrow", tablefmt="simple")

    def subset(self, mask=None, func=None):
        """
        Returns a Conduit that is a subset of the original streamset
        determined by two mechanisms: first a bitmask is applied to
        determine relevant streams then a filtering function is applied.
        You can specify both a mask and a func, this is the equivalent
        of a filter [mask & func].

        TODO: Should the subset also contain the transformers?

        Parameters
        ----------
        mask : array of bool
            The mask must have same length as the current list of streams
            and is converted to a boolean array. Anything marked as True
            in the mask is kept in the subset.

        func : function
            The filter function accepts a stream as its first argument and
            must return True if the stream is part of subset, False to be
            excluded from the subset.

        Returns
        -------
        conduit : Conduit
            A clone of the superset that contains only the masked items.
            Note that an exception is raised if all streams are masked,
            so this function will not return an empty conduit.
        """
        subset = np.ones(len(self), dtype=np.bool)

        if mask is not None:
            # Convert the mask if it is passed in
            mask = np.asarray(mask, dtype=np.bool)
            subset &= mask

        if func is not None:
            # Convert the func to a mask and and it to the subset
            fmask = np.array([func(s) for s in self], dtype=np.bool)
            subset &= fmask

        streams = [self._streams[idx] for idx in np.where(subset)[0]]
        return Conduit(*streams)

    def phase_mask(self, *phases):
        """
        Returns a stream mask for all specified phases (temporary method).

        Parameters
        ----------
        phases : str
            A list of phases, e.g. 'A', 'B', 'C', 'R', '1', '+', etc. to
            create the phase mask for. Is converted into a set.
        """
        phases = frozenset(phases)
        mask = []
        for stream in self:
            meta, _ = stream.annotations()
            mask.append(meta[PHASE] in phases)

        return np.array(mask, dtype=np.bool)

    def unit_mask(self, *units):
        """
        Returns a unit mask for all specified units (temporary method).

        Parameters
        ----------
        units : str
            A list of units, e.g. 'VPHM', 'IPHA', etc. To create the unit
            mask for. Is converted into a set.
        """
        units = frozenset(units)
        mask = [
            stream.tags()[UNIT] in units
            for stream in self
        ]
        return np.array(mask, dtype=np.bool)

    def metadata(self):
        """
        Returns an ordered list of dictionaries that contain the tags,
        annotaions, and property version of each stream.
        """
        for s in self:
            meta = {"tags": s.tags()}
            meta["annotations"], meta["property_version"] = s.annotations()
            yield meta

    def __iter__(self):
        """
        Loops through all of the streams in the conduit
        """
        for stream in self._streams:
            yield stream

    def __len__(self):
        """
        Returns the number of streams in the conduit.
        """
        return sum(1 for _ in self)

    def __getitem__(self, idx):
        """
        Returns a stream by positional index, by UUID or a subset of
        streams if a mask is supplied as the index.
        """
        if isinstance(idx, (int, str, uuid.UUID)):
            return self._streams[idx]
        return self.subset(mask=idx)
