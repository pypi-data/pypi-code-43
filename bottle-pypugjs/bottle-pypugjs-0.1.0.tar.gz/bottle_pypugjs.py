# coding: utf-8
# Created on:
# Author: Lorenzo A Garcia Calzadilla (lorenzogarciacalzadila@gmail.com)
#
# Copyright (c) 2018 Lorenzo A Garcia Calzadilla.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Este es un plugin de bottle para poder usar la libreria de mint en las vistas

Inicio rapido
-------------

Usando la funcion "template"
>>> template('test.pug', title = 'title', content = "")
'\\n<html>\\n  <head>\\n    <title>title</title>\\n  </head>\\n  <body>nocontent\\n\\n  </body>\\n</html>'
>>>
>>> template('| Hello {{ name }}!', name='World')
'Hello World!'
>>>
>>> template('html\\n\\tbody', name='World')
'\\n<html>\\n  <body></body>\\n</html>'
"""

from bottle import PluginError
from bottle import BaseTemplate, template as btemplate, view as bview, abort, SimpleTemplate
from pypugjs import simple_convert
import functools

__project__ = "bottle-pypugjs"
__autor__ = "2019, Lorenzo A. Garcia Calzadilla"
__version__ = "0.1.0"
__license__ = "MIT"

class PugTemplate(BaseTemplate):
    def __init__(self, *args,**keywords):
        self.extensions.insert(0, 'pug')
        super(PugTemplate, self).__init__(*args,**keywords)
    
    def prepare(self, **options):
        if not self.source:
            self.source = self.loader(self.name)
        #print(self.source)
        #print(simple_convert(self.source))
        self.tpl = SimpleTemplate(simple_convert(self.source))
        
    def render(self, *args, **kwargs):
        for dictarg in args:kwargs.update(dictarg)
        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults)
    
    def loader(self, name):
        if name == self.filename:
            fname = name
        else:
            fname = self.search(name, self.lookup)
        if not fname: abort(500, 'Template (%s) not found' % name)
        with open(fname, "rb") as f:
            return f.read().decode(self.encoding)

template = pug_template = functools.partial(btemplate, template_adapter=PugTemplate)
view = pug_view = functools.partial(bview, template_adapter=PugTemplate)

class PugPlugin(object):
    name = 'pug'
    api = 2

    def __init__(self, keyword="template"):
        self.keyword = keyword

    def setup(self, app):
        for other in app.plugins:
            if not isinstance(other, PugPlugin):
                continue
            if other.keyword == self.keyword:
                raise PluginError("Found another %s plugin with conflicting settings (non-unique keyword)." % self.name)
            elif other.name == self.name:
                self.name += '_%s' % self.keyword

    def apply(self, callback, route):
        conf = route.config.get(self.keyword) or None

        if not conf:
            return callback
        elif isinstance(conf, (tuple, list)):
            if len(conf) != 2:
                raise PluginError("%s takes exactly 2 arguments (%s given)" %(self.keyword, len(conf)))
            if not isinstance(conf[1], dict):
                raise PluginError("%s is not type dict" %(conf[1]))
        elif isinstance(conf, str):
            conf = (conf, {})
        else:
            raise PluginError("%s only type str, tuple or list" % self.keyword)

        return pug_view(conf[0], **conf[1])(callback)




Plugin = PugPlugin

if __name__ == '__main__':
    import doctest
    doctest.testmod()

