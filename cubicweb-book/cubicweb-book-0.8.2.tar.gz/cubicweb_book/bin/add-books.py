#!/usr/bin/python
"""
add-books script

$ python add-books.py myolib python programming

will search openlibrary for books about "python programming" and add all the
results to the myolib cubicweb instance.
"""
from __future__ import print_function

import sys
from cubicweb import dbapi
from cubicweb_book import olapi


def get_books(phrase):
    books = []
    for key in olapi.search_books(phrase):
        books.append(olapi.openlibrary_get(key))
    return books


if __name__ == '__main__':
    appid = sys.argv[1]
    phrase = ' '.join(sys.argv[2:])
    cnx = dbapi.connect(database=appid, user='admin', password='admin')
    cur = cnx.cursor()
    print('looking for books...')
    books = get_books(phrase)
    print('%i books found.' % len(books))
    for idx, book in enumerate(books):
        print('adding %s...' % book['key'])
        if 'isbn_13' in book:
            print('by isbn_13.')
            cur.execute('INSERT Book B: B isbn13 %(isbn)s',
                        {'isbn': book['isbn_13'][0]})
        elif 'isbn_10' in book:
            print('by isbn_10.')
            cur.execute('INSERT Book B: B isbn10 %(isbn)s',
                        {'isbn': book['isbn_10'][0]})
        else:
            print('no isbn found.')
        if idx % 10 == 0:
            cnx.commit()
    cnx.commit()
