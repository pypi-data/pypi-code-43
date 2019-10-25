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
import json
from StringIO import StringIO
from datetime import datetime, timedelta
from coils.foundation import CTag
from coils.core import \
    Appointment, \
    CoilsException, \
    NotImplementedException, \
    Task
from coils.net import \
    DAVObject, \
    DAVFolder, \
    OmphalosCollection, \
    OmphalosObject, \
    StaticObject, \
    Parser, \
    Multistatus_Response
from taskobject import TaskObject
from rss_feed import TasksRSSFeed
from groupwarefolder import GroupwareFolder
import coils.core.omphalos as omphalos
from coils.core.icalendar import Parser as VEvent_Parser
from coils.protocol.dav.managers import DAVTaskManager, mimestring_to_format
from tasksfolder import TasksFolder
from taskstodofolder import TasksToDoFolder
from tasksdelegatedfolder import TasksDelegatedFolder

STATIC_KEYS = {
    'ToDo': TasksToDoFolder,
    'Delegated': TasksDelegatedFolder,
}


from tasksfolder import TasksFolder


class TasksRootFolder(TasksFolder):

    def __init__(self, parent, name, **params):
        TasksFolder.__init__(self, parent, name, **params)

    def supports_DELETE(self):
        return False

    def get_ctag(self):
        return self.get_ctag_for_entity('Job')

    def _load_contents(self):
        for key, value in STATIC_KEYS.items():
            self.insert_child(
                key,
                value(
                    self, key, context=self.context, request=self.request,
                )
            )
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name.startswith('.'):
            function_name = \
                'render_key_{0}'.format(name[1:].lower().replace('.', '_'))
            if hasattr(self, function_name):
                return getattr(self, function_name)(
                    name,
                    is_webdav=is_webdav,
                    auto_load_enabled=auto_load_enabled, )
            else:
                self.no_such_path()
        self.load_contents()
        x = self.get_child(name, )
        if x:
            return x
        task = self.manager.find(name, request=self.request, )
        if task:
            return TaskObject(
                self, name,
                context=self.context,
                request=self.request,
                entity=task,
            )
        self.no_such_path()
