#-*- coding:utf-8 -*-

from peewee import *

db = SqliteDatabase("demo.db")

class Company( Model ):
    '''
    公司表模型
    en_name 英文名称
    cn_name 中文名称
    rank 排名
    revenues 收益
    profits 利润
    assets 资产
    employees 雇员数量
    '''
    en_name = CharField()
    cn_name = CharField(null=True)
    rank = IntegerField()
    revenues = FloatField()
    profits = FloatField()
    assets = FloatField()
    employees = IntegerField()

    class Meta:
        database = db

def create_database():
    #创建数据库表Company
    db.create_tables([Company])
