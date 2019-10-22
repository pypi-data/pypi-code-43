#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON

import datetime


class EventLog(Base):
    ''' Event Log '''
    __tablename__ = 'so_event_log'
    

    LOG = 'Log'
    EXCEPTION = 'Exception'

    TYPE_INSTALLATION = 'Installation'

    id = Column(Integer, primary_key=True, autoincrement=True)

    log_flag = Column('log_flag', String(64), nullable=False)
    log_message = Column('log_message', JSON)
    log_timestamp = Column('log_timestamp', DateTime, default=datetime.datetime.utcnow, nullable=False)
    log_type = Column('event_type', String(64), nullable=False)

    device_skiply_id = Column('device_skiply_id', String(255), nullable=False)

    def __init__(self, device_id, log_type, log_flag, log_message):
        self.device_skiply_id = device_id

        self.log_type = log_type
        self.log_flag = log_flag

        self.log_message = log_message

    def __repr__(self):
        return '<EventLog %r>' % (self.id)

def get_log(log_id):
    return db_session.query(EventLog).filter(EventLog.id == log_id).first()

def get_logs(log_type, nb_log):
    return db_session.query(EventLog).filter(EventLog.log_type == log_type).order_by(EventLog.log_timestamp.desc()).limit(nb_log).all()

def add_log(device_id, log_type, log_flag, log_message):
    log = EventLog(device_id, log_type, log_flag, log_message)
    db_session.add(log)
    db_session.commit()