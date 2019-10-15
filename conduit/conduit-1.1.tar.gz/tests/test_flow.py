# tests.test_flow
# Test the data flow graph implementation
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Mon Oct 14 18:28:44 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_flow.py [] benjamin@bengfort.com $

"""
Test the data flow graph implementation
"""

##########################################################################
## Imports
##########################################################################

import pytest
import numpy as np
import pandas as pd

from conduit.flow import *
from conduit.meta import *
from functools import partial


##########################################################################
## Fixtures
##########################################################################

class GeneratorNode(Node):

    def __init__(self, num_streams=1):
        self.num_streams = num_streams
        super(GeneratorNode, self).__init__(None)

    def tags(self):
        if self.num_streams == 1:
            return Tags(unit="dB", name="noise")

        return TagsGroup([
            {"unit": "dB", "name": "noise-{}".format(i+1)}
            for i in range(self.num_streams)
        ])

    def annotations(self):
        if self.num_streams == 1:
            return Annotations(phase="B", label="stereo")

        return AnnotationsGroup([
            {"phase": "B", "label": "stereo-{}".format(i+1)}
            for i in range(self.num_streams)
        ])

    def _make_series(self, start, end, step, datetime64_index=True):
        times = np.arange(start, end, step)
        if datetime64_index:
            times = pd.Index(times, dtype='datetime64[ns]')
        return pd.Series(np.random.rand(len(times))*230000, index=times)

    def values(self, *args, **kwargs):
        start = 1569414600000000000
        end = 1569414615000000000
        if self.num_streams == 1:
            return self._make_series(start, end, 33333000, True)

        series = [
            self._make_series(start, end, 33333000, True)
            for _ in range(self.num_streams)
        ]
        return pd.concat(series, axis=1)

    def windows(self, *args, **kwargs):
        start = 1569414600000000000
        end = 1569414720000000000

        if self.num_streams == 1:
            return self._make_series(start, end, 5000000000, True)

        series = [
            self._make_series(start, end, 5000000000, True)
            for _ in range(self.num_streams)
        ]
        return pd.concat(series, axis=1)

    def aligned_windows(self, *args, **kwargs):
        start = 1569414600000000000
        end = 1569414720000000000

        if self.num_streams == 1:
            return self._make_series(start, end, 5000000000, True)

        series = [
            self._make_series(start, end, 5000000000, True)
            for _ in range(self.num_streams)
        ]
        return pd.concat(series, axis=1)


##########################################################################
## Data Flow Node Tests
##########################################################################

