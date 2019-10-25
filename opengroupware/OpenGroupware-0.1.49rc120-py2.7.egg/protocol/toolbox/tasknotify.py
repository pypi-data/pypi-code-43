
# Copyright (c) 2014
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
    NoSuchPathException, \
    SQLConnectionFactory, \
    fill_project7000_template, \
    CoilsException

from coils.net import PathObject

from coils.logic.task.services.utility import \
    do_task_notification_preamble, \
    get_name_dictionary_matching_events, \
    send_task_notification_message, \
    EndTemplateException, \
    end_template


class TaskNotifyDemo(PathObject):
    """
    For testing of task notification templates

    URI paramters:
        objectId
        sentTo - presense inidcates that an e-mail should be sent
        floorSeconds - age of events to be included, default is ~1 year
        floorObjectId  - what the object id floor is for included events
    """

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return False

    def do_GET(self):

        """Parse URL parameters"""

        send_to = None
        if 'sendTo' in self.parameters:
            send_to = self.parameters['sendTo']

        try:
            object_id = int(self.parameters['objectId'][0])
        except:
            raise CoilsException(
                'objectId parameter required in paramter string'
            )

        if 'floorSeconds' in self.parameters:
            try:
                floor_seconds = long(self.parameters['floorSeconds'][0])
            except:
                raise CoilsException(
                    'floorSeconds must be a numeric value [seconds]'
                )
        else:
            floor_seconds = 86400 * 366

        if 'floorObjectid' in self.parameters:
            try:
                floor_object_id = long(self.parameters['floorObjectId'][0])
            except:
                raise CoilsException(
                    'floorObjectId must be a numeric value [objectId value]'
                )
        else:
            floor_object_id = None

        """Marshall task and perform notification preamble"""

        task, events, template, notification_addresses, to_address, = \
            do_task_notification_preamble(
                context=self.context,
                logger=self.log,
                object_id=object_id,
                floor_object_id=floor_object_id,
                floor_seconds=floor_seconds,
            )

        if not task:
            raise NoSuchPathException(
                'Unable to marshall task OGo#{0}'.format(object_id, )
            )

        if not template:
            raise NoSuchPathException(
                'Unable to marshall task notification template'
            )

        """Marshall object required for template completion"""

        names = get_name_dictionary_matching_events(self.context, events)

        owner = self.context.type_manager.get_entity(task.owner_id)

        executor = self.context.type_manager.get_entity(task.executor_id)

        """Generate the notification payload"""

        event_counter = 0
        try:
            content = fill_project7000_template(
                context=self.context,
                template_document=template,
                parameters={
                    'to_header': ','.join(notification_addresses),
                    'task': task,
                    'owner': owner,
                    'executor': executor,
                    'events': events,
                    'names': names,
                    'sql_connection_factory': SQLConnectionFactory,
                    'end_template': end_template,
                    'event_counter': event_counter,
                },
            )
        except EndTemplateException as exc:
            self.request.simple_response(
                200,
                mimetype='text/plain',
                data='Template self-terminated via EndTemplateException',
            )
            return

        """
        A sentTo was specified, so generate the e-mail message, just as
        the coils.task.event service worker would do.
        """

        if send_to:
            send_task_notification_message(
                context=self.context,
                events=events,
                to_address=send_to,
                template=template,
                task=task,
                notification_addresses=notification_addresses,
            )

        """
        Return the content to the client.
        """

        self.request.simple_response(
            200,
            mimetype='text/html',
            data=content,
        )
