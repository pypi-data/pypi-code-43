import json
from collections import namedtuple
from uuid import uuid4

import arrow
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy_utils import ArrowType

from dq.database import query_with_limit_offset, Session

# An attribute of a model. The order is the following:
# - name (string): The name of the attribute (the key)
# - allow_from (boolean): Whether the attribute can be inflated with incoming
#       dictionaries. Default is True.
# - allow_to (boolean): Whether the attribute can be exported to outgoing
#       dictionaries. Default is True.
# - serializer (function): The function that processes the attribute value
#       before converting to dictionary. Default is None (no-op).
# - deserializer (function): The function that processes the dictionary value
#       before converting to the object attribute. Default is None (no-op).
Attr = namedtuple('Attr', 'name allow_from allow_to serializer deserializer')
Attr.__new__.__defaults__ = (True, True, None, None)


def uuid4_string():
    """Return a UUID as string.

    The UUID type must NOT be used anywhere in the app - only use string.
    This function should be used whenever a new UUID is needed.

    :returns string: A UUID string.
    """
    return str(uuid4())


def arrow_in(value):
    """Convert an arrow-understandable time to an Arrow object.

    :param value: The arrow-understandable time or ``None``.
    :returns Arrow: The Arrow object, or ``None`` if the input is ``None``.
    """
    return arrow.get(value) if value else None


def arrow_out(value):
    """Convert an Arrow object to timestamp.

    :param Arrow value: The Arrow time or ``None``.
    :returns int: The timestamp, or ``None`` if the input is ``None``.
    """
    return value.timestamp if value else None


def boolean_mask(value):
    """Mask a value to boolean. This can be used for sensitive fields.

    :param value: Any value.
    :returns boolean: The input value casted to boolean.
    """
    return bool(value)


def enum_value(value):
    """Convert an enum to its value.

    :param Enum value: An enum.
    :returns string: The value of the enum.
    """
    return value.value if value else None


class DictMixin(object):
    """Dictionary mixin that provides converters to/from Python dicts.

    See comments of ``Attr`` above for defining fields to convert with this
    mixin.

    This class is inherited by ``IDBase`` and ``UUIDBase`` classes, so your
    class will not need to inherit directly from it.
    """

    __attrs__ = ()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.to_dict())

    def to_dict(self):
        """Convert an object to dictionary.

        :returns dict: The dictionary converted from the object.
        """
        out = {}
        for attr in self.__attrs__:
            if not attr.allow_to:
                continue
            name = attr.name
            out[name] = getattr(self, name)
            if attr.serializer:
                out[name] = attr.serializer(out[name])
        return out

    def to_json(self):
        """Convert an object to JSON string.

        :returns string: The JSON string representation of the object.
        """
        return json.dumps(self.to_dict())

    def inflate_to_dict(self, session=None):
        """Convert an object to dictionary, with relationships inflated.

        This method is the default implementation, which simply calls the
        ``to_dict`` method. Subclasses willing to inflate certain fields should
        override this method.

        :param Session session: The optional SQL session.
        :returns dict: The dictionary converted from the object.
        """
        return self.to_dict()

    @classmethod
    def from_dict(cls, data):
        """Convert a dictionary to an object.

        :param dict data: The data dictionary.
        :returns Base: The object converted from the dictionary.
        """
        entity = cls()
        for attr in entity.__attrs__:
            if not attr.allow_from:
                continue
            value = data.get(attr.name)
            if attr.deserializer:
                value = attr.deserializer(value)
            setattr(entity, attr.name, value)
        return entity


class TimeMixin(object):
    """Time fields common to all models.

    This class is inherited by ``IDBase`` and ``UUIDBase`` classes, so your
    class will not need to inherit directly from it.
    """

    created_at = Column(ArrowType, nullable=False, default=arrow.utcnow)
    updated_at = Column(ArrowType, nullable=False, default=arrow.utcnow,
                        onupdate=arrow.utcnow)
    deleted_at = Column(ArrowType)


