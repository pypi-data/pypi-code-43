#!/usr/bin/env python
# Copyright (c) 2014, 2015
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
from coils.core import Contact, Team
from coils.core import Command


class GetTaskNotificationList(Command):
    """
    Returns a list of CompanyValue objects for contacts which should be
    notified of a task event.  Optionally a list may be provided of
    entities to exclude from notification.
    """
    __domain__ = "task"
    __operation__ = "get-notification-list"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.obj = params.get('task', None, )
        self.exclude_ids = params.get('exclude_ids', list())

    def run(self, **params):

        """
        The email1 CompanyValue objects will be accumulated from task's
        owner and executor.  If the executor is a team then email1 will
        be accumulated for every member of the team. Finally accumulate the
        email1 for every target of a "coils:watch" from the task.
        WARN: there does not appear to be anything here to prevent duplicates.

7        """

        to_addresses = list()

        """Owner"""
        if not self.obj.owner_id <= 10000:
            owner = self._ctx.type_manager.get_entity(self.obj.owner_id)
            if isinstance(owner, Contact):
                address = owner.get_company_value('email1')
                if address and owner.object_id not in self.exclude_ids:
                    to_addresses.append(address)
            else:
                self.log.info(
                    'Owner of task OGo#{0} is OGO#{1}, not a Contact, '
                    'is an unexpected entity type of {2}'
                    .format(
                        self.obj.object_id, self.obj.owner_id, type(owner),
                    )
                )
        else:
            owner = None

        """ Executor """
        if not self.obj.executor_id <= 10000:
            executor = self._ctx.type_manager.get_entity(self.obj.executor_id)
            if isinstance(executor, Team):
                for assignment in executor.members:
                    contact = self._ctx.type_manager.get_entity(
                        assignment.child_id
                    )
                    if isinstance(contact, Contact):

                        """Do not include the Administrator"""
                        if contact.object_id <= 10000:
                            continue

                        address = contact.get_company_value('email1')
                        if (
                            address and
                            contact.object_id not in self.exclude_ids
                        ):
                            to_addresses.append(address)
                    else:
                        self.log.info(
                            'Executor (via team membership) of task OGo#{0} '
                            'is OGO#{1} (via team OGo#{2}) is not a Contact '
                            'is unexpected entity of type {2}'
                            .format(
                                self.obj.object_id,
                                assignment.child_id,
                                self.obj.executor_id,
                                type(contact), )
                        )
            elif isinstance(executor, Contact):
                address = executor.get_company_value('email1')
                if address and executor.object_id not in self.exclude_ids:
                    to_addresses.append(address)
            else:
                self.log.info(
                    'Executor of task OGo#{0} is OGO#{1}, not a Contact '
                    'or Team, is unexpected entity of type {2}'
                    .format(
                        self.obj.object_id, self.obj.owner_id, type(owner),
                    )
                )
        else:
            executor = None

        """Links"""
        links = self._ctx.link_manager.links_from(self.obj)
        for link in [x for x in links if x.kind == 'coils:watch']:
            target = self._ctx.type_manager.get_entity(link.target_id)
            if isinstance(target, Contact):
                address = target.get_company_value('email1')
                if address and target.object_id not in self.exclude_ids:
                    to_addresses.append(address)
            else:
                self.log.info(
                    'Target of coils:watch link from task OGo#{0} is OGO#{1}, '
                    'not a Contact, is unexpected entity of type {2}'
                    .format(
                        self.obj.object_id, self.obj.owner_id, type(owner),
                    )
                )

        self.set_return_value(to_addresses)
