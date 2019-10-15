# conduit.meta
# Implements immutable wrappers and helpers for tags and annotations
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Wed Sep 25 16:25:19 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: meta.py [] benjamin@bengfort.com $

"""
Implements immutable wrappers and helpers for tags and annotations
"""

##########################################################################
## Imports
##########################################################################

import pprint
import warnings

from collections.abc import Mapping, Sequence
from conduit.exceptions import ConduitTypeError, ConduitWarning

from conduit.constants import MEASUREMENT_TYPE
from conduit.constants import STREAM_TO_UNIT, UNIT, NAME, PHASE


##########################################################################
## Helper Functions
##########################################################################

def get_stream_type(tags, annotations):
    """
    Determines the type of the stream specified in the annotations by the
    measurement unit or infers the stream type from the units in the tags.
    """
    if MEASUREMENT_TYPE in annotations:
        return annotations[MEASUREMENT_TYPE]

    for stype, units in STREAM_TO_UNIT.items():
        if tags[UNIT] in units:
            return stype

    raise ConduitTypeError("could not determine measurement type of stream")


def get_all_stream_types(tags, annotations):
    """
    Returns a list of all stream types discovered in the tags and annotations groups
    """
    return [
        get_stream_type(*meta) for meta in zip(tags, annotations)
    ]


def accumulate(meta):
    """
    Accumulates a list of metadata and metagroup items into a single metagroup.
    """
    if len(meta) == 0:
        return metagroup([])

    items = []
    for item in meta:
        if isinstance(item, list):
            items += item

        elif isinstance(item, (metagroup, tuple)):
            items += list(item)

        else:
            items.append(item)

    # TODO: turn into a stand-alone function
    # TODO: allow user to specify the type and override this check
    types = set([type(item) for item in items])
    if len(types) > 1:
        raise ConduitTypeError("cannot accumulate multiple metadata types")

    types = types.pop()
    if types == Tags:
        types = TagsGroup
    elif types == Annotations:
        types = AnnotationsGroup
    else:
        types = metagroup

    return types(items)


##########################################################################
## Immutable Mappings
##########################################################################

class metadata(Mapping):
    """
    An immutable container for tags and annotations to ensure that metadata
    doesn't accidentally get mutated as it is transformed in a Conduit.
    """

    def __init__(self, *args, **kwargs):
        # This ensures that a copy is made of the data
        self._meta = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self._meta[key]

    def __iter__(self):
        for item in self._meta:
            yield item

    def __len__(self):
        return len(self._meta)

    def __eq__(self, other):
        if isinstance(other, metadata):
            return self._meta == other._meta
        return self._meta == other

    def clone(self):
        """
        Create a new copy of the metadata that is not referenced from the first
        """
        # The copy is made at init
        # TODO: should we deepcopy instead?
        return self.__class__(self._meta)

    def update(self, *args, **kwargs):
        """
        Creates a new copy of the metadata with the specified updates.
        """
        updates = dict(*args, **kwargs)
        clone = self.clone()
        clone._meta.update(updates)
        return clone

    def pprint(self):
        """
        Prints JSON representation of metadata with an indent
        """
        pprint.pprint(self._meta, indent=1)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self._meta)

    def __repr__(self):
        return "{} with {} keys".format(self.__class__.__name__, len(self))


class Tags(metadata):
    """
    Provides tags-specific helpers and validation
    """

    def __init__(self, *args, **kwargs):
        super(Tags, self).__init__(*args, **kwargs)

        # Tags must specify unit and name otherwise an error occurs
        for required in (UNIT, NAME):
            if required not in self:
                raise ConduitTypeError(
                    "tags do not contain required key '{}'".format(required)
                )


class Annotations(metadata):
    """
    Provides annotations-specific helpers and validation
    """

    def __init__(self, *args, **kwargs):
        super(Annotations, self).__init__(*args, **kwargs)

        # Annotations are optional so only warnings are issued
        for required in [PHASE]:
            if required not in self:
                warnings.warn(
                    "annotations do not contain required key '{}'".format(required),
                    ConduitWarning
                )


