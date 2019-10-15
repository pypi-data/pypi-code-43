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

from conduit.flow import Node
from conduit.meta import accumulate
from conduit.stream import points_to_series
from conduit.constants import LABEL, PHASE, UNIT
from conduit.exceptions import ConduitValueError, GraphError


##########################################################################
## Conduit
##########################################################################

class Conduit(Node):
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
    streams : `~btrdb.stream.Stream`, `~btrdb.stream.StreamSet`, or `Conduit` objects
        The stream objects whose computations are managed together.

    version : int, default=0
        Snapshot all queries to the specified version. By default the Conduit
        simply queries the latest version of the streams.

    parents : Conduit, optional
        To preserve provenance in a data flow, a Conduit may have a parent which is
        also a Conduit, however the parent will not be queried for data, databases
        queries are executed from the lowest Conduit in the data flow. The most
        effective way to use this is to create a master Conduit then subset it
        completely to ensure that the master Conduit is not itself queried for data.

    Example
    -------
    >>> db = btrdb.connect()
    >>> conduit = Conduit(db.streams(uuid1, uuid2, uuid3))
    """

    # TODO: signature does not match Node signature
    def __init__(self, *streams, version=0, parents=None):
        self.version = version

        # Expand streams into a StreamSet with all specified Stream objects
        _streams = []
        for stream in streams:
            if isinstance(stream, (tuple, list, StreamSet, Conduit)):
                _streams += list(stream)
            else:
                _streams.append(stream)
        self._streams = StreamSet(_streams)

        # NOTE: Conduit parents must also be Conduit objects
        super(Conduit, self).__init__(parents)
        if self.multi_parent():
            for parent in self.parents:
                if not isinstance(parent, Conduit):
                    raise GraphError("Conduit parents must also be Conduits")
        else:
            if not isinstance(self.parents, Conduit):
                raise GraphError("Conduit parents must also be Conduits")

    def tags(self):
        """
        TODO: docstring
        """
        # NOTE: Conduit objects do not call parents tags() methods
        if len(self) == 0:
            raise ConduitValueError(
                "{} contains no streams to query".format(self.__class__.__name__)
            )


        tags = accumulate([stream.tags() for stream in self])

        if len(tags) == 1:
            return tags[0]
        return tags

    def annotations(self):
        """
        TODO: docstring
        """
        # NOTE: Conduit objects do not call parents annotations() methods
        if len(self) == 0:
            raise ConduitValueError(
                "{} contains no streams to query".format(self.__class__.__name__)
            )

        meta = accumulate([stream.annotations()[0] for stream in self])

        if len(meta) == 1:
            return meta[0]
        return meta

    def values(self, start, end, datetime64_index=True):
        """
        TODO: update docstring
        """
        # NOTE: Conduit objects do not call parents values() methods
        if len(self) == 0:
            raise ConduitValueError(
                "{} contains no streams to query".format(self.__class__.__name__)
            )

        series = []
        for stream in self:
            series.append(points_to_series(
                stream.values(start, end, version=self.version),
                datetime64_index=datetime64_index,
                name=str(stream.uuid),
            ))

        if len(series) == 1:
            return series[0]
        return pd.concat(series, axis=1)

    def windows(self, start, end, width, depth=0, agg="mean", datetime64_index=True):
        """
        TODO: update docstring
        """
        # NOTE: Conduit objects do not call parents windows() methods
        if len(self) == 0:
            raise ConduitValueError(
                "{} contains no streams to query".format(self.__class__.__name__)
            )

        series = []
        for stream in self:
            series.append(points_to_series(
                stream.windows(start, end, width, depth=depth, version=self.version),
                datetime64_index=datetime64_index,
                agg=agg,
                name=str(stream.uuid),
            ))

        if len(series) == 1:
            return series[0]
        return pd.concat(series, axis=1)

    def aligned_windows(self, start, end, pointwidth, agg="mean", datetime64_index=True):
        """
        TODO: update docstring
        """
        # NOTE: Conduit objects do not call parents aligned_windows() methods
        if len(self) == 0:
            raise ConduitValueError(
                "{} contains no streams to query".format(self.__class__.__name__)
            )

        series = []
        for stream in self:
            series.append(points_to_series(
                stream.aligned_windows(start, end, pointwidth, version=self.version),
                datetime64_index=datetime64_index,
                agg=agg,
                name=str(stream.uuid),
            ))

        if len(series) == 1:
            return series[0]
        return pd.concat(series, axis=1)

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
        return Conduit(*streams, version=self.version, parents=self)

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
