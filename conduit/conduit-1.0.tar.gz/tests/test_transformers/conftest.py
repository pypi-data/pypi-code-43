# tests.test_transformers.conftest
# Provides pytest configuration and fixtures for the transformers tests.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Jun 25 16:47:59 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: conftest.py [] benjamin@bengfort.com $

"""
Provides pytest configuration and fixtures for the transformers tests.
"""

##########################################################################
## Imports
##########################################################################

import pytest
import pandas as pd

from conduit.meta import Tags, TagsGroup, Annotations, AnnotationsGroup


# 100 points of data
START = 1560513600000000000
END = 1560513603333332800


##########################################################################
## Single Stream Fixtures
##########################################################################

@pytest.fixture(scope='session')
def voltage_magnitude(db):
    stream = db.stream_from_uuid('0e044521-acb7-4121-9be9-3258095611fe')
    return make_transformer_arguments(stream)


@pytest.fixture(scope='session')
def voltage_angle(db):
    stream = db.stream_from_uuid('2713d533-6538-49b9-894d-0ab80150653d')
    return make_transformer_arguments(stream)


@pytest.fixture(scope='session')
def current_magnitude(db):
    stream = db.stream_from_uuid('f0fe1f63-864b-4c72-ae58-dc81c67c44ca')
    return make_transformer_arguments(stream)


@pytest.fixture(scope='session')
def current_angle(db):
    stream = db.stream_from_uuid('487bc2c4-1ca7-4def-9354-b32a3077db4e')
    return make_transformer_arguments(stream)


@pytest.fixture(scope='session')
def voltage_phasor(db):
    mag = db.stream_from_uuid('0e044521-acb7-4121-9be9-3258095611fe')
    ang = db.stream_from_uuid('2713d533-6538-49b9-894d-0ab80150653d')
    return make_composition_arguments(mag, ang)


@pytest.fixture(scope='session')
def current_phasor(db):
    mag = db.stream_from_uuid('f0fe1f63-864b-4c72-ae58-dc81c67c44ca')
    ang = db.stream_from_uuid('487bc2c4-1ca7-4def-9354-b32a3077db4e')
    return make_composition_arguments(mag, ang)


@pytest.fixture(scope='session')
def phase_b_phasor_pair(db):
    vmag = db.stream_from_uuid('0e044521-acb7-4121-9be9-3258095611fe')
    vang = db.stream_from_uuid('2713d533-6538-49b9-894d-0ab80150653d')
    imag = db.stream_from_uuid('f0fe1f63-864b-4c72-ae58-dc81c67c44ca')
    iang = db.stream_from_uuid('487bc2c4-1ca7-4def-9354-b32a3077db4e')
    return make_composition_arguments(vmag, imag, vang, iang)


@pytest.fixture(scope='session')
def voltage_phasor_group(db):
    amag = db.stream_from_uuid("847dc772-9253-44a8-b41e-c0974776727a")
    bmag = db.stream_from_uuid("0e044521-acb7-4121-9be9-3258095611fe")
    cmag = db.stream_from_uuid("b78e8def-ddff-4732-880e-b0d2342445b5")
    aang = db.stream_from_uuid("af80c527-b2ca-4b21-b656-64d11a0aa716")
    bang = db.stream_from_uuid("2713d533-6538-49b9-894d-0ab80150653d")
    cang = db.stream_from_uuid("473a0c1d-a415-4cf2-849b-98a4063d92bf")
    return make_composition_arguments(amag, bmag, cmag, aang, bang, cang)


##########################################################################
## Fixture Helpers
##########################################################################

def make_transformer_arguments(stream):
    times, values = [], []
    for point, _ in stream.values(start=START, end=END):
        times.append(point.time)
        values.append(point.value)
    data = pd.Series(values, index=times)

    annotations, _ = stream.annotations()
    return (data, Tags(stream.tags()), Annotations(annotations))


def make_composition_arguments(*streams):
    series, tags, annotations = [], [], []
    for stream in streams:
        args = make_transformer_arguments(stream)
        series.append(args[0])
        tags.append(args[1])
        annotations.append(args[2])

    data = pd.concat(series, axis=1)
    return data, TagsGroup(tags), AnnotationsGroup(annotations)