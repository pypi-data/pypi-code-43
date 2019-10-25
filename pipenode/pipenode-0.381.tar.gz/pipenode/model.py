# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from os import sys, path
from copy import deepcopy
from sqlalchemy import and_
from contextlib import closing
from datetime import datetime
import time

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from sqlalchemy import (MetaData, Table, create_engine, Column, Integer, String, DATETIME,
                        Date, DateTime, TEXT, TIME, DATE, TIMESTAMP, PrimaryKeyConstraint)

from utils.logger import RotatingLogger

logger = RotatingLogger().logger

try:
    from extensions.sqlalchemydb import SqlalchemyHelper
except:
    from .extensions.sqlalchemydb import SqlalchemyHelper

sqlhelp = SqlalchemyHelper(DB_DATABASE_NAME='django_admin')
db_session_mk = sqlhelp.get_session_mk()


class DjangoJob(sqlhelp.Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(24), nullable=False, index=True, unique=True)
    name = Column(TEXT)
    next_run_time = Column(TIMESTAMP(True))
    started = Column(TIMESTAMP(True))
    recent = Column(TIMESTAMP(True))
    job_config = Column(String(256), nullable=True)

    def __str__(self):
        status = 'next run at: %s' % self.next_run_time if self.next_run_time else 'paused'
        return '%s (%s)' % (self.name, status)


def get_or_create(job_store):
    JobTable = sqlhelp.get_ad_stat_model(pre='django', aid='aps', modelobj=DjangoJob)
    sqlhelp.create_all()
    db_session = db_session_mk()
    now = time.time()
    try:
        job_store['recent'] = datetime.fromtimestamp(int(time.time()))
        job_execution = JobTable(**deepcopy(job_store))
        q_dict = SqlalchemyHelper().serialize(job_execution)
        if not db_session.query(JobTable)\
                .filter(and_(JobTable.name == job_store['name'], JobTable.uid == job_store['uid']))\
                .first():
            db_session.add(job_execution)
        else:
            db_session.query(JobTable)\
                .filter(and_(JobTable.name == job_store['name'], JobTable.uid == job_store['uid']))\
                .update(q_dict)
        db_session.commit()
        logger.info('get_or_create: %s, %s' % (job_execution, job_store))
    except Exception as exc:
        logger.error("flush db error: %s" % exc)
        db_session.rollback()
    finally:
        db_session.close()
