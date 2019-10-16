"""template automatic tests"""

from cubicweb.devtools.testlib import AutomaticWebTest
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.fill import ValueGenerator

import random


def random_numbers(size):
    return u''.join(random.choice('0123456789') for i in range(size))


class MyValueGenerator(ValueGenerator):
    def generate_Book_isbn10(self, entity, index):
        return random_numbers(10)

    def generate_Book_isbn13(self, entity, index):
        return random_numbers(13)


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Book', 'Collection', 'Editor'))

    def list_startup_views(self):
        return ()


class ViewTC(CubicWebTC):

    def test_author_view(self):
        with self.admin_access.web_request() as req:
            jdoe = req.create_entity('Person', surname=u'jdoe')
            req.create_entity('Book', title=u'book', authors=jdoe)
            # should not raise
            jdoe.view('author-biblio')


if __name__ == '__main__':
    import unittest
    unittest.main()
