"""
KomaPy processing engine.
"""

from collections import Callable

import numpy as np
import pandas as pd
from matplotlib import cm

from .exceptions import ChartError

__all__ = [
    'register_aggregation',
    'dataframe_from_dictionary',
    'empty_dataframe',
    'dataframe_or_empty',
    'read_csv',
    'read_excel',
    'get_rgb_color',
]

supported_aggregations = {
    'cumsum': 'cumsum',
    'add': 'add',
    'subtract': 'subtract',
    'multiply': 'multiply',
    'divide': 'divide',
    'power': 'power',

    'sub': 'subtract',
    'mul': 'multiply',
    'div': 'divide',
    'pow': 'power'
}


def register_aggregation(name, resolver):
    """
    Register data aggregation function.
    """
    if not isinstance(resolver, Callable):
        raise ChartError('Data aggregation resolver must be callable')

    if name in supported_aggregations:
        raise ChartError('Data aggregation name already exists')

    supported_aggregations[name] = resolver


def dataframe_from_dictionary(entry):
    """Create Pandas DataFrame from list of dictionary."""
    return pd.DataFrame(entry)


def empty_dataframe():
    """Create empty Pandas DataFrame."""
    return pd.DataFrame()


def dataframe_or_empty(data, name):
    """Get DataFrame column name or return empty DataFrame."""
    return data.get(name, empty_dataframe())


def read_csv(*args, **kwargs):
    """Read csv file."""
    return pd.read_csv(*args, **kwargs)


def read_excel(*args, **kwargs):
    """Read excel file."""
    return pd.read_excel(*args, **kwargs)


def get_rgb_color(num_sample, index, colormap='tab10'):
    """
    Get RGB color at current index for number of sample from matplotlib
    color map.
    """
    space = np.linspace(0, 1, num_sample)
    cmap = cm.get_cmap(colormap)
    return cmap(space[index])


def cumsum(data, params=None):
    """Cumulative sum function aggregation."""
    kwargs = params or {}
    return data.cumsum(**kwargs)


def add(data, params=None):
    """Add function aggregation."""
    kwargs = params or {}
    constant = kwargs.get('by', 0)
    return data + constant


def subtract(data, params=None):
    """Subtract function aggregation."""
    kwargs = params or {}
    constant = kwargs.get('by', 0)
    return data - constant


def multiply(data, params=None):
    """Multiply function aggregation."""
    kwargs = params or {}
    factor = kwargs.get('by', 1.0)
    return data * factor


def divide(data, params=None):
    """Divide function aggregation."""
    kwargs = params or {}
    factor = kwargs.get('by', 1.0)
    return data / factor


def power(data, params=None):
    """Power function aggregation."""
    kwargs = params or {}
    factor = kwargs.get('by', 1.0)
    return data ** factor