class TestNode(object):

    def test_none_parents(self):
        """
        Assert Node parents can be set to None
        """
        node = Node(None)
        assert node.parents is None
        assert node.is_root() is True

    @pytest.mark.parametrize("parents", [Node(None), [Node(None)], [None]])
    def test_single_parents(self, parents):
        """
        Assert parents can be a single object
        """
        node = Node(parents)
        assert not isinstance(node.parents, (tuple, list))
        assert node.parents is None or isinstance(node.parents, Node)

        if isinstance(parents, Node):
            assert node in parents.children
            assert node.is_root() is False

        elif isinstance(parents, list) and parents[0] is not None:
            assert node in parents[0].children
            assert node.is_root() is False

        else:
            assert node.is_root() is True


    @pytest.mark.parametrize("parents", [
        [Node(None), Node(None), Node(None)], (Node(None), Node(None), Node(None))
    ])
    def test_multiple_parents(self, parents):
        """
        Assert Node can have multiple parents
        """
        node = Node(parents)
        assert len(node.parents) == 3
        assert isinstance(node.parents, tuple)
        assert node.is_root() is False

        for parent in parents:
            assert node in parent.children

    def test_require_parents(self):
        """
        Assert parents are required to create Node
        """
        with pytest.raises(GraphError, match="no parents have been specified"):
            Node([])

    def test_no_update_parents(self):
        """
        Assert parents cannot be modified once created
        """
        node = Node(None)
        with pytest.raises(GraphError, match="node parents cannot be modified"):
            node.parents = Node(None)

    def test_concat_series_dataframe(self):
        """
        Assert that a pandas DataFrame and Series can be concatenated
        """

        df = pd.concat([
            pd.concat([
                pd.Series([1, 2, 3], name="B"),
                pd.Series([4, 5, 6], name="C")],
            axis=1),
            pd.Series([7, 8, 9], name="A")
        ], axis=1)

        assert len(df.columns) == 3

    def test_base_node_not_root(self):
        """
        Assert that the base node cannot make queries if root
        """
        start = 1569414600000000000
        end = 1569414720000000000

        node = Node(None)
        queries = [
            node.tags,
            node.annotations,
            partial(node.values, start=start, end=end),
            partial(node.windows, start=start, end=end, width=5000000),
            partial(node.aligned_windows, start=start, end=end, pointwidth=32),
        ]

        for query in queries:
            with pytest.raises(GraphError, match="not a supported root node type"):
                query()

    @pytest.mark.parametrize("parents", [
        GeneratorNode(1),
        GeneratorNode(3),
        [GeneratorNode(1), GeneratorNode(1), GeneratorNode(1)],
        [GeneratorNode(2), GeneratorNode(1)],
    ])
    def test_tags(self, parents):
        """
        Test tag accumulation from parents
        """
        node = Node(parents)
        tags = node.tags()
        assert isinstance(tags, (Tags, TagsGroup))

        if node.multi_parent():
            assert len(tags) == 3

        else:
            assert tags == parents.tags()

    @pytest.mark.parametrize("parents", [
        GeneratorNode(1),
        GeneratorNode(3),
        [GeneratorNode(1), GeneratorNode(1), GeneratorNode(1)],
        [GeneratorNode(2), GeneratorNode(1)],
    ])
    def test_annotations(self, parents):
        """
        Test annotations accumulation from parents
        """
        node = Node(parents)
        meta = node.annotations()
        assert isinstance(meta, (Annotations, AnnotationsGroup))

        if node.multi_parent():
            assert len(meta) == 3

        else:
            assert meta == parents.annotations()

    @pytest.mark.parametrize("parents", [
        GeneratorNode(1),
        GeneratorNode(3),
        [GeneratorNode(1), GeneratorNode(1), GeneratorNode(1)],
        [GeneratorNode(2), GeneratorNode(1)],
    ])
    def test_values(self, parents):
        """
        Test values accumulation from parents
        """
        # TODO: mock parents and assert called with correct arguments.
        node = Node(parents)
        values = node.values(start=1569414600000000000, end=1569414720000000000)
        assert isinstance(values, (pd.Series, pd.DataFrame))

        if node.multi_parent():
            assert len(values.columns) == 3

    @pytest.mark.parametrize("parents", [
        GeneratorNode(1),
        GeneratorNode(3),
        [GeneratorNode(1), GeneratorNode(1), GeneratorNode(1)],
        [GeneratorNode(2), GeneratorNode(1)],
    ])
    def test_windows(self, parents):
        """
        Test windows accumulation from parents
        """
        # TODO: mock parents and assert called with correct arguments.
        node = Node(parents)
        values = node.windows(
            start=1569414600000000000, end=1569414720000000000, width=5000000000
        )
        assert isinstance(values, (pd.Series, pd.DataFrame))

        if node.multi_parent():
            assert len(values.columns) == 3

    @pytest.mark.parametrize("parents", [
        GeneratorNode(1),
        GeneratorNode(3),
        [GeneratorNode(1), GeneratorNode(1), GeneratorNode(1)],
        [GeneratorNode(2), GeneratorNode(1)],
    ])
    def test_aligned_windows(self, parents):
        """
        Test aligned_windows accumulation from parents
        """
        # TODO: mock parents and assert called with correct arguments.
        node = Node(parents)
        values = node.aligned_windows(
            start=1569414600000000000, end=1569414720000000000, pointwidth=32
        )
        assert isinstance(values, (pd.Series, pd.DataFrame))

        if node.multi_parent():
            assert len(values.columns) == 3


##########################################################################
## Transformer Tests
##########################################################################

class TestTransformerNodes(object):

    def test_partial(self):
        """
        Test that functools.partial behaves as expected
        """

        def xform(data, tags, annotations, foo=42, baz=13):
            return data, tags, annotations, foo, baz

        kwargs = {"foo": "C", "baz": "D"}
        p = partial(xform, tags="A", annotations="B", **kwargs)
        assert p("Z") == ("Z", "A", "B", "C", "D")
