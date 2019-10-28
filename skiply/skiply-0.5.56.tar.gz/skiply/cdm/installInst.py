#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON

import datetime


class InstallationInstruction(Base):
    ''' Event Log '''
    __tablename__ = 'i_install_instructions'

    id = Column(Integer, primary_key=True, autoincrement=True)

    inst_label = Column('label', String(200), nullable=False)
    inst_created_on = Column('created_on', DateTime, default=datetime.datetime.utcnow, nullable=False)
    inst_product_type = Column('product_type',String(20), default='SATISFACTION', nullable=False)

    def __init__(self, inst_label):
        self.inst_label = inst_label

    def __repr__(self):
        return '<Installation instruction %r>' % (self.inst_label)


def get_installation_instruction(install_inst_id):
    return db_session.query(InstallationInstruction).filter(InstallationInstruction.id == install_inst_id).first()

def get_installation_instruction_from_type(type):
    return db_session.query(InstallationInstruction).filter(InstallationInstruction.inst_product_type == type).first()

def get_installation_instructions():
    return db_session.query(InstallationInstruction).all()