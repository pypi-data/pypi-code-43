# -*- coding: utf-8 -*-

import pickle

import pytest


@pytest.fixture(scope="session")
def reporting(request):
    rs = request.config._reportingsession

    # We are in xdist
    if hasattr(request.config, "slaveoutput"):

        def pickle_reportingsession():
            request.config.slaveoutput["_reportingsession"] = pickle.dumps(rs)

        request.addfinalizer(pickle_reportingsession)

    return rs
