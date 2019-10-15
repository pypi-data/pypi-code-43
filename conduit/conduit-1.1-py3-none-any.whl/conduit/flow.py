# conduit.flow
# Implements a DAG API for BTrDB-specific data flow style computation.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Mon Oct 14 18:06:02 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: flow.py [] benjamin@bengfort.com $

"""
Implements a DAG API for BTrDB-specific data flow style computation.
"""

##########################################################################
## Imports
##########################################################################

import pandas as pd

from functools import partial
from conduit.exceptions import GraphError
from conduit.meta import accumulate, TagsGroup, AnnotationsGroup

try:
    import networkx as nx
except ImportError:
    nx = None


##########################################################################
## Data Flow Nodes
##########################################################################

class Node(object):
    """
    A node represents a unit of computation or collection inside of a data flow graph.

    The data flow graph is composed of nodes whose edges are directed from its parents
    and to its children. Data is aggregated from the parents through the graph to the
    node by calls initiated by the children. E.g. a call to Node.values will call all
    of the node's parent.values functions, then return some transformed data.

    Nodes implement both computation and construction methods. Computation methods are
    used to exercise the graph from all the parents of the originating node.
    Construction methods add children to the node and extend the data flow graph.

    Parameters
    ----------
    parents : Node, list of Nodes, None
        Create a node by specifying its parents - note that this can only be done once.
        The parents can be either a single parent node, a list or a tuple of nodes, or
        None if this is the root node.

    Attributes
    ----------
    children : set of Nodes
        References to
    """

    def __init__(self, parents):
        self.parents = parents
        self._children = set([])

    ## ////////////////////////////////////////////////////////////////////
    ## Graph Methods
    ## ////////////////////////////////////////////////////////////////////

    @property
    def parents(self):
        try:
            return self._parents
        except AttributeError as e:
            # Not totally sure how this would happen
            raise GraphError("the graph is disconnected at this node") from e

    @parents.setter
    def parents(self, parents):
        if hasattr(self, "_parents"):
            raise GraphError("node parents cannot be modified once created")

        if isinstance(parents, (list, tuple)):
            if len(parents) == 1:
                # Helper to ensure single parents are not lists or tuples
                # this prevents concat errors and other issues
                parents = parents[0]

            else:
                # Ensure parents is an immutable type
                parents = tuple(parents)

        if parents is not None and not parents:
            raise GraphError(
                "no parents have been specified, specify None for root node"
            )

        # TODO: should we do more type checking here or just rely on duck typing?
        # Note: we expect self._parents is None to be valid -- for the root node.
        self._parents = parents

        # If the parents have been validated, make sure that each parent has this
        # node added as a child. Sort of weird to put it in the parents call, but it
        # is a bit simpler than having add children methods or requiring the graph
        # construction methods to do this.
        if self.multi_parent():
            for parent in self._parents:
                parent._children.add(self)

        elif not self.is_root():
            self._parents._children.add(self)

    @property
    def children(self):
        # Read-only property children
        return self._children

    def is_root(self):
        """
        Returns True if self.parents is None
        """
        return self.parents is None

    def multi_parent(self):
        """
        Returns True if there are multiple parents
        """
        return isinstance(self.parents, tuple)

    def to_networkx(self):
        """
        TODO: Add docstring
        """
        if nx is None:
            raise ImportError("networkx is required for this method")

        roots = self._find_roots()
        edges = []
        for root in roots:
            edges += root._out_edges()
        return nx.DiGraph(edges)

    def _find_roots(self):
        """
        Find all root nodes that source this node.
        """
        if self.is_root():
            return set([self])

        if self.multi_parent():
            roots = set([])
            for parent in self.parents:
                roots |= parent._find_roots()
            return roots

        return self.parents._find_roots()

    def _out_edges(self):
        """
        Return all of the edges to all children and descendants, usually called from
        the root nodes of the data flow graph.
        """
        # TODO: should edges be a set like find roots?
        edges = []
        for child in self.children:
            edges.append((self, child))
            edges += child._out_edges()
        return edges

    ## ////////////////////////////////////////////////////////////////////
    ## Computational Methods
    ## ////////////////////////////////////////////////////////////////////

    def tags(self):
        """
        Returns the tags associated with the output data flow. If the output data is
        a single Series, then a single Tags object is returned. If the output data is
        a DataFrame then a TagsGroup is returned with the tags for each column in the
        DataFrame.

        Returns
        -------
        tags : Tags or TagsGroup
            The tag metadata associated with the Series or DataFrame columns.

        Notes
        -----
        Subclasses may use super() with this method to accumulate the tags from parents
        as follows: if a single parent, return the parent's tags or tags group. If
        multi-parent, aggregate the tags into a tags group in the expected order of the
        columns of the concatenated DataFrames and Series objects.
        """
        if self.is_root():
            # Subclasses that can be root nodes must specify how to get tags
            raise GraphError(
                "{} is not a supported root node type".format(self.__class__.__name__)
            )

        if not self.multi_parent():
            return self.parents.tags()

        # Accumulate the tags from the parents
        return accumulate([parent.tags() for parent in self.parents])

    def annotations(self):
        """
        Returns the annotations associated with the output data flow. If the output data
        is a single Series, then a single Annotations object is returned. If the output
        data is a DataFrame then an AnnotationsGroup is returned with the annotations
        for each column in the DataFrame.

        Returns
        -------
        annotations : Annotations or AnnotationsGroup
            The annotations metadata associated with the Series or DataFrame columns.

        Notes
        -----
        Subclasses may use super() with this method to accumulate the annotations from
        parents as follows: if a single parent, return the parent's annotations or
        annotations group. If multi-parent, aggregate the annotations into an
        annotations group in the expected order of the columns of the concatenated
        DataFrames and Series objects.
        """
        if self.is_root():
            # Subclasses that can be root nodes must specify how to get annotations
            raise GraphError(
                "{} is not a supported root node type".format(self.__class__.__name__)
            )

        if not self.multi_parent():
            return self.parents.annotations()

        # Accumulate the annotations from the parents
        # Accumulate the tags from the parents
        return accumulate([parent.annotations() for parent in self.parents])

    def values(self, start, end, datetime64_index=True):
        """
        Read raw values from BTrDB between time [start, end) then apply all data flow
        transformations to those values and return materialized pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.

        Notes
        -----
        Subclasses may use super() with this method to accumulate the data from
        parents as follows: if a single parent, return the parent's data. If
        multi-parent, concatenate all parent's data into a single DataFrame.
        """
        return self._execute_data_query(
            "values", start, end, datetime64_index=datetime64_index,
        )

    def windows(self, start, end, width, depth=0, agg="mean", datetime64_index=True):
        """
        Read arbitrarily-sized windows of data from BTrDB, then apply all data flow
        transformations to the selected aggregate values type and return materialized
        pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        width : int
            The number of nanoseconds in each window, subject to the depth parameter.

        depth : int, default: 0
            The precision of the window duration as a power of 2 in nanoseconds.
            E.g 30 would make the window duration accurate to roughly 1 second

        agg : str, default: "mean"
            The aggregate to select from the StatPoint. One of min, mean, max,
            count, or stddev.

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.

        Notes
        -----
        Subclasses may use super() with this method to accumulate the data from
        parents as follows: if a single parent, return the parent's data. If
        multi-parent, concatenate all parent's data into a single DataFrame.
        """
        return self._execute_data_query(
            "windows",
            start,
            end,
            width,
            depth=depth,
            agg=agg,
            datetime64_index=datetime64_index,
        )

    def aligned_windows(self, start, end, pointwidth, agg="mean", datetime64_index=True):
        """
        Read statistical aggregates of aligned windows of data from BTrDB by directly
        reading the Berkeley Tree, then apply all data flow transformations to the
        selected aggregate values type and return materialized pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        pointwidth : int
            Specify the number of ns between data points (2**pointwidth)

        agg : str, default: "mean"
            The aggregate to select from the StatPoint. One of min, mean, max,
            count, or stddev.

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.

        Notes
        -----
        Subclasses may use super() with this method to accumulate the data from
        parents as follows: if a single parent, return the parent's data. If
        multi-parent, concatenate all parent's data into a single DataFrame.
        """
        return self._execute_data_query(
            "aligned_windows",
            start,
            end,
            pointwidth,
            agg=agg,
            datetime64_index=datetime64_index,
        )

    def _execute_data_query(self, method, *args, **kwargs):
        """
        Unifies the behavior of data queries values, windows, and aligned_windows
        """
        if self.is_root():
            # Subclasses that can be root nodes must specify how to execute data queries
            raise GraphError(
                "{} is not a supported root node type".format(self.__class__.__name__)
            )

        # execute action closure
        def execute(parent):
            try:
                action = getattr(parent, method)
                return action(*args, **kwargs)
            except Exception as e:
                # Catches AttributeError and other database errors
                raise GraphError(
                    "could not execute {} query on {}".format(method, repr(parent))
                ) from e


        if not self.multi_parent():
            return execute(self.parents)

        try:
            # Concatenate parent series and data frames into a DataFrame
            return pd.concat([execute(parent) for parent in self.parents], axis=1)
        except GraphError:
            # If the error occurred in the execute closure continue raise
            raise
        except Exception as e:
            # If the error occurred during pd.concat - create graph error
            raise GraphError(
                "could not concatenate parents {} query".format(method)
            ) from e

    ## ////////////////////////////////////////////////////////////////////
    ## Construction Methods
    ## ////////////////////////////////////////////////////////////////////

    def collect(self, *nodes):
        """
        Collect all of the nodes along with the current node into a single node.

        Parameters
        ----------
        nodes : list of Nodes
            The nodes to collect along with the current node into a new data flow node.

        Returns
        -------
        node : Node
            A node whose parents include the current node and the specified nodes.
        """
        # Do not make a new node if no nodes are supplied.
        if len(nodes) == 0:
            return self

        parents = [self] + list(nodes)
        return Node(parents)

    def apply(self, func, **kwargs):
        """
        Create a new node in the data flow that applies a transformer or composition
        function to the incoming parent's data, tags, and annotations.

        Parameters
        ----------
        func : transformer or composition
            A function that must have the signature `func(data, tags, annotations)`.

        kwargs : dict
            Any additional keyword arguments to supply to the function.

        Returns
        -------
        node : FunctionNode
            A new data flow node whose parents are the current node.
        """
        return FunctionNode(self, func, apply_many=False, **kwargs)

    def each(self, func, **kwargs):
        """
        Create a new node in the data flow that applies a transformer or composition
        function to each of the columns, tags, and annotations in the parent's
        DataFrame, TagGroup, and AnnotationGroup.

        Parameters
        ----------
        func : transformer or composition
            A function that must have the signature `func(data, tags, annotations)`.

        kwargs : dict
            Any additional keyword arguments to supply to the function.

        Returns
        -------
        node : FunctionNode
            A new data flow node whose parents are the current node.
        """
        return FunctionNode(self, func, apply_many=True, **kwargs)


