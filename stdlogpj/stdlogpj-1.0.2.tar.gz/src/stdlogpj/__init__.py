# -*- coding: iso-8859-1 -*-

"""python logging done my way"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2019, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


from .stdlog import standard_logging_setup


__author__    = 'Pete R. Jemian'
__email__     = 'prjemian@gmail.com'
__copyright__ = '2019, Pete R. Jemian'

__package_name__ = 'stdlogpj'

__license_url__  = 'http://creativecommons.org/licenses/by/4.0/deed.en_US'
__license__      = 'Creative Commons Attribution 4.0 International Public License (see LICENSE file)'
__description__  = 'python logging done my way'
__author_name__  = __author__
__author_email__ = __email__
__url__          = u'https://github.com/prjemian/stdlogpj'
__keywords__     = ['python', 'logging']
__zip_safe__     = True
__python_version_required__ = ">=3.5"

__install_requires__ = []

__classifiers__ = [
     'Development Status :: 5 - Production/Stable',
     'Environment :: Console',
     'Intended Audience :: Science/Research',
     'License :: Freely Distributable',
     'License :: Public Domain',
     'Programming Language :: Python',
     'Programming Language :: Python :: 3.6',
     'Programming Language :: Python :: 3.7',
     'Topic :: Software Development',
     'Topic :: Utilities',
   ]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
