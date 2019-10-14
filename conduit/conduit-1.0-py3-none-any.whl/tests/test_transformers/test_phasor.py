# tests.test_transformers.test_phasor
# Test the phasor transformers package
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Thu Oct 10 10:09:13 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_phasor.py [] benjamin@bengfort.com $

"""
Test the phasor transformers package
"""

##########################################################################
## Imports
##########################################################################

import pytest
import pandas as pd

from conduit.meta import *
from conduit.constants import *
from conduit.transformers.phasor import *


class TestPhasor(object):
    """
    Test the phasor and phasor group/pair compositions
    """

    def test_real_phasor(self, voltage_phasor):
        """
        Test the real component phasor composition
        """
        series, tags, annotations = real(*voltage_phasor)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(voltage_phasor[0])

        assert tags[UNIT] == VPHM
        assert annotations[MEASUREMENT_TYPE] == REAL_PHASOR_COMPONENT

    def test_imaginary_phasor(self, current_phasor):
        """
        Test the imaginary component phasor composition
        """
        series, tags, annotations = imaginary(*current_phasor)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(current_phasor[0])

        assert tags[UNIT] == IPHM
        assert annotations[MEASUREMENT_TYPE] == IMAGINARY_PHASOR_COMPONENT

    def test_complex_phasor(self, voltage_phasor):
        """
        Test the complex component phasor composition
        """
        series, tags, annotations = complex_phasor(*voltage_phasor)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(voltage_phasor[0])
        assert series.dtype == np.complex128

        assert tags[UNIT] == VPHM
        assert annotations[MEASUREMENT_TYPE] == COMPLEX_PHASOR

    def test_complex_power(self, phase_b_phasor_pair):
        """
        Test the complex power phasor pair composition
        """
        series, tags, annotations = complex_power(*phase_b_phasor_pair)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(phase_b_phasor_pair[0])
        assert series.dtype == np.complex128

        assert tags[UNIT] == P_JQ
        assert annotations[MEASUREMENT_TYPE] == COMPLEX_POWER

    def test_real_power(self, phase_b_phasor_pair):
        """
        Test the real power phasor pair composition
        """
        series, tags, annotations = real_power(*phase_b_phasor_pair)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(phase_b_phasor_pair[0])
        assert series.dtype == np.float64

        assert tags[UNIT] == MW
        assert annotations[MEASUREMENT_TYPE] == REAL_POWER

    def test_reactive_power(self, phase_b_phasor_pair):
        """
        Test the reactive power phasor pair composition
        """
        series, tags, annotations = reactive_power(*phase_b_phasor_pair)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(phase_b_phasor_pair[0])
        assert series.dtype == np.float64

        assert tags[UNIT] == MVAR
        assert annotations[MEASUREMENT_TYPE] == REACTIVE_POWER

    def test_apparent_power(self, phase_b_phasor_pair):
        """
        Test the apparent power phasor pair composition
        """
        series, tags, annotations = apparent_power(*phase_b_phasor_pair)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(phase_b_phasor_pair[0])
        assert series.dtype == np.float64

        assert tags[UNIT] == MVA
        assert annotations[MEASUREMENT_TYPE] == APPARENT_POWER

    def test_power_factor(self, phase_b_phasor_pair):
        """
        Test the power factor phasor pair composition
        """
        series, tags, annotations = power_factor(*phase_b_phasor_pair)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(phase_b_phasor_pair[0])
        assert series.dtype == np.float64

        assert tags[UNIT] == PER_UNIT
        assert annotations[MEASUREMENT_TYPE] == POWER_FACTOR

    def test_complex_phasor_group(self, voltage_phasor_group):
        """
        Test the complex phasor group composition
        """
        df, tags, annotations = complex_phasor_group(*voltage_phasor_group)

        assert isinstance(df, pd.DataFrame)
        assert isinstance(tags, TagsGroup)
        assert isinstance(annotations, AnnotationsGroup)

        assert len(df) == len(voltage_phasor_group[0])
        assert np.all(df.dtypes == np.complex128)

        assert len(tags) == df.shape[1]
        assert len(annotations) == df.shape[1]

        assert set(tags.units()) == {VPHM}
        assert set(annotations.measurement_types()) == {COMPLEX_PHASOR}

    def test_sequence_components(self, voltage_phasor_group):
        """
        Test the complex phasor group composition
        """
        df, tags, annotations = sequence_components(*voltage_phasor_group)

        assert isinstance(df, pd.DataFrame)
        assert isinstance(tags, TagsGroup)
        assert isinstance(annotations, AnnotationsGroup)

        assert len(df) == len(voltage_phasor_group[0])
        assert np.all(df.dtypes == np.complex128)

        assert df.shape[1] == 3
        assert len(tags) == df.shape[1]
        assert len(annotations) == df.shape[1]

        assert set(tags.units()) == {VPHM}
        assert annotations.measurement_types() == [ZERO_SEQ, POS_SEQ, NEG_SEQ]

    def test_zero_sequence(self, voltage_phasor_group):
        """
        Test the zero sequence phasor group composition
        """
        series, tags, annotations = zero_sequence(*voltage_phasor_group)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(voltage_phasor_group[0])
        assert series.dtype == np.complex128

        assert tags[UNIT] == VPHM
        assert annotations[MEASUREMENT_TYPE] == ZERO_SEQ

    def test_positive_sequence(self, voltage_phasor_group):
        """
        Test the positive sequence phasor group composition
        """
        series, tags, annotations = positive_sequence(*voltage_phasor_group)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(voltage_phasor_group[0])
        assert series.dtype == np.complex128

        assert tags[UNIT] == VPHM
        assert annotations[MEASUREMENT_TYPE] == POS_SEQ

    def test_negative_sequence(self, voltage_phasor_group):
        """
        Test the negative sequence phasor group composition
        """
        series, tags, annotations = negative_sequence(*voltage_phasor_group)

        assert isinstance(series, pd.Series)
        assert isinstance(tags, Tags)
        assert isinstance(annotations, Annotations)

        assert len(series) == len(voltage_phasor_group[0])
        assert series.dtype == np.complex128

        assert tags[UNIT] == VPHM
        assert annotations[MEASUREMENT_TYPE] == NEG_SEQ

    @pytest.mark.xfail(reason="three phase power computations not implemented")
    def test_three_phase_mw(self):
        pass

    @pytest.mark.xfail(reason="three phase power computations not implemented")
    def test_three_phase_mvar(self):
        pass

    @pytest.mark.xfail(reason="three phase power computations not implemented")
    def test_three_phase_mva(self):
        pass

    @pytest.mark.xfail(reason="three phase power computations not implemented")
    def test_three_phase_complex_power(self):
        pass

    @pytest.mark.xfail(reason="three phase power computations not implemented")
    def test_three_phase_powerfactor(self):
        pass