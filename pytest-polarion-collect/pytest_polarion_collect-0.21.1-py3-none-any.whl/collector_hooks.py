"""Pytest plugin for populating items with polarion test cases data."""

import pytest

from pytest_polarion_collect import utils

# pylint: disable=protected-access,import-outside-toplevel


class MetadataCollectorHooks:
    @pytest.hookimpl
    @staticmethod
    def pytest_collect_polarion_metadata(session, items):
        """Implementat hook that appends parsed metadata to items."""
        utils.set_cache(session)

        for item in items:
            if not utils.in_test_dir(str(item.fspath), session._test_dirs_cache):
                continue

            utils.get_testcase_data(item, session._docstrings_cache)


def pytest_addhooks(pluginmanager):
    """Register the hook with pytest."""
    from pytest_polarion_collect import hookspec

    pluginmanager.add_hookspecs(hookspec)
    pluginmanager.register(MetadataCollectorHooks)
