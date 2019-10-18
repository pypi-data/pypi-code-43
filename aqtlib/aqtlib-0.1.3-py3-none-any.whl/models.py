# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Integer, Float, ForeignKey, Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Symbol(Base):
    __tablename__ = 'symbols'

    id = Column(Integer(), primary_key=True)
    symbol = Column(String(24), index=True)
    symbol_group = Column(String(18), index=True)
    asset_class = Column(String(3), index=True)
    expiry = Column(Date, index=True)


class Tick(Base):
    __tablename__ = 'ticks'
    __table_args__ = (
        Index('key', 'datetime', 'symbol_id', unique=True),
    )

    id = Column(Integer(), primary_key=True)
    datetime = Column(DateTime(), nullable=False, index=True)
    symbol_id = Column(ForeignKey('symbols.id'), nullable=False, index=True)
    bid = Column(Float(asdecimal=True))
    bidSize = Column(Integer())
    ask = Column(Float(asdecimal=True))
    askSize = Column(Integer())
    last = Column(Float(asdecimal=True))
    lastSize = Column(Integer())

    symbol = relationship('Symbol')
