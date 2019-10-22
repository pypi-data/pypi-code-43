# coding: utf-8
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class UserPortrait(Base):
    __tablename__ = 'user_portrait'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    low_pur_power = Column(Integer, nullable=False)
    med_pur_power = Column(Integer, nullable=False)
    high_pur_power = Column(Integer, nullable=False)
    high_school = Column(Integer, nullable=False)
    junior_college = Column(Integer, nullable=False)
    undergraduate = Column(Integer, nullable=False)
    job1 = Column(Integer, nullable=False)
    job2 = Column(Integer, nullable=False)
    job3 = Column(Integer, nullable=False)
    job4 = Column(Integer, nullable=False)
    job5 = Column(Integer, nullable=False)
    job6 = Column(Integer, nullable=False)
    mobile_phone = Column(String(500))
    male = Column(Integer, nullable=False)
    female = Column(Integer, nullable=False)
    teenagers = Column(Integer, nullable=False)
    youth = Column(Integer, nullable=False)
    adult = Column(Integer, nullable=False)
    old = Column(Integer, nullable=False)