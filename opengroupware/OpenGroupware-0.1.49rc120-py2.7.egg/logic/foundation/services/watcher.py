#
# Copyright (c) 2013, 2015, 2017
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
#
import time
import select
import traceback
import psycopg2
import psycopg2.extensions
from sqlalchemy import and_, or_, func
from sqlalchemy.orm.exc import NoResultFound
from threading import Thread
from threading import local as thread_local
from coils.core import \
    ObjectInfo, \
    Packet, \
    ProcessLogEntry, \
    Address, \
    Telephone, \
    ObjectProperty, \
    ProjectInfo, \
    DateInfo, \
    CompanyInfo, \
    Participant, \
    ProjectAssignment, \
    CompanyAssignment, \
    ObjectLink, \
    CollectionAssignment, \
    AuditEntry, \
    AdministrativeContext, \
    ServerDefaultsManager, \
    ThreadedService, \
    Task


EVENTQUEUE = 'auditEvent'

MAX_CYCLES_ON_CONNECTION = 384
WATCHER_SELECT_TIMEOUT = 20  # 20 seconds results in a select timeout
# a connection could site completely idle for
#    MAX_CYCLES_ON_CONNECTION * WATCHER_SELECT_TIMEOUT = ~2 hours
# after which an WATCHER_NOTIFY event will be sent at reconnection
# regardless of if any activity has been detected.
WATCHER_NAMESPACE = '817cf521c06b47228392a0437daf81e0'
WATCHER_TIMEOUT = 1000
WATCHER_NOTIFY = 1001
WATCHER_SHUTDOWN = 1002
WATCHED_TYPES = [
    'document', 'contact',     'enterprise', 'task',
    'project',  'appointment', 'folder',     'note',
    'route',    'process',
]

NOTIFY_EXCHANGE = 'OpenGroupware_Coils_Notify'

"""
A snapshot of the actions seen in a long-lived production database:
    27_reactivated         59
    02_rejected           229
    05_accepted         1,052
    25_done             1,694
    notification        7,179
    30_archived        32,855
    10_archived        33,991
    download          138,508
    05_changed        595,314
    99_delete       1,377,192
    00_created      1,671,573
    10_commented    5,326,968
"""


def _connect_to_engine(service, ctx):
    ctx.close()
    connection = None
    try:
        connection = \
            ctx.db_session().connection().connection.checkout().connection
    except Exception as exc:
        connection = None
        ctx.log.exception(exc)
        service.send_administrative_notice(
            subject='An exception occured in the database event watcher thread',  # noqa
            message=traceback.format_exc(),
            urgency=8,
            category='service',
        )
    else:
        connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
    return connection


def _wait_for_engine_connection(service, ctx):
    """
    make 30 attempts to connect the the engine at backing off intervals of
    1 seconds, so total wait time is ~465 seconds (7.75 minutes) before the
    component should fail
    """
    counter = 0
    connection = None
    while connection is None:
        counter += 1
        connection = _connect_to_engine(service, ctx)
        if connection is None:
            ctx.log.warning(
                'Engine connection attempt {0} failed'.format(counter, )
            )
            time.sleep(counter + 0.1)  # time.sleep param must be a float
        if connection > 30:
            break
    return connection


