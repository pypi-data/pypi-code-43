#!/usr/bin/env python
# coding: utf-8

from myorm.queryset import QuerySet
from myorm.exceptions import TooManyResultsError


class Manager:

    def __init__(self, base):
        self.base = base
        self.adaptor = self.base.adaptor

    def filter(self, *args, **kwargs):
        query_set = QuerySet(self.base)
        return query_set.filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        query_set = QuerySet(self.base)
        return query_set.exclude(*args, **kwargs)

    def all(self):
        return self.filter()

    def first(self):
        return self.all().first()

    def count(self):
        return self.filter().count()

    def exists(self):
        return self.count() > 0

    def create(self, *args, **kwargs):
        query, query_args = self.adaptor.get_insert_query(self.base, kwargs)
        _, _id = self.adaptor.execute_query(query, query_args)
        return self.get(id=_id)

    def get(self, *args, **kwargs):
        result = self.filter(*args, **kwargs)()

        if len(result) <= 1:
            try:
                return result[0]
            except IndexError:
                raise IndexError("No %s object found" % self.base.__class__.__name__)
        raise TooManyResultsError('To many results for get(): %s' % len(result))

    def bulk_create(self, objects):
        self.adaptor.bulk_create(objects, self.base)


class RelatedManager(Manager):

    def __init__(self, target, fieldname, reverse_name):
        self.id = None
        self.base = target
        self.fieldname = fieldname
        target.related_managers[reverse_name] = self

    def filter(self, *args, **kwargs):
        field_filter = {self.fieldname: self.id}
        return super().filter(**field_filter).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        field_filter = {self.fieldname: self.id}
        return super().filter(**field_filter).exclude(*args, **kwargs)

    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError("bulk_create cannot be used on RelatedManagers")
