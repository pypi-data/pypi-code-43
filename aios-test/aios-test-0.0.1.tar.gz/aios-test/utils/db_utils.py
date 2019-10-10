# -*- coding: utf-8 -*-
from sqlalchemy.engine import create_engine


def get_engine(db_conn):
    return create_engine(db_conn)

def query_one(db_conn, sql):
    item = None
    with get_engine(db_conn).connect() as conn:
        item = conn.execute(sql).fetchone()
    return item

def query_many(db_conn, sql):
    items = None
    with get_engine(db_conn).connect() as conn:
        items = conn.execute(sql).fetchall()
    return items

def execute(db_conn, sql):
    items = None
    with get_engine(db_conn).connect() as conn:
        items = conn.execute(sql)
    return items

def convert_model(m_tuple: tuple):
    from aios.cls.model import ModelClass
    return ModelClass(id=m_tuple[0],
                      name=m_tuple[1],
                      tenant_id=m_tuple[2],
                      framework=m_tuple[3],
                      type=m_tuple[4],
                      path=m_tuple[5],
                      origin=m_tuple[6],
                      info=m_tuple[7],
                      size=m_tuple[8],
                      algorithm_type=m_tuple[9],
                      version=m_tuple[10],
                      format=m_tuple[11])


def convert_dataset(d_dict: dict):
    from aios.cls.dataset import DatasetClass
    return DatasetClass(id=d_dict.get('id'),
                        name=d_dict.get('name'),
                        tag=d_dict.get('uuid'),
                        data_id=d_dict.get('id'),
                        tenant_id=d_dict.get('tenantId'))