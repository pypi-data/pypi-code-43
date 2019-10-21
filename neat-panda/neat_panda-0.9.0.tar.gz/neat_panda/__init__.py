# -*- coding: utf-8 -*-

"""Top-level package for Neat Panda."""

__author__ = """Henric Sundberg"""
__email__ = "henric.sundberg@gmail.com"
__version__ = "0.9.0"

from ._tidy import spread, gather
from ._caretaker import clean_column_names, _clean_column_names
from ._set_operations import difference, intersection, symmmetric_difference, union
from ._helpers import _get_version_from_toml