##########################################################################
## Transformer Nodes
##########################################################################

class TransformerNode(Node):
    """
    A transformer node is a simple data flow node that applies a transformation
    function to all data queries, e.g. `values()`, `windows()`, and `aligned_windows()`.
    This class is primarily subclassed by transformation-specific utilities so that
    they only have to implement a single `transform()` method along with trnasformer
    specific `tags()` and `annotations()` methods.

    Parameters
    ----------
    parents : Node or list of Nodes
        The parents to get data from to apply the transformer.
    """

    def __init__(self, parents):
        super(TransformerNode, self).__init_(parents)

    def transform(self, data):
        """
        Transform the data fetched from a data query and return it.

        Parameters
        ----------
        data : pd.Series or pd.DataFrame
            The materialized time series data from BTrDB.

        Returns
        -------
        data : pd.Series or pd.DataFrame
            The transformed time series data.
        """
        raise NotImplementedError(
            "{} does not implement a transform method".format(self.__class__.__name__)
        )

    def values(self, start, end, datetime64_index=True):
        """
        Read raw values from BTrDB between time [start, end) then apply all data flow
        transformations to those values and return materialized pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.
        """
        data = super(TransformerNode, self).values(
            start, end, datetime64_index=datetime64_index
        )
        return self.transform(data)

    def windows(self, start, end, width, depth=0, agg="mean", datetime64_index=True):
        """
        Read arbitrarily-sized windows of data from BTrDB, then apply all data flow
        transformations to the selected aggregate values type and return materialized
        pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        width : int
            The number of nanoseconds in each window, subject to the depth parameter.

        depth : int, default: 0
            The precision of the window duration as a power of 2 in nanoseconds.
            E.g 30 would make the window duration accurate to roughly 1 second

        agg : str, default: "mean"
            The aggregate to select from the StatPoint. One of min, mean, max,
            count, or stddev.

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.
        """
        data = super(TransformerNode, self).windows(
            start,
            end,
            width,
            depth=depth,
            agg=agg,
            datetime64_index=datetime64_index,
        )
        return self.transform(data)

    def aligned_windows(self, start, end, pointwidth, agg="mean", datetime64_index=True):
        """
        Read statistical aggregates of aligned windows of data from BTrDB by directly
        reading the Berkeley Tree, then apply all data flow transformations to the
        selected aggregate values type and return materialized pandas timeseries data.

        Parameters
        ----------
        start : int or datetime like object
            The start time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        end : int or datetime like object
            The end time in nanoseconds for the range to be queried. (see
            :func:`btrdb.utils.timez.to_nanoseconds` for valid input types)

        pointwidth : int
            Specify the number of ns between data points (2**pointwidth)

        agg : str, default: "mean"
            The aggregate to select from the StatPoint. One of min, mean, max,
            count, or stddev.

        datetime64_index : bool, default: True
            If True, parse the nanosecond epoch time values from the database into
            np.datetime64 types, creating a DatetimeIndex for the return data.

        Returns
        ------
        data : pd.Series or pd.DataFrame
            Returns the pandas timeseries data structure either as a univariate array
            (pd.Series) or a multivariate array (pd.DataFrame) depending on the data
            flow computation.
        """
        data = super(TransformerNode, self).aligned_windows(
            start,
            end,
            pointwidth,
            agg=agg,
            datetime64_index=datetime64_index,
        )
        return self.transform(data)


