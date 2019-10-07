#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from abc import ABC, abstractmethod
from mobikit_utils.utils import raise_for_keys, raise_for_values, raise_for_types
from mobikit_utils.query_builder.constants import (
    filter_types,
    payload_schema,
    sort_dirs,
    aggregation_types,
)
from mobikit.workspaces.exceptions import (
    InvalidFilter,
    MalformedFilter,
    InvalidColumn,
    InvalidComparand,
    InvalidLowerBound,
    InvalidUpperBound,
    InvalidCoordinate,
    MalformedCoordinate,
    InvalidLongitude,
    InvalidLatitude,
    InvalidRadius,
    MalformedAggregator,
    MalformedSelector,
    InvalidGeometry,
)


class Query:
    """
    Top-level class for constructing query API paylaods.

    Parameters
    ----------
    select : list
        List of columns to return. List members may be instances of either Column or Aggregator.
    sample : float
        A sample percentage expressed as a value between 0.0 and 1.0.
    filterby : Filter or AtomicFilter
        The filter(s) that will be applied to the query.
    groupby : list
        List of columns to group by. List members must be instances of Column.
    sortby: list
        List of columns to sort by. List members must be instances of SortDirection.
    limit : int
        Maximum number of rows to return.
    """

    schema = payload_schema

    def __init__(
        self,
        select=None,
        filterby=None,
        groupby=None,
        sortby=None,
        limit=None,
        sample=None,
    ):
        select = select or []
        filterby = filterby or Filter()
        groupby = groupby or []
        sortby = sortby or []
        self._select = Select(*select)
        self._sample = Sample(sample) if sample is not None else sample
        self._filter = filterby
        self._group = Group(*groupby)
        self._sort = Sort(*sortby)
        self._limit = Limit(limit) if limit is not None else limit

    def to_dict(self):
        data = {
            self.schema.select.name: self._select,
            self.schema.filter.name: self._filter.to_dict(),
            self.schema.group.name: self._group,
            self.schema.sort.name: self._sort,
            self.schema.meta.name: {self.schema.meta.spatial_format: "text"},
        }
        if self._sample is not None:
            data[self.schema.sample.name] = self._sample.val
        if self._limit is not None:
            data[self.schema.limit.name] = self._limit.val
        return data


class Sample:
    """
    validates and constructs a well-formed sample portion of the query payload
    'val' property returns the serializable value
    """

    @classmethod
    def validate(cls, sample):
        tmp_key = "sample"
        raise_for_types(
            {tmp_key: sample},
            tmp_key,
            allowed_types=[float],
            ExceptionClass=InvalidColumn,
        )
        if (sample < 0) or (sample > 1):
            raise InvalidColumn(
                f"Sample must be a value between 0.0 and 1.0. got {sample}."
            )
        return sample

    @property
    def val(self):
        return self._val

    def __init__(self, sample):
        self._val = self.validate(sample)


class Limit:
    """
    validates and constructs a well-formed limit portion of the query payload
    'val' property returns the serializable value
    """

    @classmethod
    def validate(cls, limit):
        tmp_key = "limit"
        raise_for_types(
            {tmp_key: limit}, tmp_key, allowed_types=[int], ExceptionClass=InvalidColumn
        )
        return limit

    @property
    def val(self):
        return self._val

    def __init__(self, limit):
        self._val = self.validate(limit)


class Select(list):
    """
    validates and constructs a well-formed select portion of the query payload
    """

    @classmethod
    def validate(cls, selections):
        tmp_key = "select_element"
        for selection in selections:
            raise_for_types(
                {tmp_key: selection},
                tmp_key,
                allowed_types=[Column, Selector],
                ExceptionClass=InvalidColumn,
            )
        return selections

    def __init__(self, *selections):
        selections = self.validate(selections)
        super().__init__(selections)


class Group(list):
    """
    validates and constructs a well-formed group portion of the query payload
    """

    @classmethod
    def validate(cls, groupings):
        tmp_key = "groupby_element"
        for grouping in groupings:
            raise_for_types(
                {tmp_key: grouping},
                tmp_key,
                allowed_types=[Column],
                ExceptionClass=InvalidColumn,
            )
        return groupings

    def __init__(self, *groupings):
        groupings = self.validate(groupings)
        super().__init__(groupings)


