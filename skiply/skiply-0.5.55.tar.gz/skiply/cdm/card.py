#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON

import datetime


class Card(Base):
    ''' Event Log '''
    __tablename__ = 'so_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_skiply_id = Column('skiply_id', String(255), nullable=False)

    sigfox_id = Column('sigfox_id', String(255), nullable=False)
    lora_id = Column('dev_uid', String(255), nullable=False)

    device_type = Column('device_type', String(100))

    def __init__(self, skiply_id, sigfox_id, dev_uid, device_type=None):
        self.device_skiply_id =skiply_id
        
        self.skiply_id = skiply_id
        self.dev_uid = dev_uid
        self.device_type = device_type

    def __repr__(self):
        return '<Cards %r>' % (self.device_skiply_id)

def getCard(device_id):
    return db_session.query(Card).filter(Card.device_skiply_id == device_id).first()