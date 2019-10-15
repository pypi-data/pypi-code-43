# conduit.transformers.conversions
# Transformers that perform data type and unit conversions.
#
# Author:   Kevin D. Jones <kdjones@users.noreply.github.com>
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Fri Sep 13 16:19:29 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: decorators.py [] benjamin@bengfort.com $

"""
Transformers that perform data type and unit conversions.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np

from .decorators import transformer

from conduit.meta import get_stream_type
from conduit.exceptions import ConduitValueError
from conduit.constants import UNIT, MEASUREMENT_TYPE, SQRT_3, PI
from conduit.constants import VOLTAGE_MAGNITUDE, VOLTAGE_ANGLE, VOLTS, VPHM, VPHA
from conduit.constants import CURRENT_MAGNITUDE, CURRENT_ANGLE, AMPS, IPHM, IPHA
from conduit.constants import PER_UNIT, VOLTS_L_N, VOLTS_L_L, DEGREES, RADIANS


##########################################################################
## Unit conversions
##########################################################################

@transformer([VOLTAGE_MAGNITUDE, CURRENT_MAGNITUDE])
def per_unit(series, tags, annotations, base_kv=None):
    """Convert a magnitude stream into per-unit quantities.

    The Per Unit system is a unit-less domain that allows many common power
    engineering calculations to be carried out in a much simpler fashion. Voltage
    and current magnitudes are converted using different formulas that are
    determined by the specified stream units in the tags.

    Voltage is converted to Per Unit by dividing the volts by the Base KV.
    Base KV can be set to anything but is generally mapped to the voltage level of
    the network. For example a 500kV network has a Base KV of 500. Base KV is
    represented in Line-to-Line KV.

    Conversion of voltage magnitudes to per unit is applied differently based on
    the starting units. Voltage magnitudes are traditionally reported in
    line-to-neutral volts but are commonly displayed in line-to-line volts. The
    difference between these two is a SQRT_3 multiplication.

    Current is converted to Per Unit in a similar fashion, however the conversion
    requires a constant System Base MVA value. The nearly ubiquitous rule of thumb
    is 100 MVA for System Base, which is used here.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as PER_UNIT after successful computation.

    annotations : Annotations
        May contain the ``base_kv`` parameter so it does not have to be specified.

    base_kv : float, default: None
        The Base KV of the stream for Per-Unit conversion. If None, the value is
        discovered from the annotations.

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations updated with the base_kv and stream type.
    """
    base_kv = base_kv or annotations.get("base_kv", None)
    if base_kv is None:
        raise ConduitValueError(
            "please specify the base_kv in the annotations "
            "or directly to the transformer"
        )

    # Determine the stream type
    stype = get_stream_type(tags, annotations)

    # Get the original units to determine the computation type
    units = tags[UNIT]

    # Update the annotations and the tags with the computation metadata
    annotations = annotations.update({MEASUREMENT_TYPE: stype, "base_kv": base_kv})
    tags = tags.update({UNIT: PER_UNIT})

    if stype == VOLTAGE_MAGNITUDE:
        if units == VOLTS_L_N:
            series = (series * SQRT_3 / (base_kv * 1000))
        elif units in {VOLTS_L_L, VPHM, VOLTS}:
            series = series / (base_kv * 1000)
        elif units == PER_UNIT:
            # Do nothing
            pass
        else:
            raise ConduitValueError(
                "could not convert voltage magnitude units '{}'".format(units)
            )

    elif stype == CURRENT_MAGNITUDE:
        # TODO: determine if users need to specify System Base MVA value.
        if units in {AMPS, IPHM}:
            series = series / (100000 / (base_kv * SQRT_3))
        elif units == PER_UNIT:
            # Do nothing
            pass
        else:
            raise ConduitValueError(
                "could not convert current magnitude units '{}'".format(units)
            )

    # Return the series, tags and annotations
    return series, tags, annotations


@transformer(VOLTAGE_MAGNITUDE)
def line_to_neutral(series, tags, annotations, base_kv=None):
    """Converts a voltage magnitude into Line-to-Neutral volts.

    Voltage magnitudes may begin as Per Unit, Line-to-Neutral or Line-to-Line.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as VOLTS_L_N after successful computation.

    annotations : Annotations
        May contain the ``base_kv`` parameter so it does not have to be specified.

    base_kv : float, default: None
        The Base KV of the stream for Per-Unit conversion. If None, the value is
        discovered from the annotations.

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations updated with the base_kv and stream type.
    """
    base_kv = base_kv or annotations.get("base_kv", None)
    if base_kv is None:
        raise ConduitValueError(
            "please specify the base_kv in the annotations "
            "or directly to the transformer"
        )

    # Get the original units to determine the computation type
    units = tags[UNIT]

    # Update the annotations and the tags with the computation metadata
    tags = tags.update({UNIT: VOLTS_L_N})
    annotations = annotations.update({
        MEASUREMENT_TYPE: VOLTAGE_MAGNITUDE, "base_kv": base_kv
    })

    if units == VOLTS_L_N:
        return series, tags, annotations

    if units in {VOLTS_L_L, VPHM, VOLTS}:
        return series / SQRT_3, tags, annotations

    if units == PER_UNIT:
        return ((series * base_kv * 1000) / SQRT_3), tags, annotations

    raise ConduitValueError(
        "could not convert voltage magnitude units '{}'".format(units)
    )


@transformer(VOLTAGE_MAGNITUDE)
def line_to_line(series, tags, annotations, base_kv=None):
    """Converts a voltage magnitude into Line-to-Line volts.

    Voltage magnitudes may begin as Per Unit, Line-to-Neutral or Line-to-Line.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as VOLTS_L_L after successful computation.

    annotations : Annotations
        May contain the ``base_kv`` parameter so it does not have to be specified.

    base_kv : float, default: None
        The Base KV of the stream for Per-Unit conversion. If None, the value is
        discovered from the annotations.

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations updated with the base_kv and stream type.
    """
    base_kv = base_kv or annotations.get("base_kv", None)
    if base_kv is None:
        raise ConduitValueError(
            "please specify the base_kv in the annotations "
            "or directly to the transformer"
        )

    # Get the original units to determine the computation type
    # TODO: do better than this
    units = tags[UNIT]

    # Update the annotations and the tags with the computation metadata
    tags = tags.update({UNIT: VOLTS_L_L})
    annotations = annotations.update({
        MEASUREMENT_TYPE: VOLTAGE_MAGNITUDE, "base_kv": base_kv
    })

    if units == VOLTS_L_N:
        return series * SQRT_3, tags, annotations

    if units in {VOLTS_L_L, VPHM, VOLTS}:
        return series, tags, annotations

    if units == PER_UNIT:
        return (series * base_kv * 1000), tags, annotations

    raise ConduitValueError(
        "could not convert voltage magnitude units '{}'".format(units)
    )


@transformer(CURRENT_MAGNITUDE)
def amps(series, tags, annotations, base_kv=None):
    """Converts a current magnitude from Per Unit into Amps.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as AMPS after successful computation.

    annotations : Annotations
        May contain the ``base_kv`` parameter so it does not have to be specified.

    base_kv : float, default: None
        The Base KV of the stream for Per-Unit conversion. If None, the value is
        discovered from the annotations.

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations updated with the base_kv and stream type.
    """
    base_kv = base_kv or annotations.get("base_kv", None)
    if base_kv is None:
        raise ConduitValueError(
            "please specify the base_kv in the annotations "
            "or directly to the transformer"
        )

    # Get the original units to determine the computation type
    # TODO: do better than this
    units = tags[UNIT]

    # Update the annotations and the tags with the computation metadata
    tags = tags.update({UNIT: AMPS})
    annotations = annotations.update({
        MEASUREMENT_TYPE: CURRENT_MAGNITUDE, "base_kv": base_kv
    })

    if units in {AMPS, IPHM}:
        return series, tags, annotations

    if units == PER_UNIT:
        return (series * (100000 / (base_kv * SQRT_3))), tags, annotations

    raise ConduitValueError(
        "could not convert current magnitude units '{}'".format(units)
    )


@transformer([VOLTAGE_MAGNITUDE, VOLTAGE_ANGLE, CURRENT_MAGNITUDE, CURRENT_ANGLE])
def calibrate(series, tags, annotations, rcf=None, pacf=None):
    """
    Calibrates phasor measurement components by applying a multiplicative correction
    (ratio correction factor - RCF) for phasor magnitudes and an additive correction
    factor (phase angle correction factor - PACF) to phasor angles.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams.

    annotations : Annotations
        May contain the ``rcf`` and ``pacf`` parameters so they do not have to be
        specified directly.

    rcf : float, default: None
        The Ratio Correction Factor, a multiplicative correction factor for phasor
        magnitudes. If None, the value is discovered from the annotations.

    pacf : float, default: None
        The Phase Angle Correction Factor, an additive correction factor for phasor
        angles. If None, the value is discovered from the annotations.

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations updated with the calibration factor and stream type.
    """
    # Determine the stream type
    stype = get_stream_type(tags, annotations)

    # Update the annotations and the tags with the computational metadata
    annotations = annotations.update({MEASUREMENT_TYPE: stype})

    if stype in {VOLTAGE_MAGNITUDE, CURRENT_MAGNITUDE}:
        rcf = rcf or annotations.get("rcf", None)
        if rcf is None:
            raise ConduitValueError(
                "please specify the rcf in the annotations or directly "
                "to the transformer to calibrate phasor magnitude"
            )

        # Update annotations with computational metadata
        annotations = annotations.update({"rcf": rcf})
        return (series * rcf), tags, annotations

    if stype in {VOLTAGE_ANGLE, CURRENT_ANGLE}:
        pacf = pacf or annotations.get("pacf", None)
        if pacf is None:
            raise ConduitValueError(
                "please specify the pacf in the annotations or directly "
                "to the transformer to calibrate phasor angle"
            )

        # Update annotations with computational metadata
        annotations = annotations.update({"pacf": pacf})

        if tags[UNIT] in {VPHA, IPHA, DEGREES}:
            rt = 180
            series = series + pacf
        elif tags[UNIT] == RADIANS:
            rt = PI
            series = series + (pacf * PI / 180.0)

        # TODO: is this the best way to modify the series?
        np.place(series.values, series > rt, series[series>rt]-rt)
        np.place(series.values, series < (-1 * rt), series[series<rt]+rt)

        return series, tags, annotations


@transformer([VOLTAGE_ANGLE, CURRENT_ANGLE])
def radians(series, tags, annotations):
    """Converts phasor angle into radians.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as RADIANS after successful computation.

    annotations : Annotations
        Annotations belonging to the stream

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations belonging to the stream
    """
    if tags[UNIT] in {DEGREES, IPHA, VPHA}:
        tags = tags.update({UNIT: RADIANS})
        return np.radians(series), tags, annotations

    if tags[UNIT] == RADIANS:
        return series, tags, annotations

    raise ConduitValueError(
        "could not convert phasor angle units '{}' to radians".format(tags[UNIT])
    )


@transformer([VOLTAGE_ANGLE, CURRENT_ANGLE])
def degrees(series, tags, annotations):
    """Converts phasor angle into degrees.

    Parameters
    ----------
    series : pd.Series
        The input stream for the transformation

    tags : Tags
        Tags must contain the unit of the streams, tags are updated with the
        new stream units as DEGREES after successful computation.

    annotations : Annotations
        Annotations belonging to the stream

    Returns
    -------
    series : pd.Series
        The output stream following the transformation

    tags : Tags
        Tags updated with the new units

    annotations : Annotations
        Annotations belonging to the stream
    """
    if tags[UNIT] in {DEGREES, IPHA, VPHA}:
        tags = tags.update({UNIT: DEGREES})
        return series, tags, annotations

    if tags[UNIT] == RADIANS:
        tags = tags.update({UNIT: DEGREES})
        return np.degrees(series), tags, annotations

    raise ConduitValueError(
        "could not convert phasor angle units '{}' to degrees".format(tags[UNIT])
    )
