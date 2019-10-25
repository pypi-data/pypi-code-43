#
# Copyright (c) 2014, 2015, 2018
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
import pytz
from os import getenv
from datetime import datetime, timedelta
from coils.core import \
    SQLConnectionFactory, \
    send_email_using_project7000_template, \
    get_object_from_project7000_path

GLOBAL_NOTIFICATION_ADDRESS = None


import logging
log = logging.getLogger('taskNotification')


class EndTemplateException(Exception):

    def __init__(self, message):
        self.message = message
        super(EndTemplateException, self).__init__(message)


def end_template(message='no message'):
    raise EndTemplateException(message)


class CVMockFlyweight(object):

    def __init__(self, value):

        self._string_value = value

    @property
    def string_value(self):
        return self._string_value

    @property
    def parent_id(self):
        return 0


def get_task_notification_template(context, kind):

    # We have to deal with None and blank kind values, ugly.
    if kind is None:
        kind = 'generic'
    elif isinstance(kind, basestring):
        kind = kind.strip()
        if len(kind) == 0:
            kind = 'generic'

    template_path = '/Entity Templates/Task/notify.{0}.mako'.format(
        kind,
    )
    template = get_object_from_project7000_path(
        context, template_path,
    )
    if not template and not kind == 'generic':
        # Fall back to the generic template, no specific template found
        template_path = '/Entity Templates/Task/notify.generic.mako'
        template = get_object_from_project7000_path(
            context, template_path,
        )

    return template


def get_notification_list(context, task, exclude_ids=None, ):
    """
    Return list of e-mail addresses to be notified.
    """

    global GLOBAL_NOTIFICATION_ADDRESS

    """
    Initialize value of GLOBAL_NOTIFICATION_ADDRESS from the environment
    variable COILS_ALL_TASKS_NOTIFICATION_ADDRESS.  Once this is set in
    the current process we'll just continue to use that value - environment
    variables are not expected to change beneath us.
    """

    if GLOBAL_NOTIFICATION_ADDRESS is None:
        override_address = getenv('COILS_ALL_TASKS_NOTIFICATION_ADDRESS')
        if override_address:
            GLOBAL_NOTIFICATION_ADDRESS = override_address.split(',')
        else:
            GLOBAL_NOTIFICATION_ADDRESS = False

    notifications = context.run_command(
        'task::get-notification-list', task=task,
    )
    if not notifications:
        return None, None
    if exclude_ids:
        notifications = [
            x for x in notifications if x.parent_id not in exclude_ids
        ]

    """
    take the strings out of the company values making a trivial lame
    attempt to remove hopelessly bogus values
    """
    notifications = [
        address for address in [
            cv.string_value for cv in notifications
        ] if address is not None and len(address.strip()) > 3
    ]

    if GLOBAL_NOTIFICATION_ADDRESS:
        to_address = GLOBAL_NOTIFICATION_ADDRESS
    else:
        to_address = notifications

    return notifications, to_address


def get_qualifying_task_events(
    task, floor_object_id=1, floor_seconds=360, logger=None,
):

    floor_datetime = (
        datetime.now(tz=pytz.UTC) - timedelta(seconds=floor_seconds)
    )

    events = [
        (ev.object_id, 'audit', ev.actor_id,
         ev.datetime, ev.action, ev.message, )
        for ev in task.logs
        if (
            ev.object_id > floor_object_id and
            ev.datetime > floor_datetime and
            ev.actor_id != 10000
        )
    ]

    events.extend([
        (ev.object_id, 'action', ev.actor_id,
         ev.action_date, ev.action, ev.comment, )
        for ev in task.notes
        if (
            ev.object_id > floor_object_id and
            ev.action_date > floor_datetime and
            ev.actor_id != 10000
        )
    ])

    if logger:
        logger.debug(
            'Found {0} events for notification regarding OGo#{1}'
            .format(len(events), task.object_id, )
        )

    events = sorted(events, key=lambda event: event[3])

    return events


def get_name_dictionary_matching_events(context, events):

    names = dict()
    for actor_id in set([x[2] for x in events]):
        entity = context.type_manager.get_entity(actor_id)
        if entity:
            names[actor_id] = entity.get_display_name()
        else:
            names[actor_id] = 'OGo#{0}'.format(actor_id, )

    return names


