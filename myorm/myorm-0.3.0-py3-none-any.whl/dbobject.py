#!/usr/bin/env python
# coding: utf-8

from myorm.fields import DbField, ForeignKey, PkField
from myorm.managers import Manager
from myorm.queryset import QuerySet


class MetaType(type):

    def __init__(cls, name, bases, attrs):
        if name == 'DbObject':
            setattr(cls, 'managed_models', [])
            return

        cls.managed_models.append(cls)

        if hasattr(cls, 'manager'):
            manager = getattr(cls, 'manager')
        else:
            manager = Manager

        cls.objects = manager(cls())

        tablename = getattr(cls, 'tablename', None)
        if not tablename or tablename == 'dbobject':
            cls.tablename = cls.__name__.lower()


class DbObject(metaclass=MetaType):
    adaptor = None
    related_managers = {}

    def __init__(self, *args, **kwargs):
        self.fields = [v for v in self.__class__.__dict__.values() if isinstance(v, DbField)]
        self.fieldnames = [k for k, v in self.__class__.__dict__.items() if isinstance(v, DbField)]

        pk = [f for f in self.fields if type(f) == PkField]
        try:
            pk[0]
        except IndexError:
            self.id = PkField()
            self.fields.append(self.id)
            self.fieldnames.append('id')

        for name in self.fieldnames:
            field = getattr(self, name)
            if kwargs:
                setattr(self, name, kwargs.get(name))
            setattr(field, 'fieldname', name)
            setattr(field, 'adaptor', self.adaptor)
            if isinstance(field, ForeignKey):
                field.set_related_manager(self)

    def __repr__(self):
        return "<{0}.{1} object>".format(self.__class__.__module__, self.__class__.__name__)

    @classmethod
    def raw(self, query, *args):
        return self.adaptor.execute_query(query, args)[0]

    def get_settings(self):
        settings = {}
        for fieldname in self.fieldnames:
            value = getattr(self, fieldname)
            if isinstance(value, DbObject):
                value = value.id
            settings[fieldname] = value
        return settings

    @classmethod
    def create_table(cls, tablename=None):
        create_table_query = cls.adaptor.get_create_table_query(cls(), tablename)
        return cls.adaptor.execute_query(create_table_query[0], create_table_query[1])

    @classmethod
    def drop_table(cls, tablename=None):
        drop_table_query = cls.adaptor.get_drop_table_query(cls(), tablename)
        return cls.adaptor.execute_query(drop_table_query[0], drop_table_query[1])

    @classmethod
    def add_field(cls, field):
        cls.adaptor.execute_query(field.add_column_query % cls.tablename, None)

    @classmethod
    def drop_field(cls, field, base):
        cls.adaptor.execute_query(field.get_drop_column_query(base), None)

    def delete(self):
        assert self.id is not None, "%s cannot be deleted because it has no id" % self.__class__.__name__
        query_set = QuerySet(self)
        query_set.filter(id=self.id).delete()
        query_set()
        return True

    def save(self) -> bool:
        if self.id:
            query_set = QuerySet(self)
            query_set.filter(id=self.id)
            query_set.partials['updates'] = [self.get_settings()]
            query_set()
            return

        query, query_args = self.adaptor.get_insert_query(self, self.get_settings())
        last_id = self.adaptor.execute_query(query, query_args)[1]
        inst = self.objects.get(id=last_id)
        for name in self.fieldnames:
            setattr(self, name, getattr(inst, name))
        return
