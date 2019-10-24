"""Hook spec."""
import pytest


@pytest.hookspec
# pylint: disable=unused-argument
def pytest_collect_polarion_metadata(session, items):
    """Implement hook that appends parsed metadata to items."""