def watch_for_pgevents(service):

    def execute_listen(connection):
        cursor = connection.cursor()
        cursor.execute('LISTEN {0};'.format(EVENTQUEUE, ))
        return cursor

    event_queue = service.event_queue

    cursor = None
    connection = None
    cycles_on_connection = 0

    t = thread_local()
    t.ctx = AdministrativeContext({}, component_name='coils.watcher:notify')
    connection = _wait_for_engine_connection(service, t.ctx)
    if connection:
        cursor = execute_listen(connection)
        restart_enabled = True
    else:
        restart_enabled = False

    cycles_on_connection = 0
    while service.RUNNING and restart_enabled:
        poll = None

        if cycles_on_connection > MAX_CYCLES_ON_CONNECTION:
            try:
                cursor.close()
            except:
                pass
            finally:
                cursor = None
            t.ctx.log.debug('releasing ORM connection due to maximum number of cycles')  # noqa
            cycles_on_connection = 0
            connection = _wait_for_engine_connection(service, t.ctx)
            if not connection:
                # could not rebuild database connection, component should fail
                restart_enabled = False
                continue
            event_queue.put((WATCHER_NOTIFY, None, ))  # send a notify event
            cursor = execute_listen(connection)  # resume the polling

        try:
            poll = select.select(
                [connection, ], [], [], WATCHER_SELECT_TIMEOUT,
            )
        except Exception as exc:
            t.ctx.log.exception(exc)
            service.send_administrative_notice(
                subject='An exception occured during select() on database connection',  # noqa
                message=traceback.format_exc(),
                urgency=8,
                category='service',
            )
            poll = None
        else:
            cycles_on_connection += 1

        if poll is None:
            # attempt to rebuild database connection
            try:
                cursor.close()
            except:
                pass
            finally:
                cursor = None
            cycles_on_connection = 0
            connection = _wait_for_engine_connection(service, t.ctx)
            if not connection:
                # could not rebuild database connection, component should fail
                restart_enabled = False
                continue

        if poll == ([], [], [], ):
            # no events on connection
            event_queue.put((WATCHER_TIMEOUT, None, ))
            continue

        try:
            connection.poll()
        except Exception as exc:
            t.ctx.log.exception(exc)
        else:
            gong_counter = 0
            while connection.notifies:
                # Yields a notify object we do not need
                connection.notifies.pop()
                gong_counter += 1  # we want to send a SINGLE notify event
            t.ctx.log.debug(
                'gong counter value after poll() is {0}'.format(gong_counter, )
            )
            for tmp in range(-1, gong_counter / 1000):
                # send a watcher notify event for every 1,000 gongs
                event_queue.put((WATCHER_NOTIFY, None, ))
                t.ctx.log.debug('WATCHER_NOTIFY event sent to bus')
            gong_counter = None

    t.ctx.close()


