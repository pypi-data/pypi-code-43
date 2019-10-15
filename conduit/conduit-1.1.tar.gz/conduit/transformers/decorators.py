# conduit.transformers.decorators
# Function dectorators for expanding transformer usage.
#
# Author:   Kevin D. Jones <kdjones@users.noreply.github.com>
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Wed May 29 17:55:38 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: decorators.py [] kdjones@users.noreply.github.com $

"""
Function dectorators for expanding transformer usage.
"""

##########################################################################
## Imports
##########################################################################

from functools import wraps

from conduit.meta import get_stream_type
from conduit.exceptions import ConduitValueError, ValidationError
from conduit.meta import Tags, Annotations, TagsGroup, AnnotationsGroup

from conduit.constants import STREAM_TO_UNIT
from conduit.constants import VPHM, VPHA, VOLTS, VOLTS_L_L, VOLTS_L_N
from conduit.constants import DEGREES, RADIANS, IPHA, AMPS, IPHM, PER_UNIT
from conduit.constants import UNIT, MEASUREMENT_TYPE
from conduit.constants import UNITS, MEASUREMENT_TYPES, CALCULATED_STREAM_TYPES


# valid ways to specify what a transformer accepts as input
VALID_ACCEPTS = frozenset([
    accept
    for types in [UNITS, MEASUREMENT_TYPES, CALCULATED_STREAM_TYPES]
    for accept in types
])


##########################################################################
## transformer validation
##########################################################################

def transformer(accepts):
    """
    Validates that the type of stream passed into the transformer is compatible
    with the specified calculation by checking the units or measurement type of the
    stream. Although this is somewhat redundant with the Conduit and Phasor types,
    the decorator allows transformers to be directly applied to data with correctly
    associated metadata.

    Parameters
    ----------
    accepts : str or list of str or None
        The valid units, measurement types, or caculated stream types that the
        transformer will validate. If None is passed in then the stream will
        accept *any* data no matter the tags or annotations.

    Returns
    -------
    decorator : func
        A decorator function that wraps the transformer
    """
    # Validate what has been passed into accepts
    # This only happens once at decoration time, so should be efficient enough
    if accepts is not None:
        if isinstance(accepts, str):
            accepts = (accepts,)

        for accept in accepts:
            if accept not in VALID_ACCEPTS:
                raise ConduitValueError((
                    "'{}' is not a valid stream type - "
                    "see conduit.transformers.VALID_ACCEPTS"
                ).format(accept))

        # Make sure accepts is a frozenset for fast lookup
        accepts = frozenset(accepts)

    # Create validation closure
    def validate(tags, annotations):
        if accepts is None:
            return True

        if tags[UNIT] in accepts:
            return True

        if MEASUREMENT_TYPE in annotations and annotations[MEASUREMENT_TYPE] in accepts:
            return True

        # If measurement type is not available, compare stream type to unit mappings
        for accept in accepts:
            if accept in STREAM_TO_UNIT:
                for unit in STREAM_TO_UNIT[accept]:
                    if tags[UNIT] == unit:
                        return True

        return False

    def decorator(func):
        @wraps(func)
        def wrapper(data, tags, annotations, **kwargs):
            tags, annotations = _validate_metadata(tags, annotations)

            if not validate(tags, annotations):
                stype = get_stream_type(tags, annotations)
                raise ValidationError(
                    "stream type '{}' not supported by this transformer".format(stype)
                )

            return func(data, tags=tags, annotations=annotations, **kwargs)

        return wrapper
    return decorator


##########################################################################
## Composition Validation
##########################################################################


def composition(func):
    """
    Validates a composition of multiple streams is compatible with the specified
    calculation by comparing the units and measurement types of the stream. By default
    the composition ensures the same number of tags and annotations are passed to
    the computation function and that incompatible mixed units are not collected.

    Returns
    -------
    decorator : func
        A decorator function that wraps the composition
    """
    @wraps(func)
    def wrapper(data, tags, annotations, **kwargs):
        tags, annotations = _validate_metadata(tags, annotations)
        if not isinstance(tags, TagsGroup) or not isinstance(annotations, AnnotationsGroup):
            raise ConduitValueError("compositions expect multiple streams as input")

        if len(tags) != len(annotations) != len(data):
            raise ConduitValueError("misaligned data, tags, or annotations")

        units = frozenset(tags.units())
        if len(units & {VPHM, VOLTS, VOLTS_L_N, VOLTS_L_L, PER_UNIT}) > 1:
            raise ValidationError("voltage units are mixed")

        if len(units & {VPHA, AMPS, PER_UNIT}) > 1:
            raise ValidationError("current units are mixed")

        if DEGREES in units and RADIANS in units:
            raise ValidationError("mixed angle units with both degrees and radians")

        return func(data, tags, annotations, **kwargs)
    return wrapper