def send_task_notification_message(
    context,
    events,
    to_address,
    template,
    task,
    notification_addresses,
):
    """
    events is of the form:
        (object_id, 'audit', actor_id, datetime, action, message, )
        (object_id, 'action', actor_id, action_date, action, comment, )
    """

    from_address = ''
    try:
        from_address = context.server_defaults_manager.string_for_default('TaskNotificationFromAddress')  # noqa
        if from_address is None:
            from_address = ''
    except:
        pass

    names = get_name_dictionary_matching_events(context, events)

    owner = context.type_manager.get_entity(task.owner_id)

    executor = context.type_manager.get_entity(task.executor_id)

    """
    actions: 00_created, 02_rejected, 05_accepted, 10_commented,
      25_done, 27_reactivated, 30_archived
    """

    action_list = list()
    if '00_created' in [x[4] for x in events]:  # Created
        action_list.append('N')
    if '02_rejected' in [x[4] for x in events]:  # Rejected
        action_list.append('X')
    if '05_accepted' in [x[4] for x in events]:  # Accepted
        action_list.append('A')
    if '10_commented' in [x[4] for x in events]:  # Commented
        action_list.append('C')
    if '25_done' in [x[4] for x in events]:  # Done
        action_list.append('D')
    if '27_reactivated' in [x[4] for x in events]:  # Reactivated
        action_list.append('R')
    if '30_archived' in [x[4] for x in events]:  # Archived
        action_list.append('H')
    if action_list:
        action_list = ''.join(action_list)
    else:
        action_list = None

    if action_list:
        subject = 'OGo#{0}[{1}]: {2}'.format(
            task.object_id, action_list, task.name,
        )
    else:
        subject = 'OGo#{0}: {1}'.format(task.object_id, task.name, )

    log.info('sending task notification message')
    event_counter = 0
    send_email_using_project7000_template(
        context=context,
        subject=subject,
        to_address=to_address,
        from_address=from_address,
        template_document=template,
        regarding_id=task.object_id,
        other_headers={
            'X-OpenGroupware-Task-Kind': task.kind if task.kind else 'generic',
            'X-OpenGroupware-Task-Actions': ','.join(
                [str(x[4]) for x in events]
            ),
            'X-OpenGroupware-Task-Actors': ','.join(
                [str(x[2]) for x in events]
            ),
        },
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
        send_blind=True,
    )

    return True


def do_task_notification_preamble(
    context, logger, object_id,
    floor_object_id=None,
    floor_seconds=360,

):

    """Get the task"""

    task = context.run_command('task::get', id=object_id, )
    if task is None:
        logger.error(
            'Unable to marshall OGo#{0} for notification from context OGo#{1}'.
            format(object_id, context.account_id, )
        )
        # task, events, template, notification_addresses, to_address
        return (None, None, None, None, None, )
    else:
        logger.debug('Marshalled task OGo#{0}'.format(task.object_id, ))

    if not floor_object_id:
        """Determine the floor for event selection"""
        floor_object_id = 0
        prop = context.property_manager.get_property(
            entity=task,
            namespace='817cf521c06b47228392a0437daf81e0',
            attribute='lastNotificationMaximum'
        )
        if prop:
            floor_object_id = long(prop.get_value())

    logger.debug(
        'Event floor objectId for OGo#{0} is OGo#{1}'
        .format(floor_object_id, task.object_id, )
    )

    """Get qualifying events"""

    events = get_qualifying_task_events(
        task,
        floor_object_id=floor_object_id,
        floor_seconds=floor_seconds,
        logger=logger,
    )

    if not events:
        events = list()
        # task, events, template, notification_addresses, to_address
        # return (None, None, None, None, None, )

    """
    We exclude system accounts, those with an id less than and including
    10,000 from receiving notifications.
    """
    actor_ids = set(
        [event[2] for event in events if event[2] > 10000]
    )

    logger.debug(
        'Actors: {0}'.format(
            ','.join([str(objid) for objid in actor_ids]),
        )
    )

    """
    If all actions were performed by one actor we exclude that actor
    from notifications - as that person did them and does not need to
    be notified of what they themselves did.  If there is more than one
    actor we have to notify everyone so we leave exclude ids empty. The
    value of exclude_ids is plural [an enumerable] just for potential
    future exclusions.
    """
    exclude_ids = None
    if len(actor_ids) == 1:
        exclude_ids = (actor_ids.pop(), )

    """Template Path, based on kind"""

    template = get_task_notification_template(
        context, task.kind,
    )
    if not template:
        # task, events, template, notification_addresses, to_address
        return (None, None, None, None, None, )

    """To: notification address list """

    notification_addresses, to_address, = get_notification_list(
        context, task, exclude_ids=exclude_ids,
    )
    if not to_address:
        logger.debug(
            'No targets to notify for notification regarding OGo#{0}'
            .format(task.object_id, )
        )

        context.rollback()
        return task, events, template, list(), None
    else:
        logger.debug(
            '{0} notification targets'.format(len(to_address), )
        )

    return task, events, template, notification_addresses, to_address
