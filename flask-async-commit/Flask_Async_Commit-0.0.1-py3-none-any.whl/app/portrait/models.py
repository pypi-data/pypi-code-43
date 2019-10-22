# coding: utf-8
from sqlalchemy import BigInteger, Date, ForeignKey, Integer, SmallInteger, String, Text
from configs.db_config import db


class UserPortrait(db.Model):
    __tablename__ = 'user_portrait'

    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False, index=True)
    low_pur_power = db.Column(Integer, nullable=False)
    med_pur_power = db.Column(Integer, nullable=False)
    high_pur_power = db.Column(Integer, nullable=False)
    high_school = db.Column(Integer, nullable=False)
    junior_college = db.Column(Integer, nullable=False)
    undergraduate = db.Column(Integer, nullable=False)
    job1 = db.Column(Integer, nullable=False)
    job2 = db.Column(Integer, nullable=False)
    job3 = db.Column(Integer, nullable=False)
    job4 = db.Column(Integer, nullable=False)
    job5 = db.Column(Integer, nullable=False)
    job6 = db.Column(Integer, nullable=False)
    mobile_phone = db.Column(String(500))
    male = db.Column(Integer, nullable=False)
    female = db.Column(Integer, nullable=False)
    teenagers = db.Column(Integer, nullable=False)
    youth = db.Column(Integer, nullable=False)
    adult = db.Column(Integer, nullable=False)
    old = db.Column(Integer, nullable=False)