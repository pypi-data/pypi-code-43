#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class PowerSupply(Base):
    ''' Device '''
    __tablename__ = 'so_power_supply'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    power_time = Column('time', DateTime, nullable=False)
    power_voltage = Column('power_voltage', Integer, nullable=False)

    device_id = Column('device_id', Integer, nullable=False)
    device_skiply_id = Column('devicename', String(255))

    def __init__(self, power_time, power_voltage, device_id, device_skiply_id):
        self.power_time = power_time
        self.power_voltage = power_voltage

        self.device_id = device_id
        self.device_skiply_id = device_skiply_id

    def __repr__(self):
        return '<Power Supply %s - %s>' % (self.power_time, self.power_voltage)

def get_powerSupply(powerSupply_id):
    return db_session.query(Question).filter(Question.id == question_id).first()

def get_questions_of_entity(entity_id):
    return db_session.query(Question).filter(Question.entity_id == entity_id).all()