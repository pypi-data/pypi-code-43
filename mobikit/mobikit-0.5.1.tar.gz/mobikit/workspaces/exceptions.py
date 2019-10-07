#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from mobikit.exceptions import MobikitException


class FeedTypeException(MobikitException):
    """raised when trying to query a non-queryable source type"""


class PayloadException(MobikitException):
    """used to raise exception for invalid query payload"""


class SourceError(MobikitException):
    """used to raise exceptions for missing and/or type-mismatched feed sources"""


class FeedError(MobikitException):
    """used to raise exceptions when loading sources for a feed"""


class InvalidFilter(MobikitException):
    """raised when an arg for Filter is of an invalid type"""


class MalformedFilter(MobikitException):
    """raised when an atomic filter is improperly formatted"""


class InvalidColumn(MobikitException):
    """raised when a column is constructed with invalid args"""


class InvalidComparand(MobikitException):
    """raised when a comparand provided to a filter constructing function is invalid"""


class InvalidLowerBound(MobikitException):
    """raised when an lower bound provided to a filter constructing function is invalid"""


class InvalidUpperBound(MobikitException):
    """raised when an upper bound provided to a filter constructing function is invalid"""


class InvalidCoordinate(MobikitException):
    """raised when the coordinate provided to a filter constructing function is invalid"""


class MalformedCoordinate(MobikitException):
    """raised when either the latitude or longitude portion of a coordinate are malformed"""


class InvalidLongitude(MobikitException):
    """raised when a longitude provided to a filter constructing function is invalid"""


class InvalidLatitude(MobikitException):
    """raised when a latitude provided to a filter constructing function is invalid"""


class InvalidRadius(MobikitException):
    """raised when a radius provided to a filter constructing function is invalid"""


class MalformedAggregator(MobikitException):
    """raised when an aggregator provides malformed data"""


class MalformedSelector(MobikitException):
    """raised when an selector provides malformed data"""


class InvalidGeometry(MobikitException):
    """raised when a provided gerometry is improperly formatted"""


class DBSourceError(MobikitException):
    """raised when an error is encountered when loading/querying a db source"""


class FileSourceError(MobikitException):
    """raised when an error is encountered when loading/querying a file source"""
