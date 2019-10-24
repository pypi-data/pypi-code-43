#!/usr/bin/env python
# coding: utf-8

from myorm.managers import RelatedManager


class DbField(object):

    def make_value(self, value, _object):
        return value

    def get_drop_column_query(self, base=None):
        # Must be a function for sqlite
        return self.adaptor.get_drop_column_query(self, base)


class PkField(DbField):

    def __init__(self):
        self.fieldname = 'id'

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_pkfield_create_query()


class IntegerField(DbField):

    def __init__(self, default=None):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_integer_field_create_query(self.default)

    @property
    def add_column_query(self):
        return self.adaptor.get_integer_field_create_column_query(self)


class CharField(DbField):

    def __init__(self, max_length):
        self.max_length = max_length

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_char_field_create_query(self)

    @property
    def add_column_query(self):
        return self.adaptor.get_charfield_create_column_query(self)


class TextField(DbField):

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_text_field_create_query()

    @property
    def add_column_query(self):
        return self.adaptor.get_text_field_create_column_query(self)


class BooleanField(DbField):

    def __init__(self, default):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_boolean_field_create_query(self.default)

    @property
    def add_column_query(self):
        return self.adaptor.get_boolean_field_create_column_query(self)


class DateTimeField(DbField):

    def __init__(self, default=None):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_datetime_field_create_query(self.default)

    @property
    def add_column_query(self):
        raise NotImplementedError("Still not implemented")


class ForeignKey(DbField):

    def __init__(self, reference_class, reverse_name=None):
        self.reference_class = reference_class
        self.reverse_name = reverse_name

    def set_related_manager(self, target):
        if not self.reverse_name:
            self.reverse_name = target.__class__.__name__.lower() + '_set'
        setattr(self.reference_class, self.reverse_name, RelatedManager(target, self.fieldname, self.reverse_name))

    def make_value(self, value, _object):
        if value:
            reference_obj = self.reference_class.objects.filter(id=value)
            if not reference_obj.exists():
                return None
            return reference_obj[0]

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_foreignkey_field_create_query_base()

    @property
    def partial_create_table_query_extension(self):
        return self.adaptor.get_foreignkey_field_create_query_extension(self.reference_class)

    @property
    def add_column_query(self):
        raise NotImplementedError("Still not implemented")
