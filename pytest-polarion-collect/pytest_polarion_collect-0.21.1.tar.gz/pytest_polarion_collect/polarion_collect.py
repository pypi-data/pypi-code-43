"""Pytest plugin for collecting polarion test cases data."""

import json
import pytest

from pytest_polarion_collect import utils

# pylint: disable=protected-access


def pytest_addoption(parser):
    """Add command line options."""
    group = parser.getgroup("Polarion: options related to test cases data collection")
    group.addoption(
        "--generate-json",
        action="store_true",
        default=False,
        help="generate JSON file with tests data",
    )
    group.addoption(
        "--meta-filter",
        type=json.loads,
        help="only run tests with the given meta (JSON) matches in polarion metadata",
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(session, config, items):
    """Generate testcase JSON file in collection only mode, or modify nodes based on meta filter."""
    # prevent on slave nodes (xdist)
    if hasattr(config, "slaveinput"):
        return

    gen_json = config.getoption("generate_json")
    collect = config.getoption("collectonly")
    metafilters = config.getoption("meta_filter")

    utils.set_cache(session)

    if metafilters:
        keep, discard = [], []
        # Apply any meta filters and discard cases
        # Not a great pattern, pytest issues #1372 and #1373
        for item in items:
            if not utils.in_test_dir(str(item.fspath), session._test_dirs_cache):
                continue
            if not utils.meta_matches(session, item, metafilters):
                # filter did not match item meta, discard the item
                discard.append(item)
                continue
            keep.append(item)

        # modify items list with kept functions
        items[:] = keep
        config.hook.pytest_deselected(items=discard)
        # make the number of tests uncollected by the filter available
        session._uncollected_meta_filter = len(discard)

    if gen_json and collect:
        utils.process_json_data(session, items)