##########################################################################
## Function Node
##########################################################################

class FunctionNode(TransformerNode):
    """
    Function nodes are simple data flow nodes that apply a transformer or a
    composition function to the data of the parent node. Because the function
    only operates on data queries, tags and annotations are not available until
    the function has been called with `values()`, `windows()`, or `aligned_windows()`.
    The tags and annotations for the previous call can then be fetched.

    # TODO: the previous tags thing really won't work unless this is the last
    # TODO: node in the data flow graph. Need to rethink this strategy, e.g.
    # TODO: by allowing transformer and composition functions to accept None data.

    Parameters
    ----------
    parents : Node or list of Nodes
        The parents to get data from to apply the transformer.

    func : transformer or composition
        A function that must have the signature `func(data, tags, annotations)`.

    apply_many : bool, default: False
        If true, applies the function to each column in the data frame, otherwise
        applies the function to the entire data frame.

    kwargs : dict
        Additional keyword arguments to supply to the function
    """

    def __init__(self, parents, func, apply_many=False, **kwargs):
        super(FunctionNode, self).__init__(parents)
        self.func = func
        self.apply_many = apply_many
        self.kwargs = kwargs

        self._tags = None
        self._annotations = None
        self._calls = 0

    @property
    def calls(self):
        return self._calls

    def tags(self):
        """
        Returns the tags associated with the the previous data query.

        Returns
        -------
        tags : Tags or TagsGroup
            The tag metadata associated with the Series or DataFrame columns.
        """
        if self.is_root():
            # Subclasses that can be root nodes must specify how to get tags
            raise GraphError(
                "{} is not a supported root node type".format(self.__class__.__name__)
            )

        # TODO: need to be able to call the function without data to get tags
        if self._tags is None:
            raise GraphError(
                "no tags available, a data query must be made first"
            )
        return self._tags

    def annotations(self):
        """
        Returns the annotations associated with the previous data query.

        Returns
        -------
        annotations : Annotations or AnnotationsGroup
            The annotations metadata associated with the Series or DataFrame columns.
        """
        if self.is_root():
            # Subclasses that can be root nodes must specify how to get annotations
            raise GraphError(
                "{} is not a supported root node type".format(self.__class__.__name__)
            )

        # TODO: need to be able to call the function without data to get annotations
        if self._annotations is None:
            raise GraphError(
                "No annotations available, a data query must be made first"
            )
        return self._annotations

    def transform(self, data):
        tags = super(FunctionNode, self).tags()
        annotations = super(FunctionNode, self).annotations()
        action = partial(self.func, **self.kwargs)

        if self.apply_many and isinstance(data, pd.DataFrame):
            datap, tagsp, annotationsp = [], [], []
            for idx, column in enumerate(data.columns):
                dp, tp, ap = action(data[column], tags[idx], annotations[idx])
                datap.append(dp)
                tagsp.append(tp)
                annotationsp.append(ap)

            data = pd.concat(datap, axis=1)
            self._tags = TagsGroup(tagsp)
            self._annotations = AnnotationsGroup(annotationsp)

        else:
            data, self._tags, self._annotations = action(data, tags, annotations)

        self._calls += 1
        return data

    def __str__(self):
        return self.func.__name__

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.func.__name__)