class Sort(list):
    """
    validates and constructs a well-formed sort portion of the query payload
    """

    @classmethod
    def validate(cls, sorts):
        tmp_key = "sort_element"
        for sort in sorts:
            raise_for_types(
                {tmp_key: sort},
                tmp_key,
                allowed_types=[SortDirection],
                ExceptionClass=InvalidColumn,
            )
        return sorts

    def __init__(self, *sorts):
        sorts = self.validate(sorts)
        super().__init__(sorts)


class Filter(dict):
    """
    Validates and constructs a well-formed filter portion of the query payload.

    Parameters
    ----------
    *args Filter or AtomicFilter
        Any number of predicate Filters from which to compose this Filter. 
        Predicate filters must be instances of Filter or AtomicFilter.
    conjunction : {'and', 'or'}
        The logical conjunction that will be used to join `args`.    
    """

    schema = payload_schema.filter_block

    def __init__(self, *args, conjunction="and"):
        for arg in args:
            if not isinstance(arg, Filter) and not isinstance(arg, AtomicFilter):
                raise InvalidFilter(
                    f"Filter args must be of type Filter or AtomicFilter. Got {type(arg)} instead."
                )
        self._predicates = list(args)
        self._conjunction = conjunction

    def to_dict(self):
        return {
            self.schema.conjunction: self._conjunction,
            self.schema.predicates: [
                predicate.to_dict() for predicate in self._predicates
            ],
        }

    def __bool__(self):
        return True


class AtomicFilter(dict):
    """
    automatically generated from Column functions. no need to construct explicitly
    """

    schema = payload_schema.filter

    @classmethod
    def validate(self, data):
        data = raise_for_keys(
            data,
            [self.schema.field, self.schema.type, self.schema.meta],
            ExceptionClass=MalformedFilter,
        )
        data[self.schema.negated] = data.get(self.schema.negated, False)
        tmp_key = "negated"
        raise_for_types(
            {tmp_key: data[self.schema.negated]},
            tmp_key,
            allowed_types=[bool],
            ExceptionClass=MalformedFilter,
        )
        return data

    def negate(self):
        self[self.schema.negated] = (
            not self[self.schema.negated] if self[self.schema.negated] else True
        )

    def to_dict(self):
        return self

    def __bool__(self):
        return True

    def __neg__(self):
        self.negate()
        return self

    def __init__(self, data):
        data = self.validate(data)
        super().__init__(**data)


class Selectable(ABC):
    schema = payload_schema.select

    @abstractmethod
    def alias(self, name):
        """
        Creates an alias for the Column or Selector.

        Parameters
        ----------
        name : str
            Name to be used as the alias

        Returns
        ----------
        Selector
            Aliased Selector.
        """
        pass

    @abstractmethod
    def _set_format(self, val):
        """private method for spatial formatting operations"""
        pass

    def as_geojson(self):
        """
        Formats the spatial Column or Selector as GeoJSON.

        Returns
        ----------
        Selector
            Formatted Selector.
        """
        return self._set_format("geojson")

    def as_lat(self):
        """
        Formats the spatial Column or Selector as a numeric latitude.

        Returns
        ----------
        Selector
            Formatted Selector.
        """
        return self._set_format("lat")

    def as_lng(self):
        """
        Formats the spatial Column or Selector as a numeric longitude.

        Returns
        ----------
        Selector
            Formatted Selector.
        """
        return self._set_format("lng")

    def as_text(self):
        """
        Formats the spatial Column or Selector as well-known text.

        Returns
        ----------
        Selector
            Formatted Selector.
        """
        return self._set_format("text")


class Selector(dict, Selectable):
    """
    represents a validated and well-formed selector dict for a query payload
    automatically generated from Column functions. no need to construct explicitly
    """

    schema = payload_schema.select

    @classmethod
    def validate(cls, data):
        data = raise_for_keys(
            data, [cls.schema.field], ExceptionClass=MalformedSelector
        )
        return data

    def __init__(self, data):
        data = self.validate(data)
        super().__init__(**data)

    def alias(self, val):
        self[self.schema.alias] = val
        return self

    def _set_format(self, val):
        self[self.schema.format] = val
        return self


