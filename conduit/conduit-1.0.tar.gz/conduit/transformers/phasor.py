# conduit.transformers.phasor
# Phasor specific transformers for common power engineering computation
#
# Author:   Kevin D. Jones <kdjones@users.noreply.github.com>
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Fri Sep 27 11:48:42 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: phasor.py [] kdjones@users.noreply.github.com $

"""
Function dectorators for expanding transformer usage.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np
import pandas as pd

from .decorators import phasor, phasor_pair, phasor_group, phasor_group_pair

from conduit.exceptions import ConduitValueError
from conduit.meta import get_all_stream_types, TagsGroup, AnnotationsGroup

from conduit.constants import RADIANS, PER_UNIT, VOLTS_L_L
from conduit.constants import VOLTAGE_ANGLE, VOLTAGE_MAGNITUDE
from conduit.constants import CURRENT_ANGLE, CURRENT_MAGNITUDE
from conduit.constants import UNIT, NAME, PHASE, MEASUREMENT_TYPE
from conduit.constants import ZERO_SEQ, POS_SEQ, NEG_SEQ, ALPHA, ALPHA_2
from conduit.constants import REAL_PHASOR_COMPONENT, IMAGINARY_PHASOR_COMPONENT
from conduit.constants import COMPLEX_PHASOR, COMPLEX_POWER, P_JQ, MW, MVA, MVAR
from conduit.constants import REAL_POWER, REACTIVE_POWER, APPARENT_POWER, POWER_FACTOR


##########################################################################
## Phasor Compositions
##########################################################################

@phasor
def real(df, tags, annotations):
    """
    Converts the two component streams of a Phasor (Magnitude and Angle) into the
    Real part of the Complex Phasor. Handles angles in degrees or radians.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with two columns: one for magnitude and one for angle.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series with the real component of the complex phasor

    tags : Tags
        A single tagset with the units of the magnitude stream

    annotations : Annotations
        A single annotationset with the new stream type
    """
    magi = _find_magnitude_index(tags, annotations)
    angi = _find_angle_index(tags, annotations)

    mag = _select(df, magi)
    ang = _select(df, angi)
    if tags[angi][UNIT] != RADIANS:
        ang = np.radians(ang)

    # Merge and update metadata to a single representation
    tags = tags.merge(**{NAME: REAL_PHASOR_COMPONENT, UNIT: tags[magi][UNIT]})
    annotations = annotations.merge(**{MEASUREMENT_TYPE: REAL_PHASOR_COMPONENT})

    series = pd.Series(mag * np.cos(ang), index=df.index, name=tags[NAME])
    return series, tags, annotations


@phasor
def imaginary(df, tags, annotations):
    """
    Converts the two component streams of a Phasor (Magnitude and Angle) into the
    Imaginary part of the Complex Phasor. Handles angles in degrees or radians.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with two columns: one for magnitude and one for angle.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series with the imaginary component of the complex phasor

    tags : Tags
        A single tagset with the units of the magnitude stream

    annotations : Annotations
        A single annotationset with the new stream type
    """
    magi = _find_magnitude_index(tags, annotations)
    angi = _find_angle_index(tags, annotations)

    mag = _select(df, magi)
    ang = _select(df, angi)
    if tags[angi][UNIT] != RADIANS:
        ang = np.radians(ang)

    # Merge and update metadata to a single representation
    tags = tags.merge(**{NAME: IMAGINARY_PHASOR_COMPONENT, UNIT: tags[magi][UNIT]})
    annotations = annotations.merge(**{MEASUREMENT_TYPE: IMAGINARY_PHASOR_COMPONENT})

    series = pd.Series(mag * np.sin(ang), index=df.index, name=tags[NAME])
    return series, tags, annotations


@phasor
def complex_phasor(df, tags, annotations):
    """
    Converts the two component streams of a Phasor (Magnitude and Angle) into a
    single complex valued stream. Handles angles in degrees or radians.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with two columns: one for magnitude and one for angle.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series with the complex phasor

    tags : Tags
        A single tagset with the units of the magnitude stream

    annotations : Annotations
        A single annotationset with the new stream type
    """
    magi = _find_magnitude_index(tags, annotations)
    angi = _find_angle_index(tags, annotations)

    mag = _select(df, magi)
    ang = _select(df, angi)
    if tags[angi][UNIT] != RADIANS:
        ang = np.radians(ang)

    # Merge and update metadata to a single representation
    tags = tags.merge(**{NAME: COMPLEX_PHASOR, UNIT: tags[magi][UNIT]})
    annotations = annotations.merge(**{MEASUREMENT_TYPE: COMPLEX_PHASOR})

    r = (mag * np.cos(ang)) # compute the real component
    i = (mag * np.sin(ang)) # compute the imaginary component

    # simplest way to create a complex numpy array is r + 1j * i
    series = pd.Series(r + 1j * i, index=df.index, name=tags[NAME])
    return series, tags, annotations


##########################################################################
## Phasor Pair Compositions
##########################################################################

@phasor_pair
def complex_power(df, tags, annotations):
    """
    This computes the complex power (P + jQ) in Per Unit or MW+jMVAR based on
    the input units.

    Formula: complex_voltage * conj(complex_current)

    Parameters
    ----------
    df : pd.DataFrame
        The input data with four columns: voltage and current angle and magnitudes.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of complex power values over time

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    vmagi = _find_index(VOLTAGE_MAGNITUDE, tags, annotations)
    vangi = _find_index(VOLTAGE_ANGLE, tags, annotations)
    imagi = _find_index(CURRENT_MAGNITUDE, tags, annotations)
    iangi = _find_index(CURRENT_ANGLE, tags, annotations)

    complex_voltage, _, _ = complex_phasor(*_select_all([vmagi, vangi], df, tags, annotations))
    complex_current, _, _ = complex_phasor(*_select_all([imagi, iangi], df, tags, annotations))
    series = complex_voltage * np.conjugate(complex_current)
    series.name = COMPLEX_POWER

    # NOTE: Assumes that VPHM is VOLTS_L_N which may be incorrect
    if tags[vmagi][UNIT] == VOLTS_L_L:
        series /= np.sqrt(3)

    # Merge and update metadata to a single representation
    units = PER_UNIT if tags[vmagi][UNIT] == PER_UNIT else P_JQ
    tags = tags.merge(**{NAME: COMPLEX_POWER, UNIT: units})
    annotations = annotations.merge(**{MEASUREMENT_TYPE: COMPLEX_POWER})

    return series, tags, annotations


