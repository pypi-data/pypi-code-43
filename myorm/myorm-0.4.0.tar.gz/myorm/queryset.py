#!/usr/bin/env python
# coding: utf-8

from copy import copy

from myorm.exceptions import TooManyResultsError


class QuerySet:

    def __init__(self, base):
        self.base = base
        self.adaptor = self.base.adaptor
        self.partials = {
            'filters': [],
            'excludes': [],
            'updates': [],
            'orders': [],
            'limit': None,
            'create': None,
            'all': False,
            'count': False,
            'delete': False,
        }

    def __repr__(self):
        result = self()
        appendix = ""
        if len(result) > 20:
            appendix = " ..remainung elements truncated."
        return "%s%s" % (str([item for item in result]), appendix)

    def __len__(self):
        return self.count()

    def make_objects(self, instance, db_results) -> list:
        objects = []
        for result in db_results:
            cls = instance.__class__
            _object = cls()
            mapped = zip(instance.fields, result)
            for field, value in mapped:
                setattr(_object, field.fieldname, field.make_value(value, _object))

            for reverse_name, related_manager in cls.related_managers.items():
                new_manager = copy(related_manager)
                new_manager.id = _object.id
                setattr(_object, reverse_name, new_manager)

            objects.append(_object)

        return objects

    def compile_query(self) -> tuple:
        query = ''
        query_args = []

        if self.partials['all']:
            query = self.adaptor.get_select_query(self.base)

        if self.partials['filters'] or self.partials['excludes']:
            query = self.adaptor.get_select_query(self.base) + ' WHERE '

        if self.partials['updates']:
            query, update_args = self.adaptor.get_update_query(self.base, self.partials['updates'][0])
            query_args.extend(update_args)
            if self.partials['filters']:
                query += 'WHERE '

        if self.partials['delete']:
            query = self.adaptor.get_delete_query(self.base)
            if self.partials['filters']:
                query += 'WHERE '

        if self.partials['filters']:
            filters = []
            for filter_partial in self.partials['filters']:
                filter_query, filter_args = self.adaptor.get_filter_query(filter_partial)
                filters.append(filter_query)
                if isinstance(filter_args, list):
                    query_args.extend(filter_args)
                else:
                    query_args.append(filter_args)
            query += ' AND '.join([item for item in filters])
            if self.partials['excludes']:
                query += ' AND '

        if self.partials['excludes']:
            excludes = []
            for exclude_partial in self.partials['excludes']:
                exclude_query, exclude_args = self.adaptor.get_exclude_query(exclude_partial)
                excludes.append(exclude_query)
                if isinstance(exclude_args, list):
                    query_args.extend(exclude_args)
                else:
                    query_args.append(exclude_args)
            query += ' AND '.join([item for item in excludes])

        if self.partials['orders']:
            query += ' ORDER BY '
            orders = []
            for order_partial in self.partials['orders']:
                direction = 'DESC' if order_partial[0].startswith('-') else 'ASC'
                orders.append('%s %s' % (order_partial[0].replace('-', ''), direction))
            query += ', '.join(orders)

        if self.partials['limit']:
            query += self.adaptor.get_limit_query(self.partials['limit'])

        return (query, query_args)

    def execute_sql(self):
        query, query_args = self.compile_query()
        result = self.adaptor.execute_query(query, query_args)[0]
        return result

    def __call__(self):
        result = self.execute_sql()
        return self.make_objects(self.base, result)

    def __iter__(self):
        objects = self.make_objects(self.base, self.execute_sql())
        for item in objects:
            yield item

    def __getitem__(self, n):
        return list(self)[n]

    def filter(self, *args, **kwargs):
        if not kwargs:
            self.partials['all'] = True
        for key, value in kwargs.items():
            self.partials['filters'].append({key: value})
        return self

    def exclude(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.partials['excludes'].append({key: value})
        return self

    def get(self, *args, **kwargs):
        result = self.filter(*args, **kwargs)()

        if len(result) <= 1:
            try:
                return result[0]
            except IndexError:
                raise IndexError("No %s object found" % self.base.__class__.__name__)
        raise TooManyResultsError('To many results for get(): %s' % len(result))

    def delete(self, *args, **kwargs) -> None:
        self.partials['delete'] = True
        self()
        return None

    def update(self, *args, **kwargs):
        count = 0
        filters = self.partials['filters']
        if filters:
            count_qs = QuerySet(self.base)
            for item in filters:
                count_qs = count_qs.filter(**item)
            count = count_qs.count()

        for key, value in kwargs.items():
            self.partials['updates'].append({key: value})
        self()
        return count

    def order_by(self, *args):
        self.partials['orders'].append(args)
        return self

    def first(self):
        self.partials['limit'] = 1
        result = self()
        if result:
            return result[0]

    def count(self):
        return len(self())

    def exists(self):
        return self.count() > 0
