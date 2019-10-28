#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class Keyboard(Base):
    ''' Device '''
    __tablename__ = 'so_frontage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    keyboard_label = Column('label', String(255))
    keyboard_type = Column('type', Integer)

    def __init__(self, keyboard_label, keyboard_type):
        self.keyboard_label = keyboard_label
        self.keyboard_type = keyboard_type

    def __repr__(self):
        return '<Keyboard %r>' % (self.keyboard_label)

def get_keyboard(keyboard_id):
    return db_session.query(Keyboard).filter(Keyboard.id == keyboard_id).first()