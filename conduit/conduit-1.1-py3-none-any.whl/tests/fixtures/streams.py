# tests.fixtures.streams
# Mock stream object that loads data from the parquet fixture
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Jun 25 10:56:30 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: streams.py [] benjamin@bengfort.com $

"""
Mock stream object that loads data from the parquet fixture
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import uuid
import btrdb

import pandas as pd

from btrdb.endpoint import Endpoint
from btrdb.grpcinterface.btrdb_pb2_grpc import BTrDBStub
from btrdb.grpcinterface.btrdb_pb2 import KeyOptValue, OptValue
from btrdb.grpcinterface.btrdb_pb2 import InfoResponse, ProxyInfo
from btrdb.grpcinterface.btrdb_pb2 import RawPoint, StreamDescriptor

from unittest.mock import MagicMock


FIXTURES = os.path.dirname(__file__)
METADATA = os.path.join(FIXTURES, "metadata.json")
STREAMS = os.path.join(FIXTURES, "streams.parquet")
VERSION = 1
PROPERTY_VERSION = 1


##########################################################################
## FixtureEndpoint
##########################################################################

class FixtureEndpoint(Endpoint):
    """
    The FixtureEndpoint overrides the btrdb-python grpcinterface to supply
    test data from fixtures rather than making a connection to the database.
    This object makes it easier to simulate realistic interactions with
    BTrDB and to ensure that any API changes are captured during tests.
    """

    def __init__(self, streams=STREAMS, metadata=METADATA):
        # Mock the GRPC stub
        self.stub = MagicMock(spec=BTrDBStub)

        # Load the fixtures data and cache it on init
        self._load_stream_fixture(streams)
        self._load_metadata_fixture(metadata)

        # Validate the metadata to ensure that it is correct
        self._validate_internal_dataset()

    def _load_stream_fixture(self, path):
        self._streams = pd.read_parquet(path, engine='pyarrow')

    def _load_metadata_fixture(self, path):
        with open(path, 'r') as f:
            self._metadata = json.load(f)

    def _validate_internal_dataset(self):
         # Raises a ValueError if the loaded datasets are not valid.
        if self._streams.shape[1] != len(self._metadata):
            raise ValueError("mismatch between stream data and metadata")

        # Validate the columns
        for col in self._streams.columns:
            if col not in self._metadata:
                raise ValueError("missing metadata for stream {}".format(col))

    def rawValues(self, uu, start, end, version=0):
        # Yield a tuple of (list[RawPoint], version) such that each points list
        # contains a maximum of 5000 points.
        uu = str(uu)
        if uu not in self._metadata:
            raise ValueError("[404] stream does not exist")

        if start >= end:
            raise ValueError("[413] start time >= end time")

        stream = self._streams[uu].loc[start:end]
        for i in range(0, len(stream), 5000):
            substream = stream[i:i+5000]
            points = [
                RawPoint(time=time, value=value)
                for time, value in substream.iteritems()
            ]
            yield points, VERSION

    def alignedWindows(self, uu, start, end, pointwidth, version=0):
        raise NotImplementedError("alignedWindows is not supported by fixtures endpoint")

    def windows(self, uu, start, end , width, depth, version=0):
        raise NotImplementedError("windows is not supported by fixtures endpoint")

    def streamInfo(self, uu, omitDescriptor, omitVersion):
        # Return collection, propertyVersion, tags, annotations, version
        uu = str(uu)
        if uu not in self._metadata:
            raise ValueError("[404] stream does not exist")

        meta = self._metadata[uu]
        return (
            meta['collection'],
            PROPERTY_VERSION,
            meta['tags'],
            meta['annotations'],
            VERSION
        )

    def obliterate(self, uu):
        raise NotImplementedError("obliterate is not supported by fixtures endpoint")

    def setStreamAnnotations(self, uu, expected, changes):
        raise NotImplementedError("setStreamAnnotations is not supported by fixtures endpoint")

    def setStreamTags(self, uu, expected, tags, collection):
        raise NotImplementedError("setStreamTags is not supported by fixtures endpoint")

    def create(self, uu, collection, tags, annotations):
        raise NotImplementedError("create is not supported by fixtures endpoint")

    def listCollections(self, prefix):
        # Yield a list of unique collections that start with that prefix.
        matches = {
            meta['collection']
            for meta in self._metadata.values()
            if meta['collection'].startswith(prefix)
        }

        yield list(matches)

    def lookupStreams(self, collection, isCollectionPrefix, tags, annotations):
        # yields a list of 1000 results at a time where each result is a stream descriptor
        # stream descriptors include uuid, collection, tags, annotations, and property version
        # note however that tags and annotations are a list of KeyOptValues
        matches = []
        for meta in self._metadata.values():
            # Filter by collection
            if not isCollectionPrefix:
                if meta['collection'] != collection:
                    continue
            else:
                if not meta['collection'].startswith(collection):
                    continue

            # Filter by tags
            if tags:
                try:
                    for tag, value in tags.items():
                        if tag not in meta['tags'] or meta['tags'][tag] != value:
                            raise ValueError("stream does not have matching tag")
                except:
                    continue

            # Filter by annotations
            if annotations:
                try:
                    for note, value in annotations.items():
                        if note not in meta['annotations'] or meta['annotations'][note] != value:
                            raise ValueError("stream does not have matching annotation")
                except:
                    continue

            # We're good to go -- add to matches
            matches.append(StreamDescriptor(
                uuid=uuid.UUID(meta['uuid']).bytes,
                collection=meta['collection'],
                tags = [
                    KeyOptValue(key=tag, val=OptValue(value=value))
                    for tag, value in meta['tags'].items()
                ],
                annotations = [
                    KeyOptValue(key=note, val=OptValue(value=value))
                    for note, value in meta['annotations'].items()
                ],
                propertyVersion=PROPERTY_VERSION,
            ))

        # NOTE: should be 1000 at a time, but we will never have that many
        yield matches

    def nearest(self, uu, time, version, backward):
        # Return a RawPoint and the version
        uu = str(uu)
        if uu not in self._metadata:
            raise ValueError("[404] stream does not exist")

        stream = self._streams[uu]
        index = stream.index.sort_values(ascending=not backward)

        for i, ts in enumerate(index):
            if backward:
                if time > ts:
                    break
            else:
                if time < ts:
                    break
        else:
            i+=1

        if i > 0:
            return RawPoint(time=index[i-1], value=stream.loc[index[i-1]]), VERSION
        return RawPoint(time=index[i], value=stream.loc[index[i]]), VERSION

    def changes(self, uu, fromVersion, toVersion, resolution):
        raise NotImplementedError("changes not supported by fixtures endpoint")

    def insert(self, uu, values):
        raise NotImplementedError("insert not supported by fixtures endpoint")

    def deleteRange(self, uu, start, end):
        raise NotImplementedError("deleteRange not supported by fixtures endpoint")

    def info(self):
        parts = list(map(int, btrdb.__version__.split(".")))
        return InfoResponse(
            majorVersion = parts[0],
            minorVersion=parts[1],
            build=btrdb.__version__,
            proxy=ProxyInfo(proxyEndpoints=[self.__class__.__name__]),
        )

    def faultInject(self, typ, args):
        raise NotImplementedError("faultInject not supported by fixtures endpoint")

    def flush(self, uu):
        # Does nothing
        pass

    def getMetadataUsage(self, prefix):
        raise NotImplementedError("getMetadataUsage not supported by fixtures endpoint")

    def generateCSV(self, queryType, start, end, width, depth, includeVersions, *streams):
        raise NotImplementedError("generateCSV not supported by fixtures endpoint")

    def sql_query(self, stmt, params=[]):
        raise NotImplementedError("sql_query not supported by fixtures endpoint")