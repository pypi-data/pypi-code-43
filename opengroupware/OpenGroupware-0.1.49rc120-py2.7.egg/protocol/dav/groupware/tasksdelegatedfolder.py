#
# Copyright (c) 2010, 2012, 2013, 2014
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
from taskobject import TaskObject
from tasksfolder import TasksFolder


class TasksDelegatedFolder(TasksFolder):

    def __init__(self, parent, name, **params):
        TasksFolder.__init__(self, parent, name, **params)

    def get_ctag(self):
        return self.get_ctag_for_collection()

    def _load_contents(self):
        for task in self.context.run_command('task::get-delegated'):
            if not self._check_entity_filter(task):
                continue
            alias = self._make_task_alias(task)
            self.insert_child(
                task.object_id,
                TaskObject(
                    self, unicode('{0}.ics'.format(task.object_id, )),
                    context=self.context,
                    request=self.request,
                    entity=task,
                ),
                alias=alias,
            )
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if self.is_loaded:
            if self.has_child(name):
                return self.get_child(name)
        task = self.manager.find(name, request=self.request, )
        if task:
            return TaskObject(
                self, name,
                context=self.context,
                request=self.request,
                entity=task,
            )
        self.no_such_path()
