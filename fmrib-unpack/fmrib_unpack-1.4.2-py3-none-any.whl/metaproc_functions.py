#!/usr/bin/env python
#
# metaproc_functions.py - Functions for manipulating column metadata.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains ``metaproc`` functions - functions for manipulating
column metadata.

Some :class:`.Column` instances have a ``metadata`` attribute, containing some
additional information about the column. The functions in this module can be
used to modify these metadata values. Currently, column metadata is only used
to generate a description of each column (via the ``--description_file``
command-line option).

All ``metaproc`` functions must accept three arguments:

 - The :class:`.DataTable`

 - The variable ID associated with the column. This may be ``None``, if the
   column has been newly added, and is not associated with any other variable.

 - The metadata value.
"""


from . import util
from . import custom
from . import coding
from . import hierarchy


@custom.metaproc('codingdesc')
def codingDescriptionFromValue(dtable, vid, val):
    """Generates a description for a value from a specific data coding. """
    fname = coding.getCodingFilePath(dtable, vid)
    descs = coding.loadCodingFile(fname)
    desc  = descs['meaning'][val]
    return '{} - {}'.format(val, desc)


@custom.metaproc('hierarchynumdesc')
def hierarchicalDescriptionFromNumeric(dtable, vid, val):
    """Generates a description for a numeric hierarchical code. """
    val  = hierarchy.numericToCode(val, dtable=dtable, vid=vid)
    hier = hierarchy.getHierarchyFilePath(dtable, vid)
    hier = hierarchy.loadHierarchyFile(hier)
    desc = hier.description(val)
    return '{} - {}'.format(val, desc)


@custom.metaproc('hierarchycodedesc')
def hierarchicalDescriptionFromCode(dtable, vid, val):
    """Generates a description for a hierarchical code. """
    hier = hierarchy.getHierarchyFilePath(dtable=dtable, vid=vid)
    hier = hierarchy.loadHierarchyFile(hier)
    desc = hier.description(val)
    return '{} - {}'.format(val, desc)


@custom.metaproc('icd10.numdesc')
@util.deprecated('Use hierarchynumdesc instead')
def icd10DescriptionFromNumeric(dtable, vid, val):
    """Generates a description for a numeric ICD10 code. """
    return hierarchicalDescriptionFromNumeric(dtable, vid, val)


@custom.metaproc('icd10.codedesc')
@util.deprecated('Use hierarchycodedesc instead')
def icd10DescriptionFromCode(dtable, vid, val):
    """Generates a description for an ICD10 code. """
    return hierarchicalDescriptionFromCode(dtable, vid, val)


@custom.metaproc('icd9.numdesc')
@util.deprecated('Use hierarchynumdesc instead')
def icd9DescriptionFromNumeric(dtable, vid, val):
    """Generates a description for a numeric ICD9 code. """
    return hierarchicalDescriptionFromNumeric(dtable, vid, val)


@custom.metaproc('icd9.codedesc')
@util.deprecated('Use hierarchycodedesc instead')
def icd9DescriptionFromCode(dtable, vid, val):
    """Generates a description for an ICD9 code. """
    return hierarchicalDescriptionFromCode(dtable, vid, val)


@custom.metaproc('opcs4.numdesc')
@util.deprecated('Use hierarchynumdesc instead')
def opcs4DescriptionFromNumeric(dtable, vid, val):
    """Generates a description for a numeric OPCS4 code. """
    return hierarchicalDescriptionFromNumeric(dtable, vid, val)


@custom.metaproc('opcs4.codedesc')
@util.deprecated('Use hierarchycodedesc instead')
def opcs4DescriptionFromCode(dtable, vid, val):
    """Generates a description for an OPCS4 code. """
    return hierarchicalDescriptionFromCode(dtable, vid, val)


@custom.metaproc('opcs3.numdesc')
@util.deprecated('Use hierarchynumdesc instead')
def opcs3DescriptionFromNumeric(dtable, vid, val):
    """Generates a description for a numeric OPCS3 code. """
    return hierarchicalDescriptionFromNumeric(dtable, vid, val)


@custom.metaproc('opcs3.codedesc')
@util.deprecated('Use hierarchycodedesc instead')
def opcs3DescriptionFromCode(dtable, vid, val):
    """Generates a description for an OPCS3 code. """
    return hierarchicalDescriptionFromCode(dtable, vid, val)
