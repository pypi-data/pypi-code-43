""" Request Structures, the Python API to requests and the data and stuff
"""
import logging
from uuid import UUID

import attr
from attr.validators import instance_of, optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, expression, operators

import impetuous.data

logger = logging.getLogger(__name__)


# TODO break this up into request structures, exceptions, other stuff?

# Validation errors the database driver will send us ...
error_messages = {"entry start end overlap": "This operation tries to make multiple time entries overlap."}


class RequestError(ValueError):
    def __init__(self, orig, *args, **kwargs):
        self.orig = orig
        super().__init__(*args, **kwargs)


class AccessProhibited(Exception):
    pass


class OperationError(Exception):
    pass


class TooFewResults(OperationError):
    pass


class TooManyResults(OperationError):
    pass


#@attr.s()
#class TableAccess(object):
#    tables = attr.ib()
#    where = attr.ib()


@attr.s()
class Agent(object):
    """ Represents a requester...
    """
    #def is_authenticated # TODO use ABC?


@attr.s()
class AccessControl(object):
    """
    Enforce your permissions here.

    All modification involves a table, columns and their values, and sometimes
    an existing row.
    This is enforced by access_to_modify().
    """
    tables = attr.ib()
    joins = attr.ib()
    # can create in resource (maybe if field values are a particular way)
    # can modify/delete a particular resource

    # all this will have to be redone probably or extended to allow for greater
    # querying... such as what resources can I access, what fields on them? what
    # conditions apply or filters are added implicitly on queries concerning
    # fields?

    # Interface might be...
    # On a resource/table; access to insert/view/delete some given entity/row.
    # On a entity/row; access to view/update given some field/column.
    # ... and access to use a join thiny ...

    # - Access to view/modify particular rows on a table should be supplimented
    # with a queryset that limits the rows it can operate on.
    # - It should also be possible to reject requests based on the fields. So
    # give users view/modify permissions to resource columns.

    def access_table_to_modify(self, agent, table_name, data):
        """
        This function should test if the agent can access the table, what rows
        they can access expressed by the where clause, and if they can alter the
        rows accordingly.

        Prohibited table and field value changes can be prevented by raising
        AccessProhibited.
        """
        if agent.is_authenticated():
            table = self.tables[table_name]
            for field in (*table.primary_key.columns.keys(), 'rev'):
                if field in data:
                    raise AccessProhibited(field)
            return table, None
        else:
            raise AccessProhibited()

    def access_table_to_read(self, agent, table_name, data):
        if agent.is_authenticated():
            table = self.tables[table_name]
            return table, None
        else:
            raise AccessProhibited()

    # Also aggregate things like fields to <verb> and ask for them all at once.

    def get_table(self, table_name):
        return self.tables[table_name]

    def access_table_field(self, agent, table_name, field_name):
        return self.get_table(table_name).c[field_name]

    def access_query_field(self, agent, query, field_name):
        return query.c[field_name]

    def access_join(self, agent, join_name):
        return impetuous.data.joins[join_name]

    def render_to_sql(self, obj, agent):
        """
        Given some request thing, return a sqlalchemy sql expression object if
        the agent can access the whatever.
        """
        a = AccessAttempt(self, agent)
        return a.render(obj)


impetuous_access_control = AccessControl(
    tables=impetuous.data.tables,
    joins=impetuous.data.joins,
)


