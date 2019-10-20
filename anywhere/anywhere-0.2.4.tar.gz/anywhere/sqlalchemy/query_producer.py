# -*- coding:utf-8 -*-
import typing

from sqlalchemy import select, Table, and_, or_

from anywhere import base_types as bt
from .field import Field


def _filter_fields(attrs):
    """
    """
    return filter(lambda item: isinstance(item[1], Field), attrs.items())


def _frozen_setattrs(self, name, value):
    raise RuntimeError('Meta if already frozen')


class QueryProducerMeta(type):

    def __new__(mcs, name, bases, attrs: typing.MutableMapping):  # pylint: disable=bad-mcs-classmethod-argument
        print('bases:', bases)

        if name == 'QueryProducer':
            return super().__new__(mcs, name, bases, attrs)

        attrs['_meta'] = mcs.prepare_meta(attrs)
        attrs['_fields'] = mcs.prepare_fields_map(attrs)

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def prepare_meta(attrs: typing.MutableMapping):
        # pylint: disable=unsupported-membership-test,unsubscriptable-object
        if 'Meta' not in attrs:
            raise RuntimeError('no Meta')
        if not hasattr(attrs['Meta'], 'table'):
            raise RuntimeError('no table in Meta')
        if not isinstance(attrs['Meta'].table, Table):
            raise RuntimeError('Meta.table is not Table')

        frozen_meta = attrs.pop('Meta')
        frozen_meta.__setattr__ = _frozen_setattrs
        frozen_meta.__delattr__ = _frozen_setattrs

        return frozen_meta

    @staticmethod
    def prepare_fields_map(attrs: typing.MutableMapping):
        # pylint: disable=unsubscriptable-object
        table = attrs['_meta'].table
        fields = {}

        for name, field in _filter_fields(attrs):
            field.name = name
            fields[name] = field

            if field.column is not None:
                continue

            if name not in table.columns:
                raise RuntimeError(f'Column {name} does not exist in {table}!')

            field.column = table.columns[name]

        return fields


class MetaType(typing.NamedTuple):
    table: Table


class QueryProducer(metaclass=QueryProducerMeta):

    _fields: typing.Mapping[str, Field] = None
    _meta: MetaType

    # Public interface

    @property
    def fields(self) -> typing.Mapping[str, Field]:
        return self._fields

    def get_base_query(self):
        return select([self._meta.table])

    def query_from_where(self, where, *, base_query=None):
        if base_query is None:
            query = self.get_base_query()
        else:
            query = base_query

        return query.where(self._whereclause(where))

    # Internal functions

    def _whereclause(self, where):
        if isinstance(where, bt.Primitive):
            return self._primitive_comparision(where)

        return self._logical_condition(where)

    def _primitive_comparision(self, where: bt.Primitive):
        field = self.fields[where.field]  # pylint: disable=unsubscriptable-object
        cmp_fn = field.operators[where.op]

        return cmp_fn(field.column, where.value)

    def _logical_condition(self, where: bt.Condition):
        operator = and_ if where.op == bt.Operator.AND else or_

        return (operator(*[
            self._whereclause(child) for child in where.values
        ]))