def phasor(func):
    """
    Validates that the stream types passed into the function are correctly
    structured as a phase angle and magnitude of the same measurement type.
    Note, this does not validate that they are in the same phase.

    Returns
    -------
    decorator : func
        A decorator function that wraps the composition
    """
    @wraps(func)
    def wrapper(data, tags, annotations, **kwargs):
        if len(tags) != 2:
            raise ValidationError("a phasor is exactly two streams")

        units = frozenset(tags.units())
        if units != {IPHA, IPHM} and units != {VPHA, VPHM}:
            raise ValidationError(
                "phasor must consist of either voltage or current angle and magnitude"
            )
        return func(data, tags, annotations, **kwargs)

    # NOTE: cannot decorate a decorator!
    # NOTE: composition handles the metadata
    return composition(wrapper)


def phasor_pair(func):
    """
    Validates that the stream types passed into the function are correctly
    structured as a phasor pair with both a voltage and a current phasor.

    Returns
    -------
    decorator : func
        A decorator function that wraps the composition
    """
    @wraps(func)
    def wrapper(data, tags, annotations, **kwargs):
        if len(tags) != 4:
            raise ValidationError("a phasor pair is composed of exactly four streams")

        units = frozenset(tags.units())
        if units != {IPHA, VPHA, IPHM, VPHM}:
            raise ValidationError(
                "phasor pair must consist of both voltage and current phasors"
            )
        return func(data, tags, annotations, **kwargs)

    # NOTE: cannot decorate a decorator!
    # NOTE: composition handles the metadata
    return composition(wrapper)


def phasor_group(func):
    """
    Validates that the stream types passed into the function are correctly
    structured as a phasor group with either voltage or current phasors for
    three phase power (e.g. phases A, B, and C).

    Returns
    -------
    decorator : func
        A decorator function that wraps the composition
    """
    @wraps(func)
    def wrapper(data, tags, annotations, **kwargs):
        if len(tags) % 2 != 0:
            raise ValidationError("a phasor group must have an even number of streams")

        units = frozenset(tags.units())
        if units != {IPHA, IPHM} and units != {VPHA, VPHM}:
            raise ValidationError(
                "phasor group must consist of either voltage or current phasors"
            )

        # TODO: raise a validation error if pairs do not exist
        return func(data, tags, annotations, **kwargs)

    # NOTE: cannot decorate a decorator!
    # NOTE: composition handles the metadata
    return composition(wrapper)


def phasor_group_pair(func):
    """
    Validates that the stream types passed into the function are correctly
    structured as a phasor group pair with both voltage or current phasors for
    three phase power (e.g. phases A, B, and C).

    Returns
    -------
    decorator : func
        A decorator function that wraps the composition
    """
    @wraps(func)
    def wrapper(data, tags, annotations, **kwargs):
        if len(tags) % 4 != 0:
            raise ValidationError(
                "a phasor group pair must have sets of four streams"
            )

        units = frozenset(tags.units())
        if units != {IPHA, IPHM, VPHA, VPHM}:
            raise ValidationError(
                "phasor group pair must consist of both voltage and current phasors"
            )
        return func(data, tags, annotations, **kwargs)

    # NOTE: cannot decorate a decorator!
    # NOTE: composition handles the metadata
    return composition(wrapper)


##########################################################################
## Helper Functions
##########################################################################

def _validate_metadata(tags, annotations):
    if not isinstance(tags, (Tags, TagsGroup)):
        # NOTE: type checking this way is a bit fragile, but can be avoided
        # by directly creating Tags or a TagsGroup before passing into func
        if isinstance(tags, dict):
            tags = Tags(tags)

        elif isinstance(tags, (list, tuple)):
            tags = TagsGroup(tags)

        else:
            raise ValidationError("could not validate tags type {}".format(type(tags)))

    if not isinstance(annotations, (Annotations, AnnotationsGroup)):
        # NOTE: type checking this way is a bit fragile, but can be avoided by
        # directly creating Annotations or a AnnotationsGroup before passing into func
        if isinstance(annotations, dict):
            annotations = Annotations(annotations)

        elif isinstance(annotations, (list, tuple)):
            annotations = AnnotationsGroup(annotations)

        else:
            raise ValidationError(
                "could not validate annotations type {}".format(type(annotations))
            )

    return tags, annotations