@attr.s()
class AccessAttempt(object):
    """
    ac is the AccessControl
    agent is who is doing the accessing
    memory is what objects we've already rendered and the results (memoizing)
    working is what objects we're currently rendering

    TODO memory could introduce security badnesses if maybe some object is
    legal in one context but not the other?

    TODO capture access requests and do them all at the end in one thing...
    """
    ac = attr.ib()
    agent = attr.ib()
    memory = attr.ib(default=attr.Factory(dict))
    working = attr.ib(default=attr.Factory(set))
    #access = attr.ib(default=attr.Factory(list))

    def hash(self, obj):
        """
        We cheat on hashing all throughout here because:
          a) We only care about python object instance memorizing
          b) We don't care about object retrieval for `working`
          c) We don't play by the rules
        """
        return id(obj)

    def render(self, obj):
        obj_hash = self.hash(obj)
        assert obj_hash not in self.working, "Recursion bad!"
        self.working.add(obj_hash)
        try:

            if isinstance(obj, Comparison):
                sql = self._render_comparison(obj)
            elif isinstance(obj, Conjunction):
                sql = self._render_conjunction(obj)
            elif isinstance(obj, Gather):
                sql = self._render_gather(obj)
            elif isinstance(obj, Param):
                sql = self._render_param(obj)
            elif isinstance(obj, Field):
                sql = self._render_field(obj)
            elif isinstance(obj, Sort):
                sql = self._render_sort(obj)
            elif obj is None:  # Hrm..... this should probably not be allowed ...
                sql = None
            elif isinstance(obj, list):  # FIXME
                sql = obj
            else:
                # TODO FIXME decide on something here ...
                #sql = expression.literal(obj)
                raise NotImplementedError(f"Not sure what to do with {obj!r}.")

            self.memory[obj_hash] = sql
            return sql
        finally:
            self.working.remove(obj_hash)

    def _render_conjunction(self, obj):
        return obj.op(*(self.render(part) for part in obj.parts))

    def _render_comparison(self, obj):
        opfn = {
            'like': operators.like_op,
            'ilike': operators.ilike_op,
            'in': operators.in_op,
            'eq': operators.eq,
            'ne': operators.ne,
            'ge': operators.ge,
            'gt': operators.gt,
            'le': operators.le,
            'lt': operators.lt,
            'is': operators.is_,
            'is not': operators.isnot,
        }[obj.op]
        return opfn(self.render(obj.lh), self.render(obj.rh))

    def _render_param(self, obj):
        return expression.bindparam(obj.key, expanding=obj.expanding)

    def _render_gather(self, obj):
        where = None if obj.match is None else self.render(obj.match)
        # TODO maybe use render field here maybe? fix dis
        fields = [self.render(r) for r in obj.fields]
        # ... and here FIXME TODO XXX
        if obj.order_by:
            order_by = [self.render(r) for r in obj.order_by]
        else:
            order_by = None
        stmt = expression.select(fields, whereclause=where, order_by=order_by,
                                 limit=obj.limit)
        for join in obj.relating:
            stmt = stmt.select_from(self.ac.access_join(self.agent, join))
        return stmt

    def _render_fields(self, obj):
        """ Special handling for the fields part of the Gather
        """
        raise NotImplementedError

    def _render_field(self, obj):
        if obj.is_concrete:
            col = self.ac.access_table_field(self.agent, obj.at, obj.name)
        else:
            query = self.render(obj.at)
            col = self.ac.access_query_field(self.agent, query, obj.name)
        return col if obj.alias is None else col.label(obj.alias)

    def _render_sort(self, obj):
        # TODO this should be allowed XXX FIXME TODO lasjdfklasdjfklasdjfklaj
        #self._render_field(obj.field)
        if obj.order == 'asc':
            return self.render(obj.field).asc()
        elif obj.order == 'desc':
            return self.render(obj.field).desc()
        else:
            raise NotImplementedError(obj.sort)


@attr.s(frozen=True)
class Comparison(object):
    lh = attr.ib()
    op = attr.ib(validator=instance_of(str))
    rh = attr.ib()

    #def __or__(self, lh, rh):
    #    return Conjunction.or_(lh, rh)

    #def __and__(self, lh, rh):
    #    return Conjunction.and_(lh, rh)


@attr.s(frozen=True)
class Conjunction(object):
    # Op is actually as sqlalchemy expression, the only place where we only
    # directly reference sqlalchemy in the request stuff FIXME
    op = attr.ib()#validator=attr.validators.in_(['and', 'or']))
    # TODO, stronger validation, check the contents of the tuple ...
    parts = attr.ib(validator=instance_of(tuple),
                    converter=tuple)

    @classmethod
    def and_(cls, *parts):
        return cls(expression.and_, parts=parts)

    @classmethod
    def or_(cls, *parts):
        return cls(expression.or_, parts=parts)

    def __or__(self, lh, rh):
        return Conjunction.or_(lh, rh)

    def __and__(self, lh, rh):
        return Conjunction.and_(lh, rh)


@attr.s(frozen=True)
class Gather(object):
    # TODO try to remove converters, it messes with validation/error handling?
    fields = attr.ib(
        converter=tuple,
    )  # This has a validator down below
    # Verbing the attributes here is dumb... TODO XXX FIXME
    relating = attr.ib(
        validator=instance_of(tuple),
        converter=tuple,
        default=attr.Factory(tuple),
    )
    match = attr.ib(
        validator=optional(instance_of((Conjunction, Comparison))),
        default=None,
    )
    order_by = attr.ib(
        converter=tuple,
        default=attr.Factory(tuple),
    )
    limit = attr.ib(
        validator=optional(instance_of(int)),
        default=None,
    )

    @fields.validator
    def fields_tuple_of_fields(self, attribute, value):
        if not (isinstance(value, tuple) and all(isinstance(e, Field) for e in value)):
            raise ValueError(f"'{attribute.name}' must be a collection of fields.")

    @order_by.validator
    def order_by_tuple_of_sorts(self, attribute, value):
        if isinstance(value, tuple) and all(isinstance(e, Sort) for e in value):
            pass
        else:
            raise ValueError(f"'{attribute.name}' must be a collection of sorts.")

    #@fields.validator
    #def fields_dict_of_fields(self, attribute, value):
    #    if isinstance(value, dict)\
    #            and all(isinstance(k, str) and (isinstance(v, Field) or self.fields_dict_of_fields(attribute, v))
    #                    for k, v in value.items()):
    #        return "hip hip, horray!"
    #    else:
    #        raise ValueError(f"'{attribute.name}' must be a mapping of string to fields; but instead it's {value!r}.")


