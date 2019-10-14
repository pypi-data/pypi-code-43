"""
KomaPy data transforms module.
"""

from collections import Callable

import pandas as pd

from .client import fetch_bma_as_dataframe
from .exceptions import ChartError

__all__ = [
    'register_transform',
]

transform_registers = {
    'slope_correction': 'slope_correction',
}


def register_transform(name, resolver):
    """
    Register data transform function.
    """
    if not isinstance(resolver, Callable):
        raise ChartError('Data transform resolver must be callable')

    if name in transform_registers:
        raise ChartError('Data transform name already exists')

    transform_registers[name] = resolver


def slope_correction(data, config):
    """
    Apply EDM slope distance correction.
    """
    if config.name != 'edm':
        return data

    timestamp__gte = config.query_params.get(
        'timestamp__gte') or config.query_params.get('start_at')
    timestamp__lt = config.query_params.get(
        'timestamp__lt') or config.query_params.get('end_at')

    err_data = fetch_bma_as_dataframe('slope', **{
        'timestamp__gte': timestamp__gte,
        'timestamp__lt': timestamp__lt,
        'benchmark': config.query_params['benchmark'],
        'reflector': config.query_params['reflector'],
    })
    if err_data.empty:
        return data

    slope_data = pd.DataFrame()
    slope_data['timestamp'] = data[0]
    slope_data['slope_distance'] = data[1]

    corrected_data = slope_data.apply(
        lambda item: item.slope_distance + err_data.where(
            err_data.timestamp > item.timestamp).deviation.sum(), axis=1)
    return [data[0], corrected_data]
