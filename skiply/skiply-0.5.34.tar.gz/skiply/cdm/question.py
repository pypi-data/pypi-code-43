#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class Question(Base):
    ''' Device '''
    __tablename__ = 'so_question'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    question_label = Column('libelle', String(255))
    
    question_principal = Column('principale', Boolean, default=True)

    entity_id = Column('client_id', Integer, ForeignKey("so_client.id"), nullable=False)

    def __init__(self, question_label, question_principal, entity_id):
        self.question_label = question_label
        self.question_principal = question_principal

        self.entity_id = entity_id

    def __repr__(self):
        return '<Question %r>' % (self.question_label)

def get_question(question_id):
    return db_session.query(Question).filter(Question.id == question_id).first()

def get_questions_of_entity(entity_id):
    return db_session.query(Question).filter(Question.entity_id == entity_id).all()