#!/usr/bin/env python
##########################################################################
# $Id: turbine_mongo_archiver.py 4480 2013-12-20 23:20:21Z boverhof $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
###########################################################################
import urllib.request
import urllib.error
import csv
import sys
import os
from configparser import ConfigParser
import json
import optparse
import sys
import pyodbc


SECTION = "Archiver"


def run(**kw):
    conn_str = "DRIVER={SQL Server};SERVER=%(server)s;DATABASE=%(database)s;UID=%(userid)s;PWD=%(password)s" % kw
    print(conn_str)
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    print(cursor)
    return cursor


def main(args=None):
    """consumer mongo archiver
    """
    op = optparse.OptionParser(
        usage="USAGE: %prog [options] CONFIG_FILE", description=main.__doc__)
    (options, args) = op.parse_args()

    cp = ConfigParser()
    cp.read(args[0])

    run(server=cp.get(SECTION, 'server'), database=cp.get(SECTION, 'database'),
        userid=cp.get(SECTION, 'userid'), password=cp.get(SECTION, 'password'))


if __name__ == "__main__":
    main()
