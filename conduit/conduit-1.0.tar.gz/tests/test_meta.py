# tests.test_meta
# Tests the immutable metadata object
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Wed Sep 25 16:40:50 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_meta.py [] benjamin@bengfort.com $

"""
Tests the immutable metadata object
"""

##########################################################################
## Imports
##########################################################################

import pytest

from conduit.meta import *
from conduit.constants import MEASUREMENT_TYPE, VOLTAGE_MAGNITUDE


class TestMetadata(object):
    """
    Test the immutable metadata objects and helper functions
    """

    def test_get_stream_type(self):
        """
        Test the get_stream_type helper function
        """
        tags = Tags(unit="VPHM", name="test-data")
        annotations = Annotations(phase="A")

        # TODO: should we test all measurement types with parametrize?
        assert get_stream_type(tags, annotations) == VOLTAGE_MAGNITUDE
        annotations = annotations.update({MEASUREMENT_TYPE: "foo"})
        assert get_stream_type(tags, annotations) == "foo"

    def test_mapping(self):
        """
        Ensure metadata is a mapping
        """
        meta = metadata(foo=42, bar='red', pi=3.14)
        assert "pi" in meta
        assert len(meta) == 3
        assert meta.get("baz", "apple") == "apple"
        assert meta == {"foo": 42, "bar": "red", "pi": 3.14}

    def test_no_set_item(self):
        """
        Ensure items cannot be set on metadata
        """
        meta = metadata()
        with pytest.raises(TypeError, match="does not support item assignment"):
            meta["foo"] = 42

    def test_immutable(self):
        """
        Ensure construction from mutable object does not reference original
        """
        orig = {'a': 1, 'b': 2}
        meta = metadata(orig)
        assert meta == orig
        orig['c'] = 3
        assert meta != orig
        assert len(meta) == 2

    def test_immutable_clone(self):
        """
        Ensure clone is immutable even with hacking
        """
        orig = metadata([('a', 1), ('b', 2)])
        meta = orig.clone()
        assert meta == orig

        orig._meta['c'] = 3
        assert meta != orig
        assert len(orig) == 3
        assert len(meta) == 2

    def test_immutable_update(self):
        """
        Ensure that update is immutable
        """
        orig = metadata(foo=42)
        meta = orig.update(bar=21)
        assert orig != meta
        assert len(meta) == 2
        assert len(orig) == 1
        assert 'bar' in meta

    @pytest.mark.parametrize("tags, key", [
        ({"name": "test"}, "unit"),
        ({"unit": "VPHM"}, "name"),
    ])
    def test_tags_required(self, tags, key):
        """
        Ensure that tags require unit and name
        """
        msg = "not contain required key '{}'".format(key)
        with pytest.raises(ConduitTypeError, match=msg):
            Tags(tags)

    @pytest.mark.parametrize("annotations, key", [
        ({"label": "test stream"}, "phase"),
    ])
    def test_annotations_required(self, annotations, key):
        """
        Ensure that tags require unit and name
        """
        msg = "not contain required key '{}'".format(key)
        with pytest.warns(ConduitWarning, match=msg):
            Annotations(annotations)

    @pytest.mark.parametrize("meta", [
        metadata({"a": 1, "b": 2}),
        Tags({"unit": "VPHM", "name": "test stream"}),
        Annotations({"phase": "B", "label": "test stream B"}),
    ])
    def test_clone_type(self, meta):
        """
        Assert clone type matches original
        """
        assert isinstance(meta.clone(), meta.__class__)


