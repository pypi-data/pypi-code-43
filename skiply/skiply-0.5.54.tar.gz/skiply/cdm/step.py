#!/usr/bin/python
# coding: utf8

# Copyright 2019 Skiply

from __future__ import unicode_literals


from .base import db_session, Base, SkiplyBase

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON

import datetime, json


class Step(Base):
    ''' Event Log '''
    __tablename__ = 'i_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)

    created_on = Column('created_on', DateTime, default=datetime.datetime.utcnow, nullable=False)

    install_inst_id = Column('install_inst_id', Integer, ForeignKey("i_installs.id"), nullable=False)

    step_label = Column('label', String(200), nullable=False)
    step_image = Column('image', String(255), nullable=False)
    step_seq_device = Column('seq_device', Boolean, nullable=False, default=False)
    step_seq_group  = Column('seq_group', Boolean, nullable=False, default=False)
    step_seq_nb = Column('seq_nb', Integer, nullable=False)
    step_related_to = Column('related_to', String(20))
    step_translations = Column('translations', String(1000))

    def __init__(self, install_inst_id, step_label, step_seq_nb, step_image=None, step_seq_device=None, step_seq_group=None):
        self.install_inst_id = install_inst_id
        self.step_label = step_label
        self.step_seq_nb = step_seq_nb
        if step_image is not None:
            self.step_image=step_image
        if step_seq_device is not None:
            self.step_seq_device=step_seq_device
        if step_seq_group is not None:
            self.step_seq_group=step_seq_group

    def __repr__(self):
        return '<Step %r>' % (self.seq_nb)

    def get_translation(self, lang):
        data_json = json.loads(self.step_translations)
        if lang in data_json:
            return data_json[lang]
        else:
            return None


def get_steps(install_inst_id):
    return db_session.query(Step).filter(Step.install_inst_id==install_inst_id).order_by(Step.step_seq_nb).all()

def get_steps_device(install_inst_id):
    return db_session.query(Step).filter(Step.install_inst_id==install_inst_id, Step.step_seq_device==1).order_by(Step.step_seq_nb).all()

def get_steps_group(install_inst_id):
    return db_session.query(Step).filter(Step.install_inst_id==install_inst_id, Step.step_seq_group==1).order_by(Step.step_seq_nb).all()