# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:48:03 2019

@author: jazzn
"""

import sqlite3
import pandas as pd
import os.path
from prettytable import PrettyTable

class Sql():
    def __init__(self,file_name):
        assert os.path.isfile(file_name),"file doesn't exist"
        self.file = file_name
        self.conn = sqlite3.connect(file_name)
        self.tables = self.get_tables()
        print(f"database {file_name} connected ...")
        for t in self.tables:
            print(f'table ... {t} :')
            self.display_columns(t)
    
    
    def get_tables(self):  
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        out = [item for t in cursor.fetchall() for item in t] 
        return out

    def display_columns(self,table):
        x = PrettyTable()
        x.add_column('Descriptors',self.get_columns(table))
        print(x)
    
    def get_columns(self,table):
        cursor = self.conn.execute(f'select * from {table}')
        return [description[0] for description in cursor.description]
    
    def execute(self,sql_qer):
        c = self.conn.execute(sql_qer)
        df = pd.read_sql_query(sql_qer, self.conn)
        return df