class TestMetadataGroups(object):
    """
    Test the immutable metadata collections
    """

    def test_sequence(self):
        """
        Ensure metagroup is a sequence
        """
        target = {"name": "hadley"}
        meta = metagroup([
            {"foo": 42, "color": "red"},
            {"foo": 99, "color": "blue"},
            target,
        ])

        assert target in meta
        assert len(meta) == 3
        assert meta.count(target) == 1
        assert meta.index(target) == 2

    @pytest.mark.parametrize("meta", [
        metagroup([{"a": 1, "b": 2}, {"c": 3, "d": 4}, {"e": 5, "f": 6}, {"g": 7, "h": 8}]),
        TagsGroup([
            {"unit": "VPHM", "name": "Test Stream Ebn"},
            {"unit": "VPHA", "name": "Test Stream Ebn"},
            {"unit": "IPHM", "name": "Test Stream Ib"},
            {"unit": "IPHA", "name": "Test Stream Ib"},
        ]),
        AnnotationsGroup([
            {"phase": "B", "label": "voltage magnitude"},
            {"phase": "B", "label": "voltage angle"},
            {"phase": "B", "label": "current magnitude"},
            {"phase": "B", "label": "current angle"}
        ]),
    ])
    def test_getitem(self, meta):
        """
        Test metagroup item functionality
        """
        assert isinstance(meta[2], metadata), "could not select by index"
        assert isinstance(meta[-1], metadata), "could not select by negative index"
        assert len(meta[1:3]) == 2, "could not slice"
        assert len(meta[0,2]) == 2, "could not subset by tuple index"
        assert len(meta[[0,2]]) == 2, "could not subset by list index"
        assert isinstance(meta[1,3], type(meta)), "subset does not match type"
        assert isinstance(meta[1:], type(meta)), "slice does not match type"

    def test_construct_meta(self):
        """
        Ensure objects in metagroup are always immutable themselves
        """
        meta = metagroup([
            {"foo": 42, "color": "red"},
            {"foo": 99, "color": "blue"},
        ])
        for item in meta:
            assert isinstance(item, metadata)

    def test_no_set_item(self):
        """
        Ensure items cannot be set on metagroup
        """
        meta = metagroup([{'a': 1}])
        with pytest.raises(TypeError, match="does not support item assignment"):
            meta[0] = 42

    def test_immutable(self):
        """
        Ensure construction from mutable object does not reference original
        """
        orig = [
            {"foo": 42, "color": "red"},
            {"foo": 99, "color": "blue"},
        ]
        meta = metagroup(orig)
        assert len(meta) == len(orig)
        orig.insert(0, {"foo": 314, "color": "green"})
        assert len(meta) != len(orig)
        assert len(meta) == 2

    def test_immutable_clone(self):
        """
        Ensure metagroup clone is immutable even with hacking
        """
        orig = metagroup([[('a', 1), ('b', 2)]])
        meta = orig.clone()
        assert len(meta) == len(orig)

        orig._meta.insert(0, metadata([('c', 3)]))
        assert len(meta) != len(orig)
        assert len(orig) == 2
        assert len(meta) == 1

    def test_immutable_update(self):
        """
        Test that metagroup can update internal metadata at a specific index
        """
        orig = metagroup([
            {"foo": 42, "color": "red"},
            {"foo": 99, "color": "blue"},
        ])

        meta = orig.update(1, color="green", special="unicorn")
        assert len(orig) == len(meta)
        assert orig[0] == meta[0]
        assert orig[1] != meta[1]

        assert meta[1]["color"] == "green"
        assert "special" in meta[1]

    @pytest.mark.parametrize("meta, itype", [
        (metagroup([{"a": 1, "b": 2}]), metadata),
        (TagsGroup([{"unit": "VPHM", "name": "test stream"}]), Tags),
        (AnnotationsGroup([{"phase": "B", "label": "test stream B"}]), Annotations),
    ])
    def test_clone_type(self, meta, itype):
        """
        Assert metagroup clone type matches original
        """
        assert isinstance(meta.clone(), meta.__class__)
        for item in meta:
            assert isinstance(item, itype)

        for item in meta.clone():
            assert isinstance(item, itype)

    def test_metadata_merge(self):
        """
        Test the metadata merge functionality
        """
        meta = metagroup([
            {"phase": "A", "label": "test stream 1", "device": "uPMU1"},
            {"phase": "A", "label": "test stream 2"},
            {"phase": "A", "label": "test stream 2", "id": 23},
        ])

        merged = meta.merge(foo="bar", device="uPMU-1")
        assert isinstance(merged, metadata)

        assert "phase" in merged and merged["phase"] == "A", "did not merge identical values"
        assert "id" in merged and merged["id"] == 23, "did not keep unique value"
        assert "label" in merged and merged["label"] == set(["test stream 1", "test stream 2"]), "did not set different values"
        assert "device" in merged and merged["device"] == "uPMU-1", "did not update existing key"
        assert "foo" in merged and merged["foo"] == "bar", "did not add merge key"

        # TODO: what happens when values are types other than strings?

    @pytest.mark.xfail(reason="not implemented yet")
    def test_merged_metadata_merge(self):
        """
        Testing merging merged metadata
        """
        raise NotImplementedError("not implemented yet")

    def test_tags_merge(self):
        """
        Test the TagsGroup merge functionality
        """
        tags = TagsGroup([
            {
                "name": "TST!PMU-DCA1_732-PM15",
                "unit": "VPHM",
                "ingress": "tst_42_143"
            },
            {
                "name": "TST!PMU-DCA1_732-PA14",
                "unit": "VPHA",
                "ingress": "tst_42_143"
            }
        ])

        tags = tags.merge(name="phasor", unit="complex")
        assert isinstance(tags, Tags)
        assert "name" in tags and tags["name"] == "phasor"
        assert "unit" in tags and tags["unit"] == "complex"
        assert "ingress" in tags and tags["ingress"] == "tst_42_143"

    def test_annotations_merge(self):
        """
        Test the AnnotationsGroup merge functionality
        """
        meta = AnnotationsGroup([
            {
                "reference": "TST!PMU-DCA1_732-PM15",
                "description": "National TST 1 CH 15: Northeast 732 Ecn",
                "type": "V",
                "label": "National Northeast 732 Ecn",
                "devacronym": "TST!PMU-DCA1_732",
                "enabled": "true",
                "phase": "C",
                "acronym": "VPHM",
                "internal": "true",
                "id": "b78e8def-ddff-4732-880e-b0d2342445b5"
            },
            {
                "phase": "C",
                "acronym": "VPHA",
                "internal": "true",
                "devacronym": "TST!PMU-DCA1_732",
                "label": "National Northeast 732 Ebn",
                "enabled": "true",
                "id": "2713d533-6538-49b9-894d-0ab80150653d",
                "type": "V",
                "reference": "TST!PMU-DCA1_732-PA14",
                "description": "National TST 1 CH 14: Northeast 732 Ebn"
            }
        ])

        meta = meta.merge(measurement_type="Phasor (Complex)", id=None)
        assert isinstance(meta, Annotations)
        assert "phase" in meta and meta["phase"] == "C"
        assert "enabled" in meta and meta["enabled"] == "true"
        assert "measurement_type" in meta and meta["measurement_type"] == "Phasor (Complex)"
        assert "id" in meta and meta["id"] is None
