#-*- coding:utf-8 -*-

from peewee import *

db = SqliteDatabase("demo.db")

class Company( Model ):
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
    db.create_tables([Company])
