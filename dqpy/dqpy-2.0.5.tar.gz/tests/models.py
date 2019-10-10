from enum import Enum

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType

from dq import orm


class UserType(Enum):

    regular = 'regular'
    admin = 'admin'


class User(orm.UUIDBase):

    __tablename__ = 'users'
    __attrs__ = (
        orm.Attr('email'),
    )

    email = Column(String)


class Table2(orm.IDBase, orm.UserRelationMixin):

    __tablename__ = 'table2'
    __attrs__ = (
        orm.Attr('id'),
        orm.Attr('user_uuid'),
        orm.Attr('user_type', serializer=orm.enum_value),
        orm.Attr('key', allow_to=False),
        orm.Attr('key2', allow_from=False, serializer=orm.boolean_mask),
        orm.Attr('created_at', serializer=orm.arrow_out,
                 deserializer=orm.arrow_in),
    )

    sort_key = 'created_at'

    user_uuid = Column(String)
    user_type = Column(ChoiceType(UserType, impl=String()))
    key = Column(Integer)
    key2 = Column(Integer)
