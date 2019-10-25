#
# Copyright (c) 2010, 2013, 2014, 2015, 2016
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
from coils.core import \
    OGO_ROLE_SYSTEM_ADMIN, \
    CoilsException, \
    get_yaml_struct_from_project7000
from coils.core.logic import ActionCommand
from coils.foundation import coils_json_encode


def retrieved_archive_task_rules(context):

    kind_map = get_yaml_struct_from_project7000(
        context, '/TaskRetention.yaml',
    )
    if not kind_map:
        return dict()
    return kind_map


class ArchiveOldTasksAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "archive-old-tasks"
    __aliases__ = ['archiveOldTasks', "archiveOldTasksAction", ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/json'

    def parse_action_parameters(self):
        pass

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise CoilsException(
            'Insufficient privilages to invoke archiveOldTasksAction'
        )

    def do_action(self):

        record = dict()

        configuration = retrieved_archive_task_rules(self._ctx)
        for kind, config in configuration.items():
            archive_days = config.get('autoArchiveThreshold', 180)
            result = self._ctx.run_command(
                'task::batch-archive',
                age=archive_days,
                fix_completion_dates=True,
                kind=kind,
            )
            record[kind] = result
        coils_json_encode(record, self.wfile, )
