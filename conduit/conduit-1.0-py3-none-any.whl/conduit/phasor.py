# conduit.phasor
# Phasor conduits for various stream computations.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Thu Jun 27 21:34:40 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: phasor.py [] benjamin@bengfort.com $

"""
Phasor conduits for various stream computations.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np
import pandas as pd

from .base import Conduit
from .constants import UNIT
from .constants import ALPHA, ALPHA_2
from .constants import IPHA, IPHM, VPHA, VPHM
from .exceptions import ValidationError, ConduitValueError


##########################################################################
## Phasor
##########################################################################

class Phasor(Conduit):
    """
    A Phasor consists of two streams, a voltage and an angle pair. These
    streams must have the same units, e.g. voltage or current.

    # TODO: Handle different unit types, e.g. degrees vs. radians
    # This currently expects streams in degrees
    """

    def __init__(self, *streams):
        if len(streams) != 2:
            raise ValidationError("a phasor is composed of exactly two streams")

        units = {s.tags()[UNIT] for s in streams}
        if units != {IPHA, IPHM} and units != {VPHA, VPHM}:
            raise ValidationError(
                "phasor must consist of either voltage or current angle and magnitude"
            )

        self._units = {
            "ANG": [u for u in units if u.endswith("A")][0],
            "MAG": [u for u in units if u.endswith("M")][0],
        }

        # TODO: should we validate phase on init?
        super(Phasor, self).__init__(*streams)

    @property
    def phase(self):
        """
        Returns the phase attribute of the annotations, raising an
        exception if the two streams are in different phases.
        """
        # TODO: should we filter out streams with no phase metadata?
        # e.g. if one stream has a phase and the other doesn't, use that phase?
        phases = {
            meta['annotations'].get('phase', None)
            for meta in self.metadata()
        }

        if len(phases) != 1:
            raise ConduitValueError("stream annotations did not contain a single phase")
        return phases.pop()

    def values_poc(self, start, end, datetime64_index=True):
        """
        Returns a DataFrame with unit headers
        """
        data = []
        for idx, stream in enumerate(self):
            times, values = [], []
            for point, _ in stream.values(start, end, version=0):
                times.append(point.time)
                values.append(point.value)

            series = self._apply_stream_transformations(
                idx, stream, times, values, datetime64_index=datetime64_index
            )
            series.name = stream.tags()[UNIT]
            data.append(series)

        return pd.concat(data, axis=1)

    def real_poc(self, start, end, datetime64_index=True):
        df = self.values_poc(start, end, datetime64_index=datetime64_index)
        ang = df[self._units["ANG"]]
        mag = df[self._units["MAG"]]

        r = (mag * np.cos(np.radians(ang)))
        return pd.Series(r, index=df.index, name="Real Phase {}".format(self.phase))

    def imaginary_poc(self, start, end, datetime64_index=True):
        df = self.values_poc(start, end, datetime64_index=datetime64_index)
        ang = df[self._units["ANG"]]
        mag = df[self._units["MAG"]]

        i =  (mag * np.sin(np.radians(ang)))
        return pd.Series(i, index=df.index, name="Imaginary Phase {}".format(self.phase))

    def complex_poc(self, start, end, datetime64_index=True):
        """
        Returns a Series with complex values
        """
        df = self.values_poc(start, end, datetime64_index=datetime64_index)
        ang = df[self._units["ANG"]]
        mag = df[self._units["MAG"]]

        r = (mag * np.cos(np.radians(ang))) # compute the real component
        i = (mag * np.sin(np.radians(ang))) # compute the imaginary component

        # simplest way to create a complex numpy array is r + 1j * i
        return pd.Series(r + 1j * i, index=df.index, name="Complex Phase {}".format(self.phase))

    def __str__(self):
        s0u, s1u = (s.tags()[UNIT] for s in self)
        return "{}/{} Phase {}".format(s0u, s1u, self.phase)


class PhasorGroup(Conduit):
    """
    A PhasorGroup consists of an even number of streams, phasors
    for either voltage or current. The phasor must have the same
    units (e.g. either voltage or current).
    """

    def __init__(self, *streams):
        if len(streams) % 2 != 0:
            raise ValidationError("a phasor group must have an even number of streams")

        units = {s.tags()[UNIT] for s in streams}
        if units != {IPHA, IPHM} and units != {VPHA, VPHM}:
            raise ValidationError(
                "phasor group must consist of either voltage or current angle and magnitude"
            )

        # TODO: raise a validation error if pairs do not exist
        super(PhasorGroup, self).__init__(*streams)

    @property
    def phases(self):
        phases = {
            meta['annotations'].get('phase', None)
            for meta in self.metadata()
        }
        return sorted(list(phases))

    def phasors(self):
        """
        Returns all the phasors in the PhasorGroup
        """
        for phase in self.phases:
            yield Phasor(*self.subset(self.phase_mask(phase)))

    def values_poc(self, start, end, datetime64_index=True):
        """
        Returns a DataFrame with a heirarchical index
        """
        dfs = [
            phasor.values_poc(start, end, datetime64_index=datetime64_index)
            for phasor in self.phasors()
        ]

        keys = ["Phase {}".format(phase) for phase in self.phases]
        return pd.concat(dfs, axis=1, keys=keys)

    def complex_poc(self, start, end, datetime64_index=True):
        """
        Returns a data frame with complex values for each phase
        """
        dfs = [
            phasor.complex_poc(start, end, datetime64_index=datetime64_index)
            for phasor in self.phasors()
        ]
        return pd.concat(dfs, axis=1)

    def zero_sequence_poc(self, start, end, datetime64_index=True):
        df = self.complex_poc(start, end, datetime64_index=datetime64_index)
        A = df["Complex Phase A"]
        B = df["Complex Phase B"]
        C = df["Complex Phase C"]

        return (A + B + C) / 3

    def positive_sequence_poc(self, start, end, datetime64_index=True):
        df = self.complex_poc(start, end, datetime64_index=datetime64_index)
        A = df["Complex Phase A"]
        B = df["Complex Phase B"]
        C = df["Complex Phase C"]

        return (A + B * ALPHA + C * ALPHA_2) / 3

    def negative_sequence_poc(self, start, end, datetime64_index=True):
        df = self.complex_poc(start, end, datetime64_index=datetime64_index)
        A = df["Complex Phase A"]
        B = df["Complex Phase B"]
        C = df["Complex Phase C"]

        return (A + B * ALPHA_2 + C * ALPHA) / 3

    def sequence_components_poc(self, start, end, datetime64_index=True):
        """
        Returns a DataFrame with the symmetrical components, a proof of concept.
        """
        df = self.complex_poc(start, end, datetime64_index=datetime64_index)
        A = df["Complex Phase A"]
        B = df["Complex Phase B"]
        C = df["Complex Phase C"]

        zero = (A + B + C) / 3
        pos = (A + B * ALPHA + C * ALPHA_2) / 3
        neg = (A + B * ALPHA_2 + C * ALPHA) / 3

        keys = ["Negative", "Zero", "Positive"]
        return pd.concat([neg, zero, pos], axis=1, keys=keys)


class PhasorPair(Conduit):
    """
    A phasor pair contains the voltage and current phasors for a specific phase.
    """

    def __init__(self, *streams):
        if len(streams) != 4:
            raise ValidationError("a phasor pair is composed of exactly four streams")

        units = {s.tags()[UNIT] for s in streams}
        if units != {IPHA, VPHA, IPHM, VPHM}:
            raise ValidationError(
                "phasor pair must consist of both voltage and current phasors"
            )

        # TODO: should we validate phase on init?
        super(PhasorPair, self).__init__(*streams)

    @property
    def phase(self):
        """
        Returns the phase attribute of the annotations, raising an
        exception if the two streams are in different phases.
        """
        # TODO: hoist this shared functionality between phasor and PhasorPair
        # TODO: should we filter out streams with no phase metadata?
        # e.g. if one stream has a phase and the other doesn't, use that phase?
        phases = {
            meta['annotations'].get('phase', None)
            for meta in self.metadata()
        }

        if len(phases) != 1:
            raise ConduitValueError("stream annotations did not contain a single phase")
        return phases.pop()

    def phasors(self):
        """
        Yields the voltage and current phasors
        """
        yield Phasor(*self.subset(self.unit_mask("VPHA", "VPHM")))
        yield Phasor(*self.subset(self.unit_mask("IPHA", "IPHM")))

    def complex_power_poc(self, start, end, datetime64_index=True):
        """
        Computes the complex power (P + jQ)
        """
        vph, iph = self.phasors()
        vph = vph.complex_poc(start, end, datetime64_index=datetime64_index)
        iph = iph.complex_poc(start, end, datetime64_index=datetime64_index)
        cp = vph * np.conjugate(iph)
        cp.name = "complex power"
        return cp

    def real_power_poc(self, start, end, datetime64_index=True):
        cp = self.complex_power_poc(start, end, datetime64_index=datetime64_index)
        return pd.Series(cp.real, index=cp.index, name="real power")

    def reactive_power_poc(self, start, end, datetime64_index=True):
        cp = self.complex_power_poc(start, end, datetime64_index=datetime64_index)
        return pd.Series(cp.imag, index=cp.index, name="reactive power")

    def apparent_power_poc(self, start, end, datetime64_index=True):
        cp = self.complex_power_poc(start, end, datetime64_index=datetime64_index)
        return pd.Series(np.abs(cp), index=cp.index, name="apparent power")

    def power_factor_poc(self, start, end, datetime64_index=True):
        cp = self.complex_power_poc(start, end, datetime64_index=datetime64_index)
        return pd.Series(cp.real / np.abs(cp), index=cp.index, name="power factor")


class PhasorPairGroup(Conduit):
    """
    A PhasorPairGrup must have an even number of streams, PhasorPairs for each phase.
    """

    def __init__(self, *streams):
        if len(streams) % 4 != 0:
            raise ValidationError(
                "a phasor pair group must have sets of four streams"
            )

        units = {s.tags()[UNIT] for s in streams}
        if units != {IPHA, VPHA, IPHM, VPHM}:
            raise ValidationError(
                "phasor pair must consist of both voltage and current phasors"
            )

        super(PhasorPairGroup, self).__init__(*streams)

    @property
    def phases(self):
        phases = {
            meta['annotations'].get('phase', None)
            for meta in self.metadata()
        }
        return sorted(list(phases))

    def phasor_pairs(self):
        """
        Returns all the phasor pairs in the PhasorPairGroup
        """
        for phase in self.phases:
            yield PhasorPair(*self.subset(self.phase_mask(phase)))

    def complex_power_poc(self, start, end, datetime64_index=True):
        """
        Computes the complex power (P + jQ) summed across all phases
        """
        cp = pd.concat([
            pp.complex_power_poc(start, end, datetime64_index=datetime64_index)
            for pp in self.phasor_pairs()
        ], axis=1).sum(axis=1)

        cp.name = "complex power"
        return cp

    def real_power_poc(self, start, end, datetime64_index=True):
        cp = pd.concat([
            pp.real_power_poc(start, end, datetime64_index=datetime64_index)
            for pp in self.phasor_pairs()
        ], axis=1).sum(axis=1)

        cp.name = "real power"
        return cp

    def reactive_power_poc(self, start, end, datetime64_index=True):
        cp = pd.concat([
            pp.reactive_power_poc(start, end, datetime64_index=datetime64_index)
            for pp in self.phasor_pairs()
        ], axis=1).sum(axis=1)

        cp.name = "reactive power"
        return cp

    def apparent_power_poc(self, start, end, datetime64_index=True):
        cp = pd.concat([
            pp.apparent_power_poc(start, end, datetime64_index=datetime64_index)
            for pp in self.phasor_pairs()
        ], axis=1).sum(axis=1)

        cp.name = "apparent power"
        return cp

    def power_factor_poc(self, start, end, datetime64_index=True):
        cp = pd.concat([
            pp.power_factor_poc(start, end, datetime64_index=datetime64_index)
            for pp in self.phasor_pairs()
        ], axis=1).sum(axis=1)

        cp.name = "power factor"
        return cp