class WatcherService (ThreadedService):
    __service__ = 'coils.watcher'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)
        self.create_auditor_thread()
        self.max_audit_entry = 0

    def create_auditor_thread(self, start=False):
        if 'audit' not in self.threads:
            self.threads['audit'] = Thread(
                target=watch_for_pgevents,
                name='pgListen',
                args=(self, ),
            )
            audit_thread = self.threads['audit']
            if start:
                audit_thread.start()
                audit_thread.join(0.1)
        return self.threads['audit']

    def shutdown_auditor_thread(self):
        auditor = self.threads.get('audit', None)
        if auditor:
            while auditor.is_alive():
                auditor.join(1.0)
                if auditor.is_alive():
                    self.send_administrative_notice(
                        subject='Terminated auditor thread not complete',
                        message='Terminated auditor thread not complete.\n'
                                'Component "coils.watcher" is potentially '
                                'hung.\n',
                        urgency=6,
                        category='service',
                    )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext(
            {},
            broker=self._broker,
            component_name=self.__service__,
        )
        self._sd = ServerDefaultsManager()

        prop = self._ctx.property_manager.get_server_property(
            WATCHER_NAMESPACE,
            'maxAuditEntry',
        )
        if prop:
            self.max_audit_entry = long(prop.get_value())
        else:
            self.max_audit_entry = self._ctx.db_session().\
                query(func.max(AuditEntry.object_id)).\
                one()[0]
            self.persist_max_audit_entry()
            self._ctx.commit()
            prop = None
        self._ctx.db_close()

    def process_service_specific_event(self, event_class, event_data):
        if event_class == WATCHER_TIMEOUT:
            pass
        elif event_class == WATCHER_NOTIFY:
            while self.perform_collect_changes():
                self.log.debug(
                    'Collection changes starting from OGo#{0}'
                    .format(self.max_audit_entry, )
                )
        elif event_class == WATCHER_SHUTDOWN:
            self.shutdown_auditor_thread()
            self.create_auditor_thread(start=True)
            self.send_administrative_notice(
                subject='"coils.watcher" notification thread resumed.',
                message='"coils.watcher" notification thread resumed.\n'
                        'Component resumed notification at OGo#{0}\n'.
                        format(self.max_audit_entry, ),
                urgency=1,
                category='service', )
        self._ctx.db_close()

    #
    # Perform Handlers
    #

    def perform_collect_changes(self):
        '''
        Collect changs from the audit log.

        00_created,
        02_rejected,
        27_reactivated,
        download
        25_done,
        10_archived
        99_delete
        10_commented
        05_changed
        30_archived

        Note that 10_archived is an obsolete action and should not be seen
        in modern databases, the same is true for "delete" and "99_deleted".
        Delete events are all mapped to "99_delete". A "10_archived" event
        is mapped to the current "30_archived".
        '''
        object_id = None
        try:
            query = self._ctx.db_session().\
                query(AuditEntry).\
                filter(
                    and_(
                        AuditEntry.object_id > self.max_audit_entry,
                        AuditEntry.action.in_(
                            [
                                '00_created', '05_changed', '10_commented',
                                '02_rejected', '27_reactivated', '25_done',
                                '99_delete', 'delete', '99_deleted',
                                '05_accepted', '30_archived', '10_archived',
                            ]
                        ),
                        AuditEntry.context_id > 10000,
                    )
                ).order_by(AuditEntry.object_id).limit(4096)

            deletions = {}

            reconfigure_event = False

            results = query.all()
            if not results:
                self.log.debug('No audit entries collected from database')
                self.log.debug(
                    'max_audit_entry = {0}'.format(self.max_audit_entry, )
                )
                return False

            self.log.debug(
                'Collected {0} audit entries from database'
                .format(len(results), )
            )

            for event in results:

                object_id = event.object_id

                """Fix legacy action strings"""
                if event.action in ('99_deleted', 'delete', ):
                    action_string = '99_delete'
                elif event.action == '10_archived':
                    action_string = '30_archived'
                else:
                    action_string = event.action

                # Handle Deletes
                if action_string == '99_delete':
                    '''
                    The purpose of this is to supress duplicate deleted
                    notifications with can happen when both a database trigger
                    and a Logic command post a deletion event to the entity
                    audit log.  Processing multiple deletion events is
                    pointless.
                    '''
                    if event.context_id not in deletions:
                        deletions[event.context_id] = event

                else:
                    # Handle all non-delete events
                    entity = (
                        self._ctx.type_manager.get_entity(
                            event.context_id,
                            repair_enabled=False,
                        )
                    )
                    if not entity:
                        continue

                    kind = entity.__entityName__.lower()

                    timestamp = time.mktime(event.datetime.utctimetuple())

                    project_id = 0
                    if hasattr(entity, 'project_id'):
                        project_id = entity.project_id
                    if project_id == 7000:
                        reconfigure_event = True

                    """
                    Task last modified HACK, do what we can to keep the last
                    modified property of the Task up-to-date.
                    """
                    if (
                        kind in ('task', 'job', ) and
                        event.action not in ('99_delete')
                    ):
                        self.task_last_modified_hack(
                            object_id=object_id,
                            timestamp=timestamp,
                        )

                    if kind in WATCHED_TYPES:
                        self.log.debug(
                            'Sending event notification for OGo#{0} '
                            '[{1}] "{2}"'.
                            format(event.context_id,
                                   kind,
                                   event.action, ))
                        self.send(
                            Packet(
                                None,
                                'coils.notify/__audit_{0}'.format(kind, ),
                                {
                                    'auditId':   event.object_id,
                                    'kind':      kind,
                                    'timestamp': timestamp,
                                    'projectId': project_id,
                                    'objectId':  event.context_id,
                                    'actorId':   event.actor_id,
                                    'action':    action_string,  # translated
                                    'version':   event.version,
                                    'message':   event.message,
                                },
                            ),
                            fanout=True,
                            exchange=NOTIFY_EXCHANGE,
                        )
                    else:
                        self.log.debug(
                            'Discarding event notification for OGo#{0} [{1}]'
                            .format(event.object_id, kind, )
                        )

                self.max_audit_entry = event.object_id

            if deletions:

                for object_id, event in deletions.items():

                    timestamp = time.mktime(event.datetime.utctimetuple())

                    self.send(
                        Packet(
                            None,
                            'coils.notify/__audit_delete',
                            {
                                'auditId':   event.object_id,
                                'kind':      'unknown',
                                'projectId': 0,
                                'timestamp': timestamp,
                                'objectId':  event.context_id,
                                'actorId':   event.actor_id,
                                'action':    '99_delete',
                                'version':   None,
                                'message':   event.message,
                            },
                        ),
                        fanout=True,
                        exchange=NOTIFY_EXCHANGE, )

                    self.clean_up(object_id)

            if reconfigure_event:
                self.send(
                    Packet(
                        None,
                        'coils.notify/__reconfigure',
                        {},
                    ),
                    fanout=True,
                    exchange=NOTIFY_EXCHANGE, )

            self.persist_max_audit_entry()

        except Exception as e:
            self.log.exception(e)
            self.send_administrative_notice(
                subject='Exception processing database notification',
                message=(
                    'An exception occured in processing database '
                    'notification OGo#{0}.\n\n{1}\n'
                    .format(
                        object_id,
                        traceback.format_exc(),
                    )
                ),
                urgency=9,
                category='data', )
            self._ctx.rollback()
            return False
        else:
            self._ctx.commit()
            self.log.info(
                'maxAuditEntry recorded as {0}'.format(self.max_audit_entry, )
            )
            return True

    def persist_max_audit_entry(self):
        self._ctx.property_manager.set_server_property(
            WATCHER_NAMESPACE,
            'maxAuditEntry',
            self.max_audit_entry, )

    #
    # Task last modified fix hack
    #
    def task_last_modified_hack(self, object_id, timestamp):
        try:
            task = self._ctx.db_session().query(
                Task
            ).filter(
                Task.object_id == object_id
            ).enable_eagerloads(False).one()
        except NoResultFound:
            # no such record exists
            pass
        else:
            if task._modified < timestamp - 30:
                self.log.debug(
                    'Last modified time for OGo#{0} [Task] updated '
                    'from {1} to {2}'.format(
                        task._modified,
                        timestamp,
                    )
                )
                task._modified = timestamp
        task = None

    #
    # Cleaner
    #

    def clean_up(self, object_id):

        self.log.debug(
            'Performing maintenance clean-up for deletion of OGo#{0}'.
            format(object_id, ))

        # Object Links
        counter = 0
        query = self._ctx.db_session().query(
            ObjectLink
            ).filter(
                or_(
                    ObjectLink.target_id == object_id,
                    ObjectLink.source_id == object_id,
                )
            )
        for link in query.all():
            counter += 1
            self._ctx.db_session().delete(link)
        self.log.debug(
            '{0} derelict object links purged for OGo#{1}.'.
            format(
                counter,
                object_id,
            )
        )

        # Collection Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(
                CollectionAssignment
            ).filter(
                CollectionAssignment.assigned_id == object_id
            )
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict collection assignments purged for OGo#{1}.'.
            format(
                counter,
                object_id,
            )
        )

        # Company Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(
                CompanyAssignment
            ).filter(
                or_(
                    CompanyAssignment.parent_id == object_id,
                    CompanyAssignment.child_id == object_id,
                )
            )
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict company assignments purged for OGo#{1}.'.
            format(
                counter,
                object_id,
            )
        )

        # Project Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(ProjectAssignment).\
            filter(
                or_(
                    ProjectAssignment.parent_id == object_id,
                    ProjectAssignment.child_id == object_id,
                )
            )
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict project assignments purged for OGo#{1}'.
            format(counter, object_id, )
        )

        # Date Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(Participant).\
            filter(
                or_(
                    Participant.participant_id == object_id,
                    Participant.appointment_id == object_id,
                )
            )
        for participant in query.all():
            self._ctx.db_session().delete(participant)
            counter += 1
        self.log.debug(
            '{0} derelict event participants purged for OGo#{1}'.
            format(
                counter,
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned company info entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    CompanyInfo
                ).filter(
                    CompanyInfo.parent_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned date info entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    DateInfo
                ).filter(
                    DateInfo.parent_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned project info entries for OGo#{1}.'.
            format(
                self._ctx.db_session().query(
                    ProjectInfo
                ).filter(
                    ProjectInfo.project_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned object property entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    ObjectProperty
                ).filter(
                    ObjectProperty.parent_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned telephone entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    Telephone
                ).filter(
                    Telephone.parent_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} orphaned address entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    Address
                ).filter(
                    Address.parent_id == object_id
                ).delete(),
                object_id,
            )
        )

        """
        2015-03 : The watcher no longer purges locks, locks will simply be
        left to expire.  Otherwise we have a condition where lots of
        simultanous deletes are attempted on the Locks table.  Locks on a
        non-existant entity are harmless, and they will expire naturally.

        self.log.debug(
            'Purged {0} irrelevant locks on OGo#{1}'.
            format(
                self._ctx.db_session().query(Lock).
                filter(Lock.object_id == object_id).
                delete(),
                object_id, ))
        """

        self.log.debug(
            'Purged {0} orphaned process log entries on OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    ProcessLogEntry
                ).filter(
                    ProcessLogEntry.process_id == object_id
                ).delete(),
                object_id,
            )
        )

        self.log.debug(
            'Purged {0} derelict object info entries on OGo#{1}'.
            format(
                self._ctx.db_session().query(
                    ObjectInfo
                ).filter(
                    ObjectInfo.object_id == object_id
                ).delete(),
                object_id,
            )
        )

        return

    #
    # Message Handlers
    #

    def do_set_maxauditentry(self, parameter, packet):
        object_id = long(packet.data.get('maxAuditEntry', 0))
        if object_id:
            self.log.info(
                'Request to reset "maxAuditEntryValue" to {0}'
                .format(object_id, )
            )
            self.max_audit_entry = object_id
            self.persist_max_audit_entry()

    def do_get_maxauditentry(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {
                    'status': 200,
                    'text': 'coils.watcher maxAuditEntry',
                    'value': self.max_audit_entry,
                }
            )
        )