class Aggregator(Selector):
    """
    represents a validated and well-formed aggregator dict for a query payload
    automatically generated from Column functions. no need to construct explicitly
    """

    schema = payload_schema.select

    @classmethod
    def validate(self, data):
        data = raise_for_keys(
            data, [self.schema.function], ExceptionClass=MalformedAggregator
        )
        return data

    def __init__(self, data):
        data = self.validate(data)
        super().__init__(data)


class SortDirection(dict):
    """
    represents a validated and well-formed sort-direction dict for a query payload
    automatically generated from Column functions. no need to construct explicitly
    """

    schema = payload_schema.sort

    @classmethod
    def validate(self, data):
        data = raise_for_keys(data, [self.schema.field, self.schema.dir])
        return data

    def __init__(self, data):
        data = self.validate(data)
        super().__init__(**data)


class Column(str, Selectable):
    """
    A column identifier.

    Contains functions to construct atomic filters, aggregators, sort directions

    Parameters
    ----------
    identifier : str
        Name of the desired column.
    """

    schema = payload_schema.filter

    def __init__(self, identifier):
        self._identifier = self.validate(identifier)

    def as_geojson(self):
        return super().as_geojson()

    def as_lat(self):
        return super().as_lat()

    def as_lng(self):
        return super().as_lng()

    def as_text(self):
        return super().as_text()

    def alias(self, val):
        return Selector(
            {
                payload_schema.select.field: self._identifier,
                payload_schema.select.alias: val,
            }
        )

    def _set_format(self, val):
        return Selector(
            {
                payload_schema.select.field: self._identifier,
                payload_schema.select.format: val,
            }
        )

    def ascending(self):
        """
        Creates an ascending sort direction for the Column.

        Returns
        ----------
        SortDirection
            Created ascending sort direction.
        """
        return self._compose_sort_direction(sort_dirs.ascending)

    def descending(self):
        """
        Creates a descending sort direction for the Column.

        Returns
        ----------
        SortDirection
            Created descending sort direction.
        """
        return self._compose_sort_direction(sort_dirs.descending)

    def stddev(self):
        """
        Creates a stddev aggregator for the column.

        Returns
        ----------
        Aggregator
            Created stddev aggregator.
        """
        return self._compose_aggregator(aggregation_types.stddev)

    def median(self):
        """
        Creates a median aggregator for the column.

        Returns
        ----------
        Aggregator
            Created median aggregator.
        """
        return self._compose_aggregator(aggregation_types.median)

    def min(self, distinct=False):
        """
        Creates a min aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created min aggregator.
        """
        return self._compose_aggregator(aggregation_types.min, distinct=distinct)

    def max(self, distinct=False):
        """
        Creates a max aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created max aggregator.
        """
        return self._compose_aggregator(aggregation_types.max, distinct=distinct)

    def first(self, distinct=False):
        """
        Creates a first aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created first aggregator.
        """
        return self._compose_aggregator(aggregation_types.first, distinct=distinct)

    def last(self, distinct=False):
        """
        Creates a last aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created last aggregator.
        """
        return self._compose_aggregator(aggregation_types.last, distinct=distinct)

    def count(self, distinct=False):
        """
        Creates a count aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created count aggregator.
        """
        return self._compose_aggregator(aggregation_types.count, distinct=distinct)

    def sum(self, distinct=False):
        """
        Creates a sum aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created sum aggregator.
        """
        return self._compose_aggregator(aggregation_types.sum, distinct=distinct)

    def average(self, distinct=False):
        """
        Creates an average aggregator for the column.
        
        Parameters
        ----------
        distinct : bool
            If true, will only consider unique values in the aggregation.

        Returns
        -------
        Aggregator
            Created average aggregator.
        """
        return self._compose_aggregator(aggregation_types.average, distinct=distinct)

    def equals(self, comparand, negated=False):
        """
        Creates an equals AtomicFilter.
        
        Parameters
        ----------
        comparand : Column or str or int or float or ISO-8601 datestring
            The value to which the column will be compared.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created equals AtomicFilter.
        """
        return self._compose_ineqality_filter(
            filter_types.equal, comparand, negated=negated
        )

    def greater_than(self, comparand, negated=False):
        """
        Creates a greater than AtomicFilter.
        
        Parameters
        ----------
        comparand : Column or str or int or float or ISO-8601 datestring
            The value to which the column will be compared.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created greater than AtomicFilter.
        """
        return self._compose_ineqality_filter(
            filter_types.greater_than, comparand, negated=negated
        )

    def less_than(self, comparand, negated=False):
        """
        Creates a less than AtomicFilter.
        
        Parameters
        ----------
        comparand : Column or str or int or float or ISO-8601 datestring
            The value to which the column will be compared.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created less than AtomicFilter.
        """
        return self._compose_ineqality_filter(
            filter_types.less_than, comparand, negated=negated
        )

    def greater_than_equal(self, comparand, negated=False):
        """
        Creates a greater than or equal to AtomicFilter.
        
        Parameters
        ----------
        comparand : Column or str or int or float or ISO-8601 datestring
            The value to which the column will be compared.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created greater than or equal to AtomicFilter.
        """
        return self._compose_ineqality_filter(
            filter_types.greater_than_equal, comparand, negated=negated
        )

    def less_than_equal(self, comparand, negated=False):
        """
        Creates a less than or equal to AtomicFilter.
        
        Parameters
        ----------
        comparand : Column or str or int or float or ISO-8601 datestring
            The value to which the column will be compared.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created less than or equal to AtomicFilter.
        """
        return self._compose_ineqality_filter(
            filter_types.less_than_equal, comparand, negated=negated
        )

    def isin(self, *comparand, negated=False):
        """
        Creates an 'in' AtomicFilter.
        
        Parameters
        ----------
        *comparand : Column or str or int or float or ISO-8601 datestring
            Any number of comparands that will form the set used to filter results.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created 'in' AtomicFilter.
        """
        comparand = list(comparand)
        for val in comparand:
            tmp_key = "comparand_element"
            raise_for_types(
                {tmp_key: val},
                tmp_key,
                allowed_types=[str, int, float],
                ExceptionClass=InvalidComparand,
            )
        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_types.is_in,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.in_meta.comparand: self._to_argument(comparand)
            },
        }
        return AtomicFilter(data)

    def like(self, comparand, negated=False):
        """
        Creates an like AtomicFilter.
        
        Parameters
        ----------
        comparand : str
            A patten string, to be used with a SQL 'LIKE' operator.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created like AtomicFilter.
        """
        tmp_key = "comparand"
        raise_for_types(
            {tmp_key: comparand},
            tmp_key,
            allowed_types=[str],
            ExceptionClass=InvalidComparand,
        )
        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_types.like,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.like_meta.comparand: self._to_argument(comparand)
            },
        }
        return AtomicFilter(data)

    def between(self, lb, ub, negated=False):
        """
        Creates a between/range AtomicFilter.
        
        Parameters
        ----------
        lb : Column or str or int or float or ISO-8601 datestring
            Value to be used as the lower bound (inclusive).
        ub : Column or str or int or float or ISO-8601 datestring
            Value to be used as the upper bound (inclusive).
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created between/range AtomicFilter.
        """
        tmp_key = ("lb", "ub")
        raise_for_types(
            {tmp_key[0]: lb},
            tmp_key[0],
            allowed_types=[Column, int, float, str],
            ExceptionClass=InvalidLowerBound,
        )
        raise_for_types(
            {tmp_key[1]: ub},
            tmp_key[1],
            allowed_types=[Column, int, float, str],
            ExceptionClass=InvalidUpperBound,
        )
        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_types.between,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.between_meta.lb: self._to_argument(lb),
                self.schema.between_meta.ub: self._to_argument(ub),
            },
        }
        return AtomicFilter(data)

    def _compose_aggregator(self, aggregation_type, distinct=False):
        schema = payload_schema.select
        data = {
            schema.field: self._identifier,
            schema.function: aggregation_type,
            schema.distinct: distinct,
        }
        return Aggregator(data)

    def _compose_sort_direction(self, sort_dir):
        schema = payload_schema.sort
        data = {schema.field: self._identifier, schema.dir: sort_dir}
        return SortDirection(data)

    def _compose_ineqality_filter(self, filter_type, comparand, negated=False):
        tmp_key = "comparand"
        raise_for_types(
            {tmp_key: comparand},
            tmp_key,
            allowed_types=[Column, str, int, float],
            ExceptionClass=InvalidComparand,
        )
        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_type,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.inequality_meta.comparand: self._to_argument(comparand)
            },
        }
        return AtomicFilter(data)

    @classmethod
    def _to_argument(self, val):
        return "${" + val + "}" if isinstance(val, Column) else val

    @classmethod
    def validate(self, identifier):
        tmp_key = "column_identifier"
        raise_for_types(
            {tmp_key: identifier},
            tmp_key,
            allowed_types=[str],
            ExceptionClass=InvalidColumn,
        )
        return identifier

    def __lt__(self, o):
        return self.less_than(o)

    def __gt__(self, o):
        return self.greater_than(o)

    def __le__(self, o):
        return self.less_than_equal(o)

    def __ge__(self, o):
        return self.greater_than_equal(o)

    def __eq__(self, o):
        return self.equals(o)

    def __ne__(self, o):
        return self.equals(o, negated=True)

    def __isin__(self, o):
        return self.isin(*o)

    def __repr__(self):
        return self._identifier


