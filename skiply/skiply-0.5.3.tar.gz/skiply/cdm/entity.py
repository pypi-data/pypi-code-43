#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class Entity(Base):
    ''' Device '''
    __tablename__ = 'so_client'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    entity_label = Column('entite_name', String(255))
    entity_description = Column('description', String())

    entity_address = Column('entite_address', String(255))
    entity_postcode = Column('entite_cp', String(10))
    entity_city = Column('entite_ville', String(255))
    entity_country = Column('entite_pays', String(255))
    entity_phone = Column('entite_phone', String(255))

    entity_timezone = Column('timezone', String(255), default="Europe/Paris")

    entity_parent = Column('client_id', Integer, ForeignKey("so_client.id"), nullable=False)

    def __init__(self, 
        entity_label, entity_description,
        entity_address, entity_postcode, entity_city, entity_country, entity_phone,
        entity_timezone, entity_parent):
        self.entity_label = entity_label
        self.entity_description = entity_description

        self.entity_address = entity_address
        self.entity_postcode = entity_postcode
        self.entity_city = entity_city
        self.entity_country = entity_country
        self.entity_phone = entity_phone

        self.entity_timezone = entity_timezone
        self.entity_parent = entity_parent

    def __repr__(self):
        return '<Entity %r>' % (self.entity_label)

def get_entity(entity_id):
    return db_session.query(Entity).filter(Entity.id == entity_id).first()