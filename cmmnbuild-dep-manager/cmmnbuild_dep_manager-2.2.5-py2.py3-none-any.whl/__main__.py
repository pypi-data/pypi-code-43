# -*- coding: utf-8 -*-
'''CommonBuild Dependency Manager

Copyright (c) CERN 2015-2017

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors:
    T. Levens   <tom.levens@cern.ch>
'''

import cmmnbuild_dep_manager
import logging
import six
import sys

if __name__ == '__main__':
    '''Provides a command line interface to cmmnbuild_dep_manager

    Any method of the cmmnbuild_dep_manager.Manager class can be called with
    string arguments. For example:

    $ python -m cmmnbuild_dep_manager install pytimber pyjapc
    $ python -m cmmnbuild_dep_manager list
    $ python -m cmmnbuild_dep_manager resolve

    '''
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    mgr = cmmnbuild_dep_manager.Manager()
    mgr.set_logging_level(logging.INFO)

    try:
        if len(sys.argv) >= 2:
            method = getattr(mgr, sys.argv[1])

            args = []
            kwargs = {}

            for a in sys.argv[2:]:
                if '=' in a:
                    k, v = a.split('=')
                    kwargs[k] = v
                else:
                    if len(kwargs):
                        raise SyntaxError('positional argument follows keyword argument')
                    args.append(a)

            ret = method(*args, **kwargs)
            if ret is not None:
                if isinstance(ret, six.string_types):
                    print(ret)
                elif hasattr(ret, '__iter__'):
                    for r in ret:
                        print(r)
                else:
                    print(ret)
        else:
            raise ValueError('a method name must be provided')
    except Exception as e:
        print('{0}: {1}'.format(type(e).__name__, e))
        sys.exit(1)