@phasor_pair
def real_power(df, tags, annotations):
    """
    Computes the real power (P) in Per Unit or MW based on the input units.

    Formula: (complex_voltage * conj(complex_current)).real

    Parameters
    ----------
    df : pd.DataFrame
        The input data with four columns: voltage and current angle and magnitudes.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of real power values over time

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    series, tags, annotations = complex_power(df, tags, annotations)

    # Convert units and update metadata
    units = PER_UNIT if tags[UNIT] == PER_UNIT else MW
    tags = tags.update({NAME: REAL_POWER, UNIT: units})
    annotations = annotations.update({MEASUREMENT_TYPE: REAL_POWER})

    # Return the real power component from the series
    series = pd.Series(series.real, index=series.index, name=REAL_POWER)
    return series, tags, annotations


@phasor_pair
def reactive_power(df, tags, annotations):
    """
    This computes the reactive power (Q) in Per Unit or MVAR based on the input units.

    Formula: (complex_voltage * conj(complex_current)).imag

    Parameters
    ----------
    df : pd.DataFrame
        The input data with four columns: voltage and current angle and magnitudes.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of reactive power values over time

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    series, tags, annotations = complex_power(df, tags, annotations)

    # Convert units and update metadata
    units = PER_UNIT if tags[UNIT] == PER_UNIT else MVAR
    tags = tags.update({NAME: REACTIVE_POWER, UNIT: units})
    annotations = annotations.update({MEASUREMENT_TYPE: REACTIVE_POWER})

    # Return the real power component from the series
    series = pd.Series(series.imag, index=series.index, name=REACTIVE_POWER)
    return series, tags, annotations


