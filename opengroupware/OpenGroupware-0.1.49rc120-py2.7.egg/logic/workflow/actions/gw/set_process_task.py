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
# THE SOFTWARE.
#
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from coils.core.xml import Render as XML_Render


class SetProcessTaskAction(ActionCommand):
    __domain__ = 'action'
    __operation__ = 'set-process-task'
    __aliases__ = ['setProcessTask', 'setProcessTaskAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        task = self._ctx.r_c('task::get', id=self._task_id, )
        if not task:
            raise CoilsException(
                'Cannot marshal task OGo#{0} to make it the process task'
                .format(self._task_id, )
            )
        self.process.task_id = task.object_id
        comment = (
            'This task has been set as the process task '
            'for OGo#{0} [Process]\n'
            .format(self.process.object_id, )
        )
        if self.process.route:
            comment += (
                'Route OGo#{0} "{1}"'
                .format(
                    self.process.route.object_id, self.process.route.name,
                )
            )

        self._ctx.r_c(
            'task::comment',
            task=task,
            values={'comment': comment, }
        )

        results = XML_Render.render(task, self._ctx)
        self.wfile.write(results)
        self.wfile.flush()

    def _get_attribute_from_params(self, name, default=None):
        x = unicode(self.action_parameters.get(name, default))
        return unicode(self.process_label_substitutions(x))

    def parse_action_parameters(self):
        self._task_id = self._get_attribute_from_params('taskId')
        if not self._task_id:
            raise CoilsException(
                'Parameter taskId is required for action setProcessTaskAction'
            )
        try:
            self._task_id = long(self._task_id)
        except:
            raise CoilsException(
                'Parameter taskId must be an integer [objectId] value'
            )
