# conduit.constants
# Important package constants and variables for computation and meta data.
#
# Author:   Kevin D. Jones <kdjones@users.noreply.github.com>
# Created:  Wed May 29 17:55:38 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: constants.py [] kdjones@users.noreply.github.com $

"""
Important package constants and variables for computation and meta data.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np


##########################################################################
## Default Computational Parameters
##########################################################################

DEFAULT_RCF  = 1.0
DEFAULT_PACF = 0.0
SQRT_3 = np.sqrt(3)
PI = np.pi

# Alpha and Alpha Squared are used in Symmetrical Components computation
ALPHA = np.complex(np.cos(np.radians(120)), np.sin(np.radians(120)))
ALPHA_2 = np.complex(np.cos(np.radians(240)), np.sin(np.radians(240)))

##########################################################################
## Metadata String Constants
## TODO: Convert to Enum types
##########################################################################

# Tags fields
INGRESS = 'ingress'
NAME = 'name'
UNIT = 'unit'

# All tag fields
TAG_FIELDS = [INGRESS, NAME, UNIT]

# Annotations fields
# Ingress related fields
ACRONYM = 'acronym'
DESCRIPTION = 'description'
DEVACRONYM = 'devacronym'
DEVICE = 'device'
ENABLED = 'enabled'
ID = 'id'
INTERNAL = 'internal'
LABEL = 'label'
REFERENCE = 'reference'
TYPE = 'type'

# Conduit related fields
BASE_KV = 'base_kv'
MEASUREMENT_TYPE = 'measurement_type'
RCF = 'rcf'
PACF = 'pacf'
PHASE = 'phase'
PHASOR_ID = 'phasor_id'
PHASOR_GROUP_ID = 'phasor_group_id'
STATUSFLAG_ID = 'statusflag_id'
VARIANCE = 'variance'

# All annotation fields
ANNOTATION_FIELDS = [
    ACRONYM, DESCRIPTION, DEVACRONYM, DEVICE, ENABLED, ID, INTERNAL, LABEL, REFERENCE,
    TYPE, BASE_KV, MEASUREMENT_TYPE, RCF, PACF, PHASE, PHASOR_ID, PHASOR_GROUP_ID,
    STATUSFLAG_ID, VARIANCE,
]

# Units
# TODO: Create unit to stream type conversions
AMPS = 'Amps'
ANALOG = 'Analog'
DEGREES = 'Degrees'
DFDT = 'DFDT'
DIGI = 'DIGI'
DIGITAL = 'Digital'
FLAGS = 'StatusFlags'
FREQ = 'FREQ'
HZ = 'Hz'
IPHA = 'IPHA'
IPHM = 'IPHM'
MVA = 'MVA'
MVAR = 'MVAR'
MW = 'MW'
PER_UNIT = 'Per Unit'
P_JQ = 'MW + jMVAR'
RADIANS = 'Radians'
UNITLESS = 'Unit-less'
VOLTS = 'Volts'
VOLTS_L_N = 'Voltage Line-to-Neutral'
VOLTS_L_L = 'Voltage Line-to-Line'
VPHA = 'VPHA'
VPHM = 'VPHM'

# All unit definitions
UNITS = [
    AMPS, ANALOG, DEGREES, DFDT, DIGI, DIGITAL, FLAGS, FREQ, HZ, IPHA, IPHM, MVA, MVAR,
    MW, PER_UNIT, P_JQ, RADIANS, UNITLESS, VOLTS, VOLTS_L_L, VOLTS_L_N, VPHA, VPHM,
]

# Measurement Types
ANALOG_VALUE = 'Analog'
CURRENT_ANGLE = 'Current Angle'
CURRENT_MAGNITUDE = 'Current Magnitude'
DIGITAL_WORD = 'Digital'
FREQUENCY = 'Frequency'
ROCOF = 'DfDt'
STATUSFLAGS = 'Status Flags'
VOLTAGE_ANGLE = 'Voltage Angle'
VOLTAGE_MAGNITUDE = 'Voltage Magnitude'

MEASUREMENT_TYPES = [
    ANALOG_VALUE, CURRENT_ANGLE, CURRENT_MAGNITUDE, DIGITAL_WORD, FREQUENCY, ROCOF,
    STATUSFLAGS, VOLTAGE_ANGLE, VOLTAGE_MAGNITUDE,
]

# Calculated Stream Types
APPARENT_POWER = 'Apparent Power'
COMPLEX_PHASOR = 'Phasor (Complex)'
COMPLEX_POWER = 'Complex Power'
IMAGINARY_PHASOR_COMPONENT = 'Phasor (Imag)'
POWER_FACTOR = 'Power Factor'
REACTIVE_POWER = 'Reactive Power'
REAL_PHASOR_COMPONENT = 'Phasor (Real)'
REAL_POWER = 'Real Power'

CALCULATED_STREAM_TYPES = [
    APPARENT_POWER, COMPLEX_PHASOR, COMPLEX_POWER, IMAGINARY_PHASOR_COMPONENT,
    POWER_FACTOR, REACTIVE_POWER, REAL_PHASOR_COMPONENT, REAL_POWER,
]

# Phases
PHASE_A = 'A'
PHASE_B = 'B'
PHASE_C = 'C'
POS_SEQ = '1'
NEG_SEQ = '2'
ZERO_SEQ = '0'

PHASES = [
    PHASE_A, PHASE_B, PHASE_C,
    POS_SEQ, NEG_SEQ, ZERO_SEQ,
]

# Stream to Unit Mappings
# TODO: Generalize this function
STREAM_TO_UNIT = {
    ANALOG_VALUE: {ANALOG},
    CURRENT_ANGLE: {IPHA, DEGREES, RADIANS},
    CURRENT_MAGNITUDE: {IPHM, AMPS},
    DIGITAL_WORD: {DIGI, DIGITAL},
    FREQUENCY: {FREQ, HZ},
    ROCOF: {DFDT},
    STATUSFLAGS: {FLAGS},
    VOLTAGE_ANGLE: {VPHA, DEGREES, RADIANS},
    VOLTAGE_MAGNITUDE: {VPHM, VOLTS, VOLTS_L_L, VOLTS_L_N},
}
