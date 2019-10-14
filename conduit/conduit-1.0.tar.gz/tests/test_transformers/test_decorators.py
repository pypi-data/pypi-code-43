# tests.test_transformers.test_decorators
# Test the transformers decorator helper utilities package
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Fri Sep 13 12:29:37 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_decorators.py [] benjamin@bengfort.com $

"""
Test the transformers decorator helper utilities package
"""

##########################################################################
## Imports
##########################################################################

import pytest

from conduit.constants import *
from conduit.exceptions import *
from conduit.transformers.decorators import *
from conduit.transformers.decorators import _validate_metadata


##########################################################################
## Helper Tests
##########################################################################

@pytest.mark.parametrize("tags, annotations", [
    ({"unit": "VPHM", "name": "test"}, {"phase": "B"}),
    (Tags({"unit": "VPHM", "name": "test"}), Annotations({"phase": "B"})),
    (
        [{"unit": "VPHM", "name": "mag"}, {"unit": "VPHA", "name": "ang"}],
        [{"phase": "B"}, {"phase": "B"}]
    ),
    (
        TagsGroup([{"unit": "VPHM", "name": "mag"}, {"unit": "VPHA", "name": "ang"}]),
        AnnotationsGroup([{"phase": "B"}, {"phase": "B"}]),
    ),
])
def test_validate_metadata(tags, annotations):
    """
    Ensure metadata is correctly validated
    """
    tags, annotations = _validate_metadata(tags, annotations)
    assert isinstance(tags, (Tags, TagsGroup))
    assert isinstance(annotations, (Annotations, AnnotationsGroup))


@pytest.mark.parametrize("tags, annotations", [
    ({"name": "unitless"}, {"phase": "A"}),
    (
        [{"unit": "VPHM", "name": "foo"}, {"unit": "nameless"}],
        [{"phase": "A"}, {"phase": "B"}]
    ),
    (42, 24),
])
def test_invalid_metadata(tags, annotations):
    """
    Ensure invalid metadata raises an exception
    """
    with pytest.raises((ConduitTypeError, ValidationError)):
        _validate_metadata(tags, annotations)


##########################################################################
## Transformer Decorator Tests
##########################################################################

class TestTransformerDecorator(object):
    """
    Test the transformer decorator stream validation mechanism
    """

    def test_valid_accepts(self):
        """
        Ensure all valid accepts are allowed by transformer
        """
        try:
            transformer(VALID_ACCEPTS)
        except ConduitValueError as e:
            pytest.fail("valid accept raised value error: {}".format(e))

    def test_invalid_accepts(self):
        """
        Assert a validation error is raised on exception if bad accepts
        """
        with pytest.raises(ConduitValueError, match="not a valid stream type"):
            @transformer([VOLTAGE_ANGLE, VOLTAGE_MAGNITUDE, "foo", CURRENT_ANGLE])
            def myfunc(data, tags, annotations, **kwargs):
                pass

    def test_accepts_none(self, voltage_magnitude, voltage_angle):
        """
        Enusre that accepts=None will accept any stream
        """
        @transformer(None)
        def myfunc(data, tags, annotations, **kwargs):
            pass

        try:
            myfunc(None, {'unit': None, 'name': None}, {'phase': 'B'})
            myfunc(*voltage_magnitude)
            myfunc(*voltage_angle)
        except ValidationError as e:
            pytest.fail("none accept raised validation error: {}".format(e))

    def test_accepts_str(self, voltage_magnitude, voltage_angle):
        """
        Enusre that accepts=str is valid input
        """
        @transformer(VOLTAGE_MAGNITUDE)
        def myfunc(data, tags, annotations, **kwargs):
            pass

        try:
            myfunc(*voltage_magnitude)
        except ValidationError as e:
            pytest.fail("string accept raised validation error: {}".format(e))

        with pytest.raises(ValidationError, match="not supported by this transformer"):
            myfunc(*voltage_angle)

    def test_accepts_list(self, voltage_magnitude, voltage_angle, current_angle):
        """
        Ensure that accepts=list is valid input
        """
        @transformer([VOLTAGE_MAGNITUDE, VOLTAGE_ANGLE])
        def myfunc(data, tags, annotations, **kwargs):
            pass

        try:
            myfunc(*voltage_magnitude)
            myfunc(*voltage_angle)
        except ValidationError as e:
            pytest.fail("string accept raised validation error: {}".format(e))

        with pytest.raises(ValidationError, match="not supported by this transformer"):
            myfunc(*current_angle)

    def test_transformer_validation_by_unit(self, voltage_angle):
        """
        Test stream validation by direct unit
        """
        @transformer([VPHM, VPHA])
        def myfunc(data, tags, annotations, **kwargs):
            pass

        try:
            myfunc(*voltage_angle)
        except ValidationError as e:
            pytest.fail("caught unexpected validation error: {}".format(e))

    def test_transformer_validation_by_measurement_type(self, current_magnitude):
        """
        Test stream validation by measurement type
        """
        @transformer(CURRENT_ANGLE)
        def myfunc(data, tags, annotations, **kwargs):
            pass

        data, tags, annotations = current_magnitude
        annotations = annotations.update(measurement_type=CURRENT_ANGLE)

        try:
            myfunc(data, tags, annotations)
        except ValidationError as e:
            pytest.fail("caught unexpected validation error: {}".format(e))

    def test_transformer_validation_by_measurement_type_mapping(self, current_angle):
        """
        Test stream validation by measurement type to unit mapping
        """
        @transformer([VOLTAGE_ANGLE, CURRENT_ANGLE])
        def myfunc(data, tags, annotations, **kwargs):
            pass

        data, tags, annotations = current_angle
        assert "measuement_type" not in annotations
        assert tags[UNIT] in STREAM_TO_UNIT[CURRENT_ANGLE]

        try:
            myfunc(data, tags, annotations)
        except ValidationError as e:
            pytest.fail("caught unexpected validation error: {}".format(e))
