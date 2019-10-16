#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : DB.py
#   Created Time  : 2019-09-19 16:31
#   Last Modified : 2019-09-27 14:45
#   Describe      :
#
# ====================================================
"""usage: DB.py
some functions to operate the data base
1.insertDB(var type: list of tuple)
  insert some information to the data base
"""

import sqlite3
from sqlite3 import OperationalError
import os
# import time
from core.config import local_config
query = """
CREATE TABLE IF NOT EXISTS fileInfo
(id INTEGER PRIMARY KEY, 
 address text, 
 trashAddress text, type text,
time real, date text, exits text)
"""


# @profile
def initDB():
    conn = sqlite3.connect(local_config.get('core', 'data_base_file'))
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.execute("CREATE index  fileInfoIndex on fileInfo(id) ")
        conn.commit()
    # except Exception:
    #    pass
    finally:
        conn.close()
    return


# @profile
def lastID():
    conn = sqlite3.connect(local_config.get('core', 'data_base_file'), timeout=30.0)
    ID = 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fileInfo ORDER BY id DESC limit 1")
        rows = cursor.fetchall()
        if rows:
            ID = rows[0][0]
    finally:
        cursor.close()
        conn.close()
    return ID

#@profile
def insertDB(information):
    # add ID
    ID = lastID() + 1
    # print ID
    IDinfo = []
    for indx, item in enumerate(information):
        # print "id:", indx, "item",  item
        IDinfo.append((ID + indx, ) + item)
    conn = sqlite3.connect(local_config.get('core', 'data_base_file') )
    insertmt = 'INSERT INTO fileInfo VALUES(?, ?, ?, ?, ?, ?, ?)'
    # print IDinfo
    cursor = conn.cursor()
    cursor.execute("begin transaction")
    try:
        cursor.executemany(insertmt, IDinfo)
    except OperationalError as e:
        if "database is locked" in e:
            print("fun<insertDB>", "OperationalError :", e)
            insertDB(information)
        if "no such table" in e:
            print("OperationalError :", e)
            cursor.execute(query)
            cursor.executemany(insertmt, IDinfo)
            conn.commit()
    # except Exception as e:
    #    print "fun<insertDB>", e
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def getAllInf():
    """
    get all information from the data base
    """
    con = sqlite3.connect(local_config.get('core', 'data_base_file'),
                          timeout=30.0)
    cursor = con.cursor()
    cursor = con.execute("SELECT * FROM fileInfo")
    rows = cursor.fetchall()
    return rows


def getLastRecord(n):
    """
    get the record of last #n
    """
    con = sqlite3.connect(local_config.get('core', 'data_base_file'),
                          timeout=30.0)
    cursor = con.cursor()
    cursor.execute(
        "SELECT * FROM fileInfo ORDER BY id DESC limit {}".format(n))
    rows = cursor.fetchall()
    cursor.close()
    con.close()
    return rows


def get_record_by_id(ID):
    """
    get the record with certain ID 
    """
    con = sqlite3.connect(local_config.get('core', 'data_base_file'))
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM fileInfo WHERE id = {}".format(ID))
        rows = cursor.fetchall()
    finally:
        cursor.close()
    con.close()
    return rows


def clearDB():
    con = sqlite3.connect(local_config.get('core', 'data_base_file'),
                          timeout=30.0)
    delQuery = "DELETE from fileInfo"
    try:
        cursor = con.cursor()
        cursor.execute(delQuery)
        con.commit()
    # except Exception as e:
    #     print "fun<clearDB>", e
    finally:
        con.close()


def delByID(Id):
    """
    Args:
        Id: the Index the the one creod 
    return:
        void
    """
    con = sqlite3.connect(local_config.get('core', 'data_base_file'),
                          timeout=30.0)
    try:
        cursor = con.cursor()
        delQuery = "DELETE from fileInfo WHERE id=?"
        cursor.execute(delQuery, (Id, ))
        con.commit()
    # except Exception as e:
    #    print "fun<delByID>", e
    finally:
        con.close()


# initi the fileInfo.config.db
if not os.path.isfile(local_config.get('core', 'data_base_file')):
    initDB()
if __name__ == "__main__":
    if not os.path.isfile(local_config.get('core', 'data_base_file')):
        initDB()
    print(lastID())
    exit()

    for inf in getAllInf():
        print(inf)
    print(lastID())
    print(get_record_by_id(1))
