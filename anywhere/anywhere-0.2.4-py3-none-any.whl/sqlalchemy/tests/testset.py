# -*- coding:utf-8 -*-
from sqlalchemy import or_, and_, select

from .conftest import SomeModel


WHERECLAUSES = [
    SomeModel.__table__.c.public_id == 'value',
    SomeModel.__table__.c.public_id == 42,
    SomeModel.__table__.c.public_id == 3.14,
    SomeModel.__table__.c.public_id == True,  # pylint: disable=singleton-comparison
    or_(
        SomeModel.__table__.c.public_id == 'aaa',
        SomeModel.__table__.c.f2 == 5,
    ),
    or_(
        SomeModel.__table__.c.public_id == 'aaa',
        SomeModel.__table__.c.f2 == 5,
        SomeModel.__table__.c.public_id == 'bbb',
    ),
    and_(
        SomeModel.__table__.c.public_id == 'aaa',
        SomeModel.__table__.c.f2 == 5,
    ),
    and_(
        SomeModel.__table__.c.public_id == 'aaa',
        SomeModel.__table__.c.f2 == 5,
        SomeModel.__table__.c.public_id == 'bbb',
    ),
    or_(
        and_(
            SomeModel.__table__.c.public_id == 50,
            SomeModel.__table__.c.f2 == 'aaa',
        ),
        SomeModel.__table__.c.f2 == 'bbb',
    ),
    # custom operators
    SomeModel.__table__.c.public_id > 'value',
    SomeModel.__table__.c.public_id > 42,
    SomeModel.__table__.c.public_id > 3.14,
    SomeModel.__table__.c.public_id > 'true',  # we cannot use > operator with boolean value
    or_(
        SomeModel.__table__.c.public_id > 'aaa',
        SomeModel.__table__.c.f2.ilike('%5%'),
    ),
    or_(
        SomeModel.__table__.c.public_id > 'aaa',
        SomeModel.__table__.c.f2.ilike('%5%'),
        SomeModel.__table__.c.public_id > 'bbb',
    ),
    and_(
        SomeModel.__table__.c.public_id > 'aaa',
        SomeModel.__table__.c.f2.ilike('%5%'),
    ),
    and_(
        SomeModel.__table__.c.public_id > 'aaa',
        SomeModel.__table__.c.f2.ilike('%5%'),
        SomeModel.__table__.c.public_id > 'bbb',
    ),
    or_(
        and_(
            SomeModel.__table__.c.public_id > 50,
            SomeModel.__table__.c.f2.ilike('%aaa%'),
        ),
        SomeModel.__table__.c.f2.ilike('%bbb%'),
    ),
]

QUERIES = [
    select([SomeModel.__table__]).where(whereclause) for whereclause in WHERECLAUSES
]
