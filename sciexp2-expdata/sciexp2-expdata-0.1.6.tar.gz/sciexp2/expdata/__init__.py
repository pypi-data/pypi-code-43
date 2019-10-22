#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SciExp²-ExpData provides helper functions for easing the workflow of
analyzing the many data output files produced by experiments. The helper
functions simply aggregate the many per-experiment files into a single data
structure that contains all the experiment results with appropriate metadata to
identify each of the experiment results (e.g., using a pandas data frame).

It works best in combination with SciExp²-ExpDef, which can be used to define
many experiments based on parameter permutations.

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


__version_info__ = (0, 1, 6)
__version__ = ".".join([str(i) for i in __version_info__])


from sciexp2.expdata import pandas


__all__ = [
    "pandas",
]
