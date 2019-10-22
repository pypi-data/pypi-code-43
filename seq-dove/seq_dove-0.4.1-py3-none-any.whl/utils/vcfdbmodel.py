'''
VCF model for mongodb
'''
from mongoengine import *
import datetime



class BasicEntry(Document):
    entry = StringField()


class ListEntry(Document):
    variant = ListField(ReferenceField(BasicEntry))


class MongoVcf(Document):
    entry_date = DateTimeField(default=datetime.datetime.now)
    meta_info = ListField(ReferenceField(ListEntry), required=True)
    sample_names = ListField(ReferenceField(BasicEntry), required=True)
    columns = ListField(ReferenceField(BasicEntry), required=True)
    data = ListField(ReferenceField(ListEntry), required=True)
    panel = StringField(required=True)
