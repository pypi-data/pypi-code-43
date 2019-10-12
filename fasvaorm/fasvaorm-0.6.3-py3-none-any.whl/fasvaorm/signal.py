# -*- tab-width: 4; encoding: utf-8; -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger, String, Text, Float, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import get_class_by_table

from fasvaorm.models import SignalAggregatedBaseModel, signal_table_name, SignalBaseModel

__all__ = [
    'get_class_by_table',
    'get_signal_table'
]

DB_TYPE_MAP = {
    int: "integer",
    float: "double precision",
    str: "text",
    list: "text",
    bool: "boolean",
    datetime: "datetime(6)",
    None: float
}

RECORD_TYPE_MAP = {
    'double': float,
    'bool': bool,
    'string': str,
    'binary': str,
    'uint8_t': int,
    'float_t': float,
    'uint16_t': int,
    'uint32_t': int

}

Base = declarative_base()


class BigIntegerSignalMixin(object):
    value = Column(BigInteger, nullable=True)


class StringSignalMixin(object):
    value = Column(String(255), nullable=True)


class TextSignalMixin(object):
    value = Column(Text, nullable=True)


class DateTimeSignalMixin(object):
    value = Column(DateTime, nullable=True)


class FloatSignalMixin(object):
    value = Column(Float, nullable=True)


class BooleanSignalMixin(object):
    value = Column(Boolean, nullable=True)


class LargeBinarySignalMixin(object):
    value = Column(LargeBinary, nullable=True)


_TYPE_MIXIN_MAP = {

    # add numpy support
    'float64': FloatSignalMixin,
    'float32': FloatSignalMixin,

    "int": BigIntegerSignalMixin,
    "float": FloatSignalMixin,
    "str": StringSignalMixin,
    "bool": BooleanSignalMixin,
    datetime: DateTimeSignalMixin,
    None: float,
    'None': float,
    'datetime': DateTimeSignalMixin,

    # provide backward compatibility
    "uint8_t": BigIntegerSignalMixin,
    "uint16_t": BigIntegerSignalMixin,
    "uint32_t": BigIntegerSignalMixin,
    "double": FloatSignalMixin,
    "float_t": FloatSignalMixin,
}


def get_signal_table(metadata, name, aggregated=False):
    """Get the table of the signal with the given `name` which value is of the specified `valuetype`.

    Args:
        name (str): Name of the signal
        aggregated (bool): If the signal is an aggregated signal.

    Returns:
        sqlalchemy.Table: The table of the signal
        None: If no table is not found
    """
    try:
        # the model does not exist; check if the tables exists
        table = metadata.tables[signal_table_name(name, aggregated)]

        return table
    except KeyError:
        pass


def create_signal_table(metadata, base, name, valuetype, aggregated=True):
    """Create a table for the signal with the `name` which value is of the specified `valuetype`.

    Args:
        metadata: Metadata used by this application
        name (str): Name of the signal
        valuetype (str|any): Name of the signal value type or a python type
        aggregated (bool): If the signal is an aggregated signal.

    Returns:
        tuple[sqlalchemy.MetaData, sqlalchemy.Table]: The meta model and the table

    Warning:
        The use of the returned model is deprecated and will be removed.

    """

    table = get_signal_table(metadata, name, aggregated)

    model = None

    if table is None:
        try:
            signal_type = _TYPE_MIXIN_MAP[valuetype]
        except KeyError:
            signal_type = LargeBinarySignalMixin

        model = type(name, (SignalAggregatedBaseModel if aggregated else SignalBaseModel, base,
                            signal_type,), {})

        table = model.__table__

    if not table.exists():
        metadata.create_all(tables=[table])

    if model is None:
        model = get_class_by_table(base, table)

    return model, table
