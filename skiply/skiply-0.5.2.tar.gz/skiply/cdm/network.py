#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class Network(Base):
    ''' Device '''
    __tablename__ = 'so_network'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    network_label = Column('label', String(255))
    
    network_operator_url = Column('operator_url', String(500))
    network_operator_url_header = Column('operator_url_header', String(1000))

    network_type = Column('network_type', String(255))

    def __init__(self, network_label, network_operator_url, network_operator_url_header, network_type):
        self.network_label = network_label
        self.network_operator_url = network_operator_url
        self.network_operator_url_header = network_operator_url_header

        self.network_type = network_type

    def __repr__(self):
        return '<Network %r>' % (self.network_label)

def get_network(network_id):
    return db_session.query(Network).filter(Network.id == network_id).first()