@phasor_pair
def apparent_power(df, tags, annotations):
    """
    This computes the apparent power (S) in Per Unit or MVA based on the input units.

    Formula: abs(complex_voltage * conj(complex_current))

    Parameters
    ----------
    df : pd.DataFrame
        The input data with four columns: voltage and current angle and magnitudes.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of apparent power values over time

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    series, tags, annotations = complex_power(df, tags, annotations)

    # Convert units and update metadata
    units = PER_UNIT if tags[UNIT] == PER_UNIT else MVA
    tags = tags.update({NAME: APPARENT_POWER, UNIT: units})
    annotations = annotations.update({MEASUREMENT_TYPE: APPARENT_POWER})

    # Return the real power component from the series
    series = pd.Series(np.abs(series), index=series.index, name=APPARENT_POWER)
    return series, tags, annotations


@phasor_pair
def power_factor(df, tags, annotations):
    """
    Computes the power factor.

    Formula: real_power() / apparent_power()

    Parameters
    ----------
    df : pd.DataFrame
        The input data with four columns: voltage and current angle and magnitudes.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of power factor values over time

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    series, tags, annotations = complex_power(df, tags, annotations)

    # Compute the power factor
    series = pd.Series(
        series.real / np.abs(series), index=series.index, name=POWER_FACTOR
    )

    # Convert units and update metadata
    tags = tags.update({NAME: POWER_FACTOR, UNIT: PER_UNIT})
    annotations = annotations.update({MEASUREMENT_TYPE: POWER_FACTOR})

    return series, tags, annotations


##########################################################################
## Phasor Group Compositions
##########################################################################

@phasor_group
def complex_phasor_group(df, tags, annotations):
    """
    Returns the phasor group as complex phasors for each power phase.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with six columns: angle and magnitudes for three phases.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    data : pd.DataFrame
        A DataFrame with a complex phasor for each power phase

    tags : TagsGroup
        Tags describing each column (power phase) in the output

    annotations : AnnotationsGroup
        Annotations describing each column (power phase) in the output
    """
    data, tg, ag = [], [], []
    for phase in ("A", "B", "C"):
        s, t, a = complex_phasor(*_select_phase(phase, df, tags, annotations))
        s.name = "Phase {}".format(phase)
        data.append(s)
        tg.append(t.update({NAME: s.name}))
        ag.append(a)

    return pd.concat(data, axis=1), TagsGroup(tg), AnnotationsGroup(ag)


@phasor_group
def sequence_components(df, tags, annotations):
    """
    Formula is here: https://en.wikipedia.org/wiki/Symmetrical_components

    Parameters
    ----------
    df : pd.DataFrame
        The input data with six columns: angle and magnitudes for three phases.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    data : pd.DataFrame
        A DataFrame with all three sequence components over time

    tags : TagsGroup
        Tags describing each column (sequence component) in the output

    annotations : AnnotationsGroup
        Annotations describing each column (sequence component) in the output
    """
    # Convert to complex power group
    # TODO: Determine if input is already in complex power components
    df, tags, annotations = complex_phasor_group(df, tags, annotations)

    # Compute the sequence components
    df = pd.concat([
        _zero_sequence(df),
        _positive_sequence(df),
        _negative_sequence(df)
    ], axis=1)

    # Update the annotations with the measurement types
    annotations = AnnotationsGroup([
        meta.update({MEASUREMENT_TYPE: seq})
        for meta, seq in zip(annotations, (ZERO_SEQ, POS_SEQ, NEG_SEQ))
    ])

    return df, tags, annotations


@phasor_group
def zero_sequence(df, tags, annotations):
    """
    Formula is (A + B + C) / 3.
    This is phasor math in complex plane.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with six columns: angle and magnitudes for three phases.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of the complex zero sequence component over time.

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    # Convert to complex power group
    # TODO: Determine if input is already in complex power components
    df, tags, annotations = complex_phasor_group(df, tags, annotations)

    # Merge tags and annotations for zero sequence
    tags = tags.merge()
    annotations = annotations.merge(**{MEASUREMENT_TYPE: ZERO_SEQ})

    return _zero_sequence(df), tags, annotations


def _zero_sequence(cpg):
    """
    Helper function to compute the zero-sequence from a complex phasor group.
    Expects CPG to be complex phasor group with phase A, B, C columns respectively.
    """
    A, B, C = cpg.iloc[:,0], cpg.iloc[:,1], cpg.iloc[:,2]
    return pd.Series((A + B + C) / 3, index=cpg.index, name=ZERO_SEQ)


@phasor_group
def positive_sequence(df, tags, annotations):
    """
    Formula is (A + B * 1<120 + C * 1<240) / 3
    ALPHA and ALPHA_2 are unit vectors at 120 degrees and -120 degrees, respectively.

    Parameters
    ----------
    df : pd.DataFrame
        The input data with six columns: angle and magnitudes for three phases.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of the complex positive sequence component over time.

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    # Convert to complex power group
    # TODO: Determine if input is already in complex power components
    df, tags, annotations = complex_phasor_group(df, tags, annotations)

    # Merge tags and annotations for zero sequence
    tags = tags.merge()
    annotations = annotations.merge(**{MEASUREMENT_TYPE: POS_SEQ})

    return _positive_sequence(df), tags, annotations


