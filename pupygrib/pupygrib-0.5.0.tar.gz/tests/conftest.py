"""Test fixtures for pupygrib."""

import io
import itertools
from operator import itemgetter
from os import path

import numpy
from pkg_resources import resource_filename, resource_stream
import pytest

import pupygrib


@pytest.fixture(scope="module")
def message(request):
    with resource_stream(__name__, request.module.gribfile) as stream:
        message = next(pupygrib.read(stream))
    return message


@pytest.fixture(scope="class")
def section(request, message):
    return message[request.cls.section_number]


@pytest.fixture(scope="module")
def target_field(request):
    def _iterrows(lines):
        rows = (line.split() for line in lines)
        for lat, subrows in itertools.groupby(rows, itemgetter(0)):
            yield zip(*(map(float, row) for row in subrows))

    datafile = path.extsep.join([request.module.gribfile, "values"])
    with io.open(resource_filename(__name__, datafile)) as stream:
        assert next(stream).strip() == "Latitude, Longitude, Value"
        lats, lons, values = map(numpy.vstack, zip(*_iterrows(stream)))
    return lons, lats, values


@pytest.fixture(scope="module")
def target_longitudes(target_field):
    return target_field[0]


@pytest.fixture(scope="module")
def target_latitudes(target_field):
    return target_field[1]


@pytest.fixture(scope="module")
def target_values(target_field):
    return target_field[2]
