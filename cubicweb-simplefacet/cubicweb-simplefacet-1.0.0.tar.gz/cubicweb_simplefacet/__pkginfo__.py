# pylint: disable=W0622
"""cubicweb-simplefacet application packaging information"""


modname = 'simplefacet'
distname = 'cubicweb-simplefacet'

numversion = (1, 0, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Cube adding another display for facets.'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {'cubicweb': '>= 3.24.0'}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python :: 3',
    'Programming Language :: JavaScript',
]