def _positive_sequence(cpg):
    """
    Helper function to compute the positive-sequence from a complex phasor group.
    Expects CPG to be complex phasor group with phase A, B, C columns respectively.
    """
    A, B, C = cpg.iloc[:,0], cpg.iloc[:,1], cpg.iloc[:,2]
    return pd.Series((A + B * ALPHA + C * ALPHA_2) / 3, index=cpg.index, name=POS_SEQ)


@phasor_group
def negative_sequence(df, tags, annotations):
    """
    Formula is (A + B * 1<240 + C * 1<120) / 3

    Parameters
    ----------
    df : pd.DataFrame
        The input data with six columns: angle and magnitudes for three phases.

    tags : TagsGroup
        A collection of tags that describe each column in the input data.

    annotations : AnnotationsGroup
        A collection of annotations that describe each column in the input data.

    Returns
    -------
    series : pd.Series
        A single series of the complex negative sequence component over time.

    tags : Tags
        A single tagset with the units based on the input

    annotations : Annotations
        A single annotationset with the new stream type
    """
    # Convert to complex power group
    # TODO: Determine if input is already in complex power components
    df, tags, annotations = complex_phasor_group(df, tags, annotations)

    # Merge tags and annotations for zero sequence
    tags = tags.merge()
    annotations = annotations.merge(**{MEASUREMENT_TYPE: NEG_SEQ})

    return _negative_sequence(df), tags, annotations


def _negative_sequence(cpg):
    """
    Helper function to compute the negative-sequence from a complex phasor group.
    Expects CPG to be complex phasor group with phase A, B, C columns respectively.
    """
    A, B, C = cpg.iloc[:,0], cpg.iloc[:,1], cpg.iloc[:,2]
    return pd.Series((A + B * ALPHA_2 + C * ALPHA) / 3, index=cpg.index, name=NEG_SEQ)


##########################################################################
## Phasor Group Pair Compositions
##########################################################################

# THESE ARE THE SAME AS SINGLE PHASE BUT SUMMED ACROSS ALL THREE PHASES
# I DID NOT TAKE THE TIME TO WRITE THEM OUT BECAUSE IT WOULD BE CONCEPTUALLY REDUNDANT AT THIS POINT

@phasor_group_pair
def three_phase_mw(df, tags, annotations):
    raise NotImplementedError("three phase power computations not yet implemented")


@phasor_group_pair
def three_phase_mvar(df, tags, annotations):
    raise NotImplementedError("three phase power computations not yet implemented")


@phasor_group_pair
def three_phase_mva(df, tags, annotations):
    raise NotImplementedError("three phase power computations not yet implemented")


@phasor_group_pair
def three_phase_complex_power(df, tags, annotations):
    raise NotImplementedError("three phase power computations not yet implemented")


@phasor_group_pair
def three_phase_powerfactor(dataframe, stream_types, phases, units):
    raise NotImplementedError("three phase power computations not yet implemented")


##########################################################################
## Helper Functions
##########################################################################

def _find_index(mtype, tags, annotations):
    for idx, stype in enumerate(get_all_stream_types(tags, annotations)):
        if stype == mtype:
            return idx
    raise ConduitValueError("could not determine index of {} stream".format(mtype))


def _find_magnitude_index(tags, annotations):
    for idx, stype in enumerate(get_all_stream_types(tags, annotations)):
        if stype in {VOLTAGE_MAGNITUDE, CURRENT_MAGNITUDE}:
            return idx
    raise ConduitValueError("could not determine phasor magnitude index")


def _find_angle_index(tags, annotations):
    for idx, stype in enumerate(get_all_stream_types(tags, annotations)):
        if stype in {VOLTAGE_ANGLE, CURRENT_ANGLE}:
            return idx
    raise ConduitValueError("could not determine phasor magnitude index")


def _find_phase_indices(phase, annotations):
    indices = []
    for idx, meta in enumerate(annotations):
        if meta[PHASE] == phase:
            indices.append(idx)

    if len(indices) == 0:
        raise ConduitValueError("could not find indices for phase {}".format(phase))
    return indices


def _select(df, idx):
    return df.iloc[:,idx]


def _select_all(idx, df, tags, annotations):
    return _select(df, idx), tags[idx], annotations[idx]


def _select_phase(phase, df, tags, annotations):
    indices = _find_phase_indices(phase, annotations)
    return _select_all(indices, df, tags, annotations)