@attr.s(frozen=True)
class Param(object):
    key = attr.ib(validator=instance_of(str))
    expanding = attr.ib(validator=instance_of(bool), default=False)


@attr.s(frozen=True)
class Field(object):
    """
    A concrete field is a field on a resource, rather than a gathering. The
    resource is specified with a string.
    """
    at = attr.ib(validator=instance_of((str, Gather)))
    name = attr.ib(validator=instance_of(str))
    alias = attr.ib(default=None)

    @property
    def is_concrete(self):
        return isinstance(self.at, str)


@attr.s(frozen=True)
class Sort(object):
    order = attr.ib(validator=attr.validators.in_(('asc', 'desc')))
    field = attr.ib(validator=instance_of(Field))


# Requests

@attr.s(frozen=True)
class FindRequest(object):
    gather = attr.ib(validator=instance_of(Gather))
    using = attr.ib(validator=optional(instance_of(dict)),
                    default=attr.Factory(dict))


@attr.s(frozen=True)
class InsertRequest(object):
    resource = attr.ib(validator=instance_of(str))
    values = attr.ib()
    #fields = attr.ib()


@attr.s(frozen=True)
class UpdateRequest(object):
    resource = attr.ib(validator=instance_of(str))
    values = attr.ib()
    #match = attr.ib(validator=instance_of((Conjunction, Comparison)))
    id = attr.ib(validator=instance_of(UUID))
    rev = attr.ib(validator=optional(instance_of(UUID)), default=None)
    #fields = attr.ib()


@attr.s(frozen=True)
class DeleteRequest(object):
    resource = attr.ib(validator=instance_of(str))
    match = attr.ib(validator=instance_of((Conjunction, Comparison)))


def RequestError_from_IntegrityError(e):
    logger.debug("Derp? %r", e.orig.args)
    code, = e.orig.args
    msg = error_messages[code]
    raise RequestError(e, msg)


@attr.s()
class Interaction(object):
    """ A context around handling one or more requests.
    """

    conn = attr.ib()
    agent = attr.ib()
    ac = attr.ib(validator=instance_of(AccessControl))

    # TODO, maybe move those values items crap somewhere else
    def find(self, gather, using, map_values=None, unpack_values=None, map_items=None, unpack_items=None):
        # TODO enforce access stuff properly
        sql = self.ac.render_to_sql(gather, agent=self.agent)
        res = self.conn.execute(sql, **using)
        if map_values is not None:
            return (map_values(row.values()) for row in res)
        elif unpack_values is not None:
            return (unpack_values(*row.values()) for row in res)
        elif map_items is not None:
            return (map_items(row.items()) for row in res)
        elif unpack_items is not None:
            return (unpack_items(**dict(row.items())) for row in res)
        else:
            return res

    def find_one(self, *args, **kwargs):
        """ Raises TooFewResults or TooManyResults. Gather with limit=1 maybe.
        """
        res = self.find(*args, **kwargs)
        try:
            one = next(res)
        except StopIteration:
            raise TooFewResults("Expected one result, got zero.")
        try:
            next(res)
        except StopIteration:
            return one
        else:
            raise TooManyResults("Expected one result, got more than that.")
        

    def insert(self, resource, values):
        table, condition = self.ac.access_table_to_modify(self.agent, resource, values)
        assert condition is None, "what do we do here?"
        sql = expression.insert(table).values(**values)
        try:
            res = self.conn.execute(sql)
        except IntegrityError as e:
            raise RequestError_from_IntegrityError(e)
        return dict(zip(
            table.primary_key.columns.keys(),
            res.inserted_primary_key,
        ))

    def update(self, resource, values, id, rev=None):
        table, condition = self.ac.access_table_to_modify(self.agent, resource, values)
        where = table.c.id == id
        if rev is not None:
            where &= table.c.rev == rev
        if condition is not None:
            where &= condition
        sql = expression.update(table, whereclause=where).values(**values)
        try:
            res = self.conn.execute(sql)
        except IntegrityError as e:
            # An integrity error is probably a client value error...
            raise RequestError_from_IntegrityError(e)
        else:
            # TODO since the parameters are not where clauses but id and rev,
            # this should expect to update exactly one thing. This should
            # probably be named update_one or something ...
            if res.rowcount != 1:
                raise OperationError("I was supposed to update something but I couldn't find it.")
            #return res.rowcount

    def delete(self, resource, id, rev=None):
        table, condition = self.ac.access_table_to_modify(self.agent, resource, {})
        where = table.c.id == id
        if rev is not None:
            where &= table.c.rev == rev
        if condition is not None:
            where &= condition
        sql = expression.delete(table, whereclause=where)
        try:
            res = self.conn.execute(sql)
        except IntegrityError as e:
            raise RequestError_from_IntegrityError(e)
        else:
            if res.rowcount != 1:
                raise OperationError("I was supposed to delete something but I couldn't find it.")
            #return res.rowcount
