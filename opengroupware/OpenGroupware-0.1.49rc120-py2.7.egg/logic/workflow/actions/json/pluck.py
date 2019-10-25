#
# Copyright (c) 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFRWARE
#
import json
from coils.core import ActionCommand, CoilsException


class PluckValueFromJSONAction(ActionCommand):
    __domain__ = "action"
    __operation__ = 'pluck-value-from-json'
    __aliases__ = ['pluckValueFromJSON', 'pluckValueFromJSONAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):
        data = json.load(self.rfile)
        self.log_message(
            'JSON data loaded, path for pick is "{0}"'.format(self._path, ),
            category='info',
        )
        if isinstance(data, list):
            self.log_message(
                'JSON data is a list, selecting first element of list',
                category='info',
            )
            if not len(data):
                raise CoilsException('JSON data is an empty list')
        for element in self._path.split('.'):
            data = data[element]
        if isinstance(data, basestring):
            self.wfile.write(data)
        else:
            json.dump(data, self.wfile, indent=2, )

    def parse_action_parameters(self):
        self._path = self.action_parameters.get('path')
        self._path = self.process_label_substitutions(self._path)

    def do_epilogue(self):
        pass
