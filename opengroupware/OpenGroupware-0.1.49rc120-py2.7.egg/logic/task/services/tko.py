#
# Copyright (c) 2013, 2014, 2015, 2017
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
# THE  SOFTWARE.
#
import os
import random
import time
import Queue
import logging
from coils.core import AdministrativeContext, ThreadedService, CoilsException
from event_worker import EventWorker
from collections import defaultdict

from events import \
    TASK_MODIFIED_NOTIFICATION, \
    TASK_RUN_NOTIFICATIONS, \
    TASK_NOTIFICATION_PROCESSED

# from utility import get_inherited_property

NOTIFICATION_TICK_DURATION = 31  # Seconds
NOTIFICATION_WAIT_DURATION = 60.0  # Seconds


class Notification(object):
    """
    This represents a object [Task] with notifications in the notification
    queue. Its purpose is to coalesce multiple events into a single
    notification object.
    """

    def __init__(self):
        self._created_timestamp = time.time()
        self._updated_timestamp = time.time()
        self._events = list()
        self._object_id = None

    @property
    def updated(self):
        """
        Timestamp of the most recent event registered for this object
        """
        return self._updated_timestamp

    @property
    def created(self):
        """
        Timestamp of the first event registered for this object
        """
        return self._created_timestamp

    @property
    def events(self):
        """
        List of registered events
        """
        return self._events

    @property
    def object_id(self):
        return self._object_id

    def register(self, payload):
        """
        Register an incoming event into the event list
        """
        self._updated_timestamp = time.time()
        object_id = payload.get('objectId', 0)
        if self._object_id is None:
            self._object_id = object_id
        elif self._object_id != object_id:
            raise CoilsException(
                'This registration event crosses entities.'
            )
        self._events.append(payload)


class PendingNotifications(object):

    def __init__(self):
        self._events = defaultdict(Notification)
        self.log = logging.getLogger('coils.task.event.notification')

    def register_event(self, object_id, payload, ):
        self._events[object_id].register(payload)

    def deregister_entity(self, object_id, ):
        if object_id in self._events:
            del self._events[object_id]

    def get_events(self):
        floor = time.time() - NOTIFICATION_WAIT_DURATION
        events = [
            event for event in self._events.values()
            if event.updated < floor
        ]
        for event in events:
            self.deregister_entity(event.object_id)
        return events


COMMAND_MAP = {
    TASK_MODIFIED_NOTIFICATION: None,
    TASK_RUN_NOTIFICATIONS: 'run_task_notifications',
}


class TKOService(ThreadedService):
    __service__ = 'coils.task.event'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def worker_name_generator(self):
        return 'coils.task.event.worker-{0}-{1}'.format(
            os.getpid(),
            ''.join([chr(random.randrange(65, 90)) for x in [1, 2, 3, 4, ]])
        )

    def setup(self, silent=True):
        ThreadedService.setup(self, silent=silent, )
        self._broker.subscribe(
            '{0}.notify'.format(self.__service__, ),
            self.receive_message,
            expiration=900000,
            queue_type='fanout',
            durable=False,
            exchange_name='OpenGroupware_Coils_Notify',
        )
        self.start_workers(
            count=4,
            classname=EventWorker,
            name_generator=self.worker_name_generator,
        )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext(
            {},
            broker=self._broker,
            component_name=self.__service__,
        )

        self._notification_queue = PendingNotifications()

        """
        There should be a much more efficient way than to poll, we need to
        go back to the previous mechanism where an wake up was only scheduled
        if there was a possibility of pending events - sometimes the server
        will be silent for long periods, and during those periods there is
        not reason to wake-up-to-check-for-events.
        """
        self.schedule_at_interval(
            'taskNotificationPoll',
            message=TASK_RUN_NOTIFICATIONS,
            seconds=NOTIFICATION_TICK_DURATION,
        )

    def process_service_specific_event(self, event_class, event_data):
        if event_class in COMMAND_MAP:
            method_name = COMMAND_MAP.get(event_class)
            if method_name:
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(event_data)
                else:
                    self.log.error(
                        'Method "{0}" mapped from event "{1}" does not exist.'.
                        format(method_name, event_class, ))
            else:
                self.log.info(
                    'Event "{0}" mapped as no-operation'.
                    format(event_class, ))
        else:
            self.log.warn(
                'Event "{0}" is not in command processing map'.
                format(event_class, )
            )

    def run_task_notifications(self, data):

        counter = 0

        events = self._notification_queue.get_events()

        for event in events:

            """
            And event in this case is a Notification object, not an audit log
            entity.  It is a composite of a possible series of events until
            the task became quiscent for a period of time.  The structure of
            the Notification.events property is a set of tuples having three
            value: (event, actor, audit_id, ) where event is the action tag
            [20_commented, 00_created, etc...], the actor is the object id
            of the context which performed tha ction, and audit id is the
            related entry in the audit table.
            """
            counter += 1
            self._work_queue.put(
                (
                    TASK_RUN_NOTIFICATIONS,
                    {
                        'objectId': event.object_id,
                        'events': event.events,
                    },
                    None,
                )
            )

        self.log.debug(
            'Requested event notifications for {0} tasks'.
            format(counter, )
        )

    #
    # Message Handlers
    #

    def do___audit_delete(self, parameter, packet):
        # No action, just eat it
        pass

    def do___audit_task(self, parameter, packet):

        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        actor_id = long(packet.data.get('actorId', 0))

        self.log.debug(
            'Recieved action "{0}" for task OGo#{1}'
            .format(action_tag, object_id, )
        )

        # Do not generate notifications for administrative events
        if actor_id == 10000:
            return

        try:

            if action_tag not in ('99_deleted', ):
                self._notification_queue.register_event(
                    object_id=object_id,
                    payload=packet.data,
                )
            elif action_tag in ('99_deleted', ):
                self._notification_queue.deregister_entity(object_id)
                self.log.debug(
                    'Deleting notifications for deleted task OGo#{0}'
                    .format(object_id, )
                )

        except Queue.Full:
            self.log.error('Unable to queue task event for processing')

        return

    #
    # Event handling
    #
