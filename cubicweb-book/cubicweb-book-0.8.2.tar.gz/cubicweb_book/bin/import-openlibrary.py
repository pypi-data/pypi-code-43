#!/usr/bin/python
"""
to use this script:
cubicweb-ctl import-openlibrary.py authors.json.gz
"""
from __future__ import print_function

import sys
from gzip import GzipFile
from cubicweb import dbapi


def read_authors(filename):
    for line in GzipFile(authors):
        line = line.replace('": "', '": u"')  # read as unicode
        d = eval(line)
        yield d


if __name__ == '__main__':
    appid = sys.argv[1]
    authors = sys.argv[2]
    cnx = dbapi.connect(database=appid, user='admin', password='admin')
    cur = cnx.cursor()
    max = 1000
    rql = 'INSERT Person P: P surname %(name)s, P description %(key)s'
    for idx, author in enumerate(read_authors(authors)):
        try:
            cur.execute(rql, author)
        except Exception as exc:
            print(rql, author, exc)
            raise
        if idx % 100 == 0:
            cnx.commit()
            print('inserted %i authors...' % idx)
        if idx > max:
            break
    cnx.commit()
