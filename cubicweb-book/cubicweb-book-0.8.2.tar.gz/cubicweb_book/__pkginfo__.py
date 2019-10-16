# pylint: disable-msg=W0622
"""cubicweb-book application packaging information"""

modname = 'book'
distname = 'cubicweb-%s' % modname

numversion = (0, 8, 2)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
description = 'component to describe books for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
long_desc = """
This cube provides the entity type ``Book`` and uses the OpenLibrary API_
to automatically fill the book's description

Check out : `Fetching book descriptions and covers`_

.. _`Fetching book descriptions and covers` : http://www.logilab.org/blogentry/9138
.. _API : http://openlibrary.org/dev/docs/api
"""
web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'cubicweb': '>= 3.24.0',
               'cubicweb-addressbook': None,
               'cubicweb-person': None,
               'cubicweb-file': None,
               }
