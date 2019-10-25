#
# Copyright (c) 2013, 2014, 2017
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
import logging
import traceback
from coils.core import \
    MultiProcessWorker, \
    AdministrativeContext

from utility import \
    do_task_notification_preamble, \
    send_task_notification_message, \
    EndTemplateException

from events import \
    TASK_MODIFIED_NOTIFICATION, \
    TASK_RUN_NOTIFICATIONS, \
    TASK_NOTIFICATION_PROCESSED

GLOBAL_NOTIFICATION_ADDRESS = None


COMMAND_MAP = {
    TASK_RUN_NOTIFICATIONS: 'send_task_notification',
}


"""
  EVENT : TASK NOTIFICATION
  event_worker:do_send_task_notification
    task, events, template, notification_addresses, to_address, = \
        do_task_notification_preamble(self.context, log, object_id, )
      events = get_qualifying_task_events( ... )
      template = get_task_notification_template( ... )
      notification_addresses, to_address, = get_notification_list(...)
    -- bail out if no data or events
    -- bail out if notification disabled
    -- stage notificaiton log message [if commit occurs]
    message_id = send_task_notification_message( ... )
      get_name_dictionary_matching_events
      -- gets owner
      -- gets executor
      -- creates subject
      send_email_using_project7000_template
    update_notification_marker
    commit
"""


class EventWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, silent=True):
        MultiProcessWorker.__init__(self, name, work_queue, event_queue, )
        self.context = AdministrativeContext(
            {},
            component_name=name,
        )

    def process_worker_message(self, command, payload, ):

        object_id = long(payload.get('objectId', 0))

        self.log.debug(
            'received command {0} for OGo#{1}'. format(command, object_id, )
        )
        if command in COMMAND_MAP:
            method = 'do_{0}'.format(COMMAND_MAP[command], )
            if hasattr(self, method):
                method = getattr(self, method)
                if method:
                    method(payload, )
            else:
                self.log.error(
                    'Command received with no corresponding implementation; '
                    'looking for "{0}"'.format(method, )
                )
        else:
            self.log.error(
                'Unmapped command "{0}" received.'.format(command, )
            )
        self.context.db_close()

    def do_send_task_notification(
        self,
        payload,
    ):
        """
        PAYLOAD = {
          objectId:
          events: [
            {'auditId':   695872193,      # objectId of audit log entry
             'kind':      'process',      # lower-case entity type
             'objectId':  695872156,      # objectId of affected entity
             'actorId':   10100,          # objectId of actor (user)
             'projectId': 0               # related project object id
             'action':    '00_created',   # action code (00_created,...)
             'version':   None,           # Revision of the entity
             'message':   'Process created' }, ... ]
        }
        """

        def update_notification_marker(context, task, events):
            context.property_manager.set_property(
                entity=task,
                namespace='817cf521c06b47228392a0437daf81e0',
                attribute='lastNotificationMaximum',
                value=max([event[0] for event in events]),
            )
            return

        object_id = long(payload.get('objectId', 0))
        actions = payload.get('events', None, )

        self.log.debug(
            'processing {0} events for task OGo#{1}'
            .format(len(actions), object_id, )
        )

        log = logging.getLogger(
            'coils.task.event.notification.{0}'.format(object_id, )
        )

        task, events, template, notification_addresses, to_address, = \
            do_task_notification_preamble(self.context, log, object_id, )

        if not task or not events or not template or not to_address:
            if not task:
                log.debug(
                    'Task OGo#{0} cannot be marshalled, '
                    'no notifications will be generated'
                    .format(object_id, )
                )
            elif not events:
                log.debug(
                    'No events for notification related to OGo#{0}, '
                    'no notifications will be generated'
                    .format(object_id, )
                )
            elif not template:
                log.debug(
                    'No notification template found for OGo#{0}, '
                    'no notifications will be generated'
                    .format(object_id, )
                )
            elif not to_address:
                log.debug(
                    'No notification targets found for OGo#{0}, '
                    'no notifications will be generated'
                    .format(object_id, )
                )

            self.enqueue_event(
                TASK_NOTIFICATION_PROCESSED,
                (object_id, ),
            )

            return

        """
        If task.notify is None or Zero then task notification is disabled,
        no notification processing should be performed.
        """
        if not task.notify:
            log.debug(
                'Notifications disabled for OGo#{0} [Task], '
                'no notifications will be generated'
                .format(object_id, )
            )

            self.enqueue_event(
                TASK_NOTIFICATION_PROCESSED,
                (object_id, ),
            )

            return

        self.context.audit_at_commit(
            object_id=task.object_id,
            action='notification',
            message=(
                'Generated notification message to: {0}'
                .format(','.join(to_address), )
            )
        )

        """Send Message"""

        try:

            log.debug('sending task notification message')
            message_id = send_task_notification_message(
                context=self.context,
                events=events,
                to_address=to_address,
                template=template,
                task=task,
                notification_addresses=notification_addresses,
            )
            log.debug('task notification message send call completed')

        except EndTemplateException as exc:
            """
            Template chose to end, no notification will be generated. This
            permits events to be examined in template logic, under the control
            of the site-administrator, and if nothing interesting is found to
            bail out without generating an error message or a notification.
            """
            self.log.info(
                'Template self-terminated for notification of OGo#{0} '
                'with message "{1}"'
                .format(task.object_id, exc.message, )
            )

            update_notification_marker(self.context, task, events)
            self.context.commit()

        except Exception as exc:

            self.log.error(
                'An exception occurred generating task notification '
            )
            self.log.exception(exc)
            self.send_administrative_notice(
                subject=(
                    'Exception generating task notification for OGo#{0}'.
                    format(task.object_id, )
                ),
                message=traceback.format_exc(),
                urgency=5,
                category='data',
            )
            self.context.rollback()

        else:

            self.log.info(
                'Sent notification message for OGo#{0} to "{1}" '
                'including {2} events'.
                format(task.object_id, ', '.join(to_address), len(events), )
            )
            update_notification_marker(self.context, task, events)
            self.context.commit()

        finally:
            task = None
            self.enqueue_event(
                TASK_NOTIFICATION_PROCESSED,
                (object_id, ),
            )
