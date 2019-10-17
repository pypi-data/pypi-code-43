# pylint: disable=W0622
"""cubicweb-nosylist application packaging information"""


modname = 'cubicweb_nosylist'
distname = 'cubicweb-nosylist'

numversion = (0, 7, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'roundup like nosylist component for the CubicWeb framework'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {'cubicweb': '>= 3.24.0'}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python :: 3',
    'Programming Language :: JavaScript',
]
