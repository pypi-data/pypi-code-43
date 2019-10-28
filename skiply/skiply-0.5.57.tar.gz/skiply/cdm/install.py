#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON


class Installation(Base):
    ''' Event Log '''
    __tablename__ = 'i_installs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    created_date = Column('created_on', DateTime)

    install_label = Column('label', String(200), nullable=False)
    install_config_file = Column('config_file', String(500))
    install_ended_on = Column('ended_on', DateTime)
    install_started_on = Column('started_on', DateTime)
    install_support_phone_number = Column('support_phone_number', String(20))

    install_group_set = Column('group_set', Boolean, default=False, nullable=False)
    install_standalone_inst = Column('standalone_inst', Boolean, default=False, nullable=False)
    install_language = Column('lang', String(10), default=False, nullable=False)
    
    endpoint = Column('endpoint', String(500))

    install_inst_id = Column('install_inst_id', Integer, ForeignKey("i_install_instructions.id"), nullable=False)

    entity_id = Column('client_id', Integer, ForeignKey("so_client.id"), nullable=False)

    def __init__(self, install_inst_id, entity_id, install_label, endpoint=None):
        self.install_inst_id = install_inst_id

        self.entity_id = entity_id
        self.install_label = install_label

        self.endpoint = endpoint

    def __repr__(self):
        return '<Installation %r>' % (self.install_label)

def get_installation(install_id):
    if install_id is not None:
        return db_session.query(Installation).filter(Installation.id == install_id).first()
    else:
        return None

def get_installations():
    return db_session.query(Installation).all()