# This file contains example model definitions.
from myorm import fields
from app import DbObject


class User(DbObject):

    def __repr__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.username)

    username = fields.CharField(max_length=250)
    first_name = fields.CharField(max_length=250)


class Address(DbObject):
    a = fields.IntegerField()
