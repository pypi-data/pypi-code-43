# -*- coding: utf-8 -*-
"""compatibleversion module.

This module determines if a version is permitted by a specifier.
"""

from packaging.specifiers import SpecifierSet
from packaging.version import Version


__version__ = "0.1.2"


def check_version(version, specifier):
    """Check version against specifier to see if version is specified."""
    if not version or not specifier:
        print("Must provide a value for version and specifier")
        raise ValueError

    version_obj = Version(version)
    specifier_obj = SpecifierSet(specifier)

    if list(specifier_obj.filter([version_obj])):
        return True

    return False
