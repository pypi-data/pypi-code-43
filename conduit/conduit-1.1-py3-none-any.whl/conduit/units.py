# conduit.units
# Unit conversion transformer nodes.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Oct 15 10:53:18 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: units.py [] benjamin@bengfort.com $

"""
Unit conversion transformer nodes.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np
import pandas as pd

from conduit.flow import TransformerNode
from conduit.meta import get_stream_type
from conduit.exceptions import ConduitValueError
from conduit.meta import TagsGroup, AnnotationsGroup

from conduit.constants import IPHM, AMPS
from conduit.constants import UNIT, MEASUREMENT_TYPE
from conduit.constants import VPHM, VOLTS, VOLTS_L_L, VOLTS_L_N
from conduit.constants import PER_UNIT, VOLTAGE_MAGNITUDE, CURRENT_MAGNITUDE


class PerUnit(TransformerNode):
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
    base_kv : float, default: None
        The Base KV of the stream for Per-Unit conversion. If None, the value is
        discovered from the annotations.
    """

    def __init__(self, parents, base_kv=None):
        self.base_kv = base_kv
        super(PerUnit, self).__init__(parents)

    def tags(self):
        tags = super(PerUnit, self).tags()

        # TODO: Better type checking
        # TODO: Should we identify only the magnitude streams and update only those?
        # TODO: lift many/single functionality to the super class
        if isinstance(tags, TagsGroup):
            return tags.update_all({UNIT: PER_UNIT})
        return tags.update({UNIT: PER_UNIT})

    def annotations(self):
        tags = super(PerUnit, self).tags()
        meta = super(PerUnit, self).annotations()
        update = {"base_kv": self.base_kv} if self.base_kv is not None else {}

        # TODO: Better type checking
        # TODO: Should we identify only the magnitude streams and update only those?
        # TODO: lift many/single functionality to the super class
        if isinstance(meta, AnnotationsGroup):
            for idx in range(len(meta)):
                update[MEASUREMENT_TYPE] = get_stream_type(tags[idx], meta[idx])
                meta = meta.update(idx, update)
            return meta

        update[MEASUREMENT_TYPE] = get_stream_type(tags, meta)
        return meta.update(update)

    def transform(self, data):
        # Get input tags and annotations
        tags = super(PerUnit, self).tags()
        meta = super(PerUnit, self).annotations()

        # TODO: lift many/single functionality to the super class
        if isinstance(data, pd.DataFrame):
            return pd.concat([
                self._transform_single(data[column], tags[idx], meta[idx])
                for idx, column in enumerate(data.columns)
            ], axis=1)
        return self._transform_single(data, tags, meta)

    def _transform_single(self, series, tags, annotations):
        base_kv = self.base_kv or annotations.get("base_kv", None)
        if base_kv is None:
            raise ConduitValueError(
                "please specify the base_kv in the annotations "
                "or directly to the transformer"
            )

        units = tags[UNIT]
        stype = get_stream_type(tags, annotations)

        if stype == VOLTAGE_MAGNITUDE:
            if units == VOLTS_L_N:
                return (series * np.sqrt(3) / (base_kv * 1000))
            elif units in {VOLTS_L_L, VPHM, VOLTS}:
                return series / (base_kv * 1000)
            elif units == PER_UNIT:
                return series
            else:
                raise ConduitValueError(
                    "could not convert voltage magnitude units '{}'".format(units)
                )

        if stype == CURRENT_MAGNITUDE:
            # TODO: determine if users need to specify System Base MVA value.
            if units in {AMPS, IPHM}:
                return series / (100000 / (base_kv * np.sqrt(3)))
            elif units == PER_UNIT:
                return series
            else:
                raise ConduitValueError(
                    "could not convert current magnitude units '{}'".format(units)
                )

        raise ConduitValueError("unhandled stream type '{}'".format(stype))

    def __str__(self):
        if self.base_kv is not None:
            return "per-unit (base kV={})".format(self.base_kv)
        return "per-unit"

    def __repr__(self):
        if self.base_kv is not None:
            return "<PerUnit (base kV={})>".format(self.base_kv)
        return "<PerUnit>"