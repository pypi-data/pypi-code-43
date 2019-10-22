# coding: utf-8
from sqlalchemy import BigInteger, Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.schema import FetchedValue
from configs.db_config import db


class HoursDatum(db.Model):
    __tablename__ = 'hours_data'

    id = db.Column(Integer, primary_key=True)
    date_hour = db.Column(Integer, nullable=False, index=True)
    passenger_flow = db.Column(Integer, nullable=False)
    customer_trend = db.Column(Integer, nullable=False)

class DailyDatum(db.Model):
    __tablename__ = 'daily_data'

    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False, index=True)
    passenger_flow = db.Column(Integer, nullable=False)
    customer_trend = db.Column(Integer, nullable=False)
    old_number = db.Column(Integer, nullable=False)
    new_number = db.Column(Integer, nullable=False)
    visited_deep = db.Column(SmallInteger, nullable=False)
    visited_interval = db.Column(SmallInteger, nullable=False)
    avg_stay = db.Column(SmallInteger, nullable=False)
    old_customer_stay = db.Column(SmallInteger, nullable=False)
    new_customer_stay = db.Column(SmallInteger, nullable=False)
    top_10 = db.Column(String(60), nullable=False)

class DailyVisit(db.Model):
    __tablename__ = 'daily_visit'

    id = db.Column(Integer, primary_key=True)
    customer_mac = db.Column(BigInteger, nullable=False)
    date = db.Column(Date, nullable=False)
    visited_zone_list = db.Column(Text)
    visited_deep = db.Column(SmallInteger, nullable=False)
    vitied_interval = db.Column(SmallInteger, nullable=False)


class CustomerDatum(db.Model):
    __tablename__ = 'customer_data'

    customer_mac = db.Column(BigInteger, primary_key=True)
    last_visit_time = db.Column(Date, nullable=False)
    visit_blank = db.Column(Integer, server_default=FetchedValue())
    visit_blank_list = db.Column(Text)
    level = db.Column(Integer, nullable=False, server_default=FetchedValue())