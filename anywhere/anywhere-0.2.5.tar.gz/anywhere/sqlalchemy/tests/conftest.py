# -*- coding:utf-8 -*-
# pylint: disable=too-few-public-methods
import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from anywhere.sqlalchemy import Field
from anywhere.sqlalchemy import QueryProducer

Base = declarative_base()  # pylint: disable=invalid-name


class SomeModel(Base):
    __tablename__ = 'some_table'

    id = Column(Integer, primary_key=True)
    public_id = Column(String(50))
    f2 = Column(String(50))


class SampleQueryProducer(QueryProducer):

    class Meta:
        table = SomeModel.__table__

    f1 = Field(
        column=SomeModel.__table__.c.public_id,
        extra_operators=(
            ('gt', lambda col, val: col > str(val)),  # casting to string to handle > operator with boolean value
        ),
    )
    f2 = Field(
        extra_operators=(
            ('match', lambda col, val: col.ilike(f'%{val}%')),
        ),
    )


@pytest.fixture
def query_producer():
    return SampleQueryProducer()