##########################################################################
## Immutable Sequences
##########################################################################

class metagroup(Sequence):
    """
    A collection of ordered metadata objects that represent multiple streams.
    This sequence is immutable to protect from accidental modification during
    the dataflow.
    """

    def __init__(self, items):
        # Convert items to immutable mappings if not already
        self._meta = [
            metadata(item) if not isinstance(item, metadata) else item
            for item in items
        ]

    def __getitem__(self, idx):
        if isinstance(idx, (tuple, list, Sequence)):
            return self.__class__([self[i] for i in idx])

        if isinstance(idx, slice):
            return self.__class__(self._meta[idx])

        return self._meta[idx]

    def __len__(self):
        return len(self._meta)

    def __eq__(self, other):
        if isinstance(other, metagroup):
            return self._meta == other._meta
        return self._meta == other

    def _metadata_class(self):
        """
        Returns the underlying metadata class
        """
        return metadata

    def clone(self):
        """
        Create a new copy of the metagroup that is not referenced from the first
        """
        # The copy is made at init
        return self.__class__(self._meta)

    def update(self, idx, *args, **kwargs):
        """
        Creates a new metagroup, updating the metadata at the specified index.
        """
        clone = self.clone()
        clone._meta[idx] = clone._meta[idx].update(*args, **kwargs)
        return clone

    def update_all(self, *args, **kwargs):
        return self.__class__([
            item.update(*args, **kwargs)
            for item in self
        ])

    def merge(self, *args, **kwargs):
        """
        Merges the metadata group into a single metadata such that the keys from
        the original metadata are retained and the values are either:

        1. The original value if the value is identical in all metadata
        2. The value of a unique key for metadata
        3. A set of all unique values (unordered)

        The metadata is then updated with the values passed into the merge function,
        note that these values will override anything in the original metadata.
        """
        merged = {}
        for meta in self:
            for key, val in meta.items():
                if key in merged:
                    # Maintain unique values as original value
                    if merged[key] == val:
                        continue

                    # If a set has already been created, add the value to the set
                    elif isinstance(merged[key], set):
                        if isinstance(val, set):
                            # TODO: test the merge of a merge
                            merged[key] &= val
                        else:
                            merged[key].add(val)

                    # Otherwise convert the original into a set
                    else:
                        merged[key] = set([merged[key], val])

                else:
                    merged[key] = val

        # Update the merged metadata with the supplied values
        merged.update(dict(*args, **kwargs))
        return self._metadata_class()(merged)

    def pprint(self):
        """
        Prints JSON representation of metadata with an indent
        """
        pprint.pprint([t._meta for t in self], indent=1)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self._meta)

    def __repr__(self):
        return "{} with {} keys".format(self.__class__.__name__, len(self))


class TagsGroup(metagroup):
    """
    Provides tags-specific group helpers and validation
    """

    def __init__(self, items):
        self._meta = [
            Tags(item) if not isinstance(item, Tags) else item
            for item in items
        ]

    def _metadata_class(self):
        """
        Returns the underlying metadata class
        """
        return Tags

    def units(self):
        """
        Helper method to fetch the list of units in the tag group
        """
        return [
            meta[UNIT] for meta in self
        ]


class AnnotationsGroup(metagroup):
    """
    Provides annotations-specific group helpers and validation
    """

    def __init__(self, items):
        self._meta = [
            Annotations(item) if not isinstance(item, Annotations) else item
            for item in items
        ]

    def _metadata_class(self):
        """
        Returns the underlying metadata class
        """
        return Annotations

    def measurement_types(self):
        """
        Helper to fetch the list of measurement types in the annotation group
        """
        return [
            meta.get(MEASUREMENT_TYPE, None) for meta in self
        ]