class SpatialColumn(Column):
    """
    A spatial column identifier.

    Contains additional methods to construct spatial AtomicFilters.

    Parameters
    ----------
    identifier : str
        Name of the desired column.
    """

    def within(self, point, radius, negated=False):
        """
        Creates a within AtomicFilter for a spatial column.

        Parameters
        ----------
        point : tuple of the form (lat, lng)
            Center point of the within filter. `lat` and `lng` should both be valid lat/lng floats.
        radius : int or float
            Distance in meters from the center point.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created within AtomicFilter.
        """
        lat, lng = self._validate_point(point)
        tmp_key = "radius"
        raise_for_types(
            {tmp_key: radius},
            tmp_key,
            allowed_types=[int, float],
            ExceptionClass=InvalidComparand,
        )
        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_types.within,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.within_meta.lat: lat,
                self.schema.within_meta.lng: lng,
                self.schema.within_meta.radius: radius,
            },
        }
        return AtomicFilter(data)

    def intersected_by(self, geometry, negated=False):
        """
        Creates an intersected by (point in polygon) AtomicFilter for a spatial column.

        Parameters
        ----------
        geometry : Column or list of points.
            Each point should be a tuple of the form (lat, lng). 
            `lat` and `lng` should both be valid lat/lng floats.
        negated : bool
            If true, resulting AtomicFilter will be negated.

        Returns
        -------
        AtomicFilter
            Created intersected by AtomicFilter.
        """
        tmp_key = "geometry"
        raise_for_types(
            {tmp_key: geometry},
            tmp_key,
            allowed_types=[list, SpatialColumn],
            ExceptionClass=InvalidGeometry,
        )
        if isinstance(geometry, list):
            for point in geometry:
                self._validate_point(point)
            geometry = [
                list(point) if isinstance(point, tuple) else point for point in geometry
            ]

        data = {
            self.schema.field: self._identifier,
            self.schema.type: filter_types.intersected_by,
            self.schema.negated: negated,
            self.schema.meta: {
                self.schema.intersected_by_meta.geometry: self._to_argument(geometry)
            },
        }
        return AtomicFilter(data)

    def _validate_point(self, point):
        tmp_key = "coordinate"
        raise_for_types(
            {tmp_key: point},
            tmp_key,
            allowed_types=[tuple, list],
            ExceptionClass=InvalidCoordinate,
        )
        if len(point) != 2:
            raise MalformedCoordinate(
                f"Expected a coordinate of the form (lat, lng), instead got {point}"
            )
        lat, lng = point
        tmp_key = ("lat", "lng")
        raise_for_types(
            {tmp_key[0]: lat},
            tmp_key[0],
            allowed_types=[int, float],
            ExceptionClass=InvalidComparand,
        )
        raise_for_types(
            {tmp_key[1]: lng},
            tmp_key[1],
            allowed_types=[int, float],
            ExceptionClass=InvalidComparand,
        )
        return lat, lng
