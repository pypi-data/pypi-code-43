# coding: utf-8
from sqlalchemy import Date, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, MEDIUMINT
from common.model_helper import DictAble, QuickSave, CacheSave
from configs.db_config import db
from time import clock


class PriMac(db.Model, QuickSave, CacheSave):
    __tablename__ = 'primac'

    mac = db.Column(BIGINT(20), primary_key=True)
    xixi = db.Column(INTEGER(11), server_default=text("'11111111'"))
    str1 = db.Column(Text)
    str2 = db.Column(Text)
    str3 = db.Column(Text)
    str4 = db.Column(Text)
    str5 = db.Column(Text)
    str6 = db.Column(Text)
    str7 = db.Column(Text)
    str8 = db.Column(Text)
    str9 = db.Column(Text)
    str10 = db.Column(Text)
    str11 = db.Column(Text)
    str12 = db.Column(Text)


# class BigJson(db.Model, DictAble, QuickSave, CacheSave):
#     __tablename__ = 'big_json'
#
#     mac = db.Column(BIGINT(20), primary_key=True)
#     xixi = db.Column(INTEGER(11), server_default=text("'11111111'"))
#     time = db.Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
#     str1 = db.Column(Text)


if __name__ == '__main__':
    from configs.db_config import session_factory
    session = session_factory()
    ONE = 1001
    result = []
    i = 0
    start = clock()
    temp = session.query(BigJson).all()
    result.append(temp)
    end = clock()
    print(end-start)