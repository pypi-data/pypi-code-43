"""
Implementation of the command-line I{pyflakes} tool.
"""
from __future__ import absolute_import

# For backward compatibility
__all__ = ['check', 'checkPath', 'checkRecursive', 'iterSourceCode', 'build_file']
from pyflakes.api import check, checkPath, checkRecursive, iterSourceCode, build_file
