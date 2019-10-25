#
# Copyright (c) 2015
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
# THE SOFTWARE
#
from coils.core.logic import ActionCommand
from coils.logic.workflow.maps import MapFactory


class RunMapAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "run-map"
    __aliases__ = ['runMapAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._result_mimetype

    def do_action(self):

        self._result_mimetype = 'application/octet-stream'

        m = MapFactory.Marshall(
            context=self._ctx, name=self._map_name,
        )
        m.verify_input(self.input_mimetype)
        m.run(self.rfile, self.wfile)
        self._result_mimetype = m.result_mimetype
        m.close()

    def parse_action_parameters(self):
        self._map_name = self.process_label_substitutions(
            self.action_parameters.get('mapName')
        )
