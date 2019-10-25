#
# Copyright (c) 2010, 2014, 2015
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
from coils.core import CoilsException
from coils.core.logic import UpdateCommand
from keymap import COILS_TASK_KEYMAP
from command import TaskCommand
from flyweight import TaskFlyWeight


class UpdateTask(UpdateCommand, TaskCommand):
    __domain__ = "task"
    __operation__ = "set"

    def prepare(self, ctx, **params):
        self.keymap = COILS_TASK_KEYMAP
        UpdateCommand.prepare(self, ctx, **params)

    def _generate_difference_messages(self):
        '''
            self._ctx.audit_at_commit(
                object_id,
                '05_changed',
                self.message,
            )
        '''

        flyweight = TaskFlyWeight()

        attributes_to_compare = (
            'project_id', 'owner_id', 'name', 'start', 'end', 'kind',
            'keywords', 'sensitivity', 'priority', 'comment', 'actual',
            'total', 'travel',
        )

        for attribute in attributes_to_compare:
            setattr(flyweight, attribute, TaskFlyWeight.NOVALUE)

        flyweight.take_values(
            values=self.values,
            keymap=self.keymap,
            timezone=self.timezone,
        )

        for attribute in attributes_to_compare:
            if getattr(flyweight, attribute) == TaskFlyWeight.NOVALUE:
                continue
            if (
                not(
                    getattr(self.obj, attribute) ==
                    getattr(flyweight, attribute)
                )
            ):
                from_value_text = (
                    getattr(self.obj, attribute)
                    if getattr(self.obj, attribute) is not None
                    else ''
                )
                to_value_text = (
                    getattr(flyweight, attribute)
                    if getattr(flyweight, attribute) is not None
                    else ''
                )
                self._ctx.audit_at_commit(
                    object_id=self.obj.object_id,
                    action='05_changed',
                    message=(
                        'Value of "{0}" changed from "{1}" to "{2}"'
                        .format(
                            attribute,
                            from_value_text,
                            to_value_text,
                        )
                    ),
                    version=self.obj.version,
                )

    def run(self):
        self._generate_difference_messages()
        UpdateCommand.run(self)
        self.process_attachments()
        self.sanitize_values()
        self.obj.status = 'updated'
        if not self.verify_values():
            raise CoilsException('Illegal values in task entity.')
        self.apply_rules()
