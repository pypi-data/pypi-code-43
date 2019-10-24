# This file is needed to initialize the models and migrations
import os
from myorm.dbobject import DbObject
from myorm.adaptors.sqlite import SQLiteAdaptor
from myorm.migrations import Migration

from models import *

DbObject.adaptor = SQLiteAdaptor('myorm.db')

# Examples for other DBMS

# MySQL
# from myorm.adaptors.mysql import MySQLAdaptor
# DbObject.adaptor = MySQLAdaptor(
#     {'host': 'localhost', 'user': 'myorm', 'db': 'myorm', 'use_unicode': True, 'charset': 'utf8'}
# )

Migration.migration_dir = os.path.join(os.getcwd(), 'migrations')