class QueryMixin(object):
    """Query helper functions useful to all models.

    This class is inherited by ``IDBase`` and ``UUIDBase`` classes, so your
    class will not need to inherit directly from it.
    """

    @classmethod
    def get_by(cls, column, value, for_update=False, contains_deleted=False,
               contains_empty=False, session=None):
        """Get the object satisfying the query condition.

        :param string column: The name of the column to query by.
        :param string value: The value of the column to query for.
        :param boolean for_update: Whether the query is for updating the row.
        :param boolean contains_deleted: Whether to contain deleted records.
            Default is ``False`` and only active records are returned.
        :param boolean contains_empty: Whether to contain empty records.
            Default is ``False`` and if value is ``None``, ``None`` will be
            returned.
        :param Session session: Optional SQL session.
        :returns QueryMixin: The matching object. This method is designed for
            unique queries and in case of multiple matches, only the first one
            is returned.
        """
        if not contains_empty and value is None:
            return None

        session = session or Session()
        args = {}
        args[column] = value
        if not contains_deleted:
            args['deleted_at'] = None
        query = session.query(cls).filter_by(**args)
        if for_update:
            query = query.with_for_update()
        return query.first()

    @classmethod
    def get_multi(cls, column, value, sort_column='updated_at', desc=True,
                  offset=0, limit=10, session=None):
        """Get multiple objects satisfying the query condition.

        :param string column: The name of the column to query by.
        :param string value: The value of the column to query for.
        :param string sort_column: The column to sort results against. Default
            is updated_at. Please note that created_at usually doesn't have
            index, so if it should be used as the sort column, an index needs
            to be added.
        :param bool desc: Whether to sort DESC. Default is ``True``.
        :param int offset: The query offset. Default is 0.
        :param int limit: The max number of results to return. Default is 10.
            If specified, the function will try to fetch one more result to
            indicate whether there are more results. If not specified or 0, all
            results will be returned.
        :param Session session: The optional SQL session to use.
        """
        session = session or Session()
        args = {'deleted_at': None}
        args[column] = value
        q = session.query(cls).filter_by(**args)
        if sort_column:
            attr = getattr(cls, sort_column)
            q = q.order_by(attr.desc()) if desc else q.order_by(attr.asc())
        return query_with_limit_offset(q, limit, offset).all()


class UserRelationMixin(QueryMixin):
    """Mixin that provides a common ``get_by_user`` function.

    This mixin should be used by classes that a user can have a 1-many
    relationship to, such as orders, shipments, and periods.
    """

    # The key used for sorting (DESC) when getting by user. This is most likely
    # a time field such as created_at or updated_at.
    sort_key = None

    @classmethod
    def get_by_user(cls, user_id, desc=True, offset=0, limit=10, session=None):
        """Get the related object of a user.

        :param string/int user_id: The ID (if int) or UUID (if string) of the
            user.
        :param bool desc: Whether to sort DESC. Default is ``True``.
        :param integer offset: The offset of the objects. If limit is 10 and
            offset is 5, the function will attempt to get the 6th to 15th
            most recent objects.
        :param integer limit: The max number of objects to get.
        :param Session session: The optional SQL session.
        :returns list<UserRelationMixin>: The list of objects matching the
            requirement.
        """
        column = 'user_id' if isinstance(user_id, int) else 'user_uuid'
        return cls.get_multi(column, user_id, cls.sort_key, desc=desc,
                             offset=offset, limit=limit, session=session)


@as_declarative()
class IDBase(QueryMixin, DictMixin, TimeMixin):
    """Base class for an ORM model with numeric ID as the primary key."""

    __attrs__ = (
        Attr('id', allow_to=False),
    )

    id = Column(Integer, primary_key=True)

    @classmethod
    def get(cls, id, for_update=False, contains_deleted=False, session=None):
        """Get an object by its ID.

        :param int id: The ID of the object.
        :param boolean for_update: Whether the query is for updating the row.
        :param boolean contains_deleted: Whether to contain deleted objects.
            Default is ``False``.
        :param Session session: Optional SQL session to use.
        """
        return cls.get_by('id', id, for_update=for_update,
                          contains_deleted=contains_deleted, session=session)


@as_declarative()
class UUIDBase(QueryMixin, DictMixin, TimeMixin):
    """Base class for an ORM model with UUID as the primary key."""

    __attrs__ = (
        Attr('uuid', allow_to=False),
    )

    uuid = Column(String, primary_key=True, default=uuid4_string)

    @classmethod
    def get(cls, uuid, for_update=False, contains_deleted=False, session=None):
        """Get an object by its UUID.

        :param string uuid: The UUID of the object.
        :param boolean for_update: Whether the query is for updating the row.
        :param boolean contains_deleted: Whether to contain deleted objects.
            Default is ``False``.
        :param Session session: Optional SQL session to use.
        """
        return cls.get_by('uuid', uuid, for_update=for_update,
                          contains_deleted=contains_deleted, session=session)
