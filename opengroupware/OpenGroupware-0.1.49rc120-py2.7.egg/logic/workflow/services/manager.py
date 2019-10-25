#
# Copyright (c) 2010, 2012, 2013, 2014, 2015, 2016, 2018
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
import json
import traceback
from time import time  # NOTE: only used from scheduling
from sqlalchemy import and_, not_
from coils.core import \
    Process, \
    Route, \
    AdministrativeContext, \
    Packet, \
    CoilsException, \
    ThreadedService, \
    RouteGroup, \
    Lock


"""
The manager maintains an internal dictionary where the key is the PID and the
values indicate what the manager believes about the process.  It uses this
table to manage process and polls other components to verify its vision of the
world.

  {
     PID: {
        processId: process.object_id,
        contextId: process.owner_id,
        status: R | F | Q | C | P | ?
        executor: '', ununsed, in anticipation of multiple executors
        routeGroup: String
        registered: 0.0
        routeId': #
        routeName': String
        lockToken': None | String
        missCount': #
        singleton': True / False
    }
  }

A process must get registered with this dictionary in order to be tracked
correctly by the manager - this registration is accomplished by calling the
manager_register_process method.

Any commit/rollback must be handled by the job/do methods.  The manager
methods are USED by the job/do methods and MUST return a reasonable value so
the job/do can determine if it wants to commit or rollback any database
activity.

We do not db_close in the manager component except in the case of do_disabled,
which should place the manager into an idle state.
"""


ADMIN_RECORD_STATUS = 200
ADMIN_TICK_TOCK = 201
ADMIN_PING_PARKED = 202

ADMIN_TICK_TOCK_INTERVAL = 60  # every minute
ADMIN_PING_PARKED_INTERVAL = 300  # every five minutes


COMMAND_MAP = {
    ADMIN_RECORD_STATUS: 'manager_record_state',
    ADMIN_TICK_TOCK: 'job_tick_tock',
    ADMIN_PING_PARKED: 'job_ping_parked',
}


class ManagerService(ThreadedService):
    __service__ = 'coils.workflow.manager'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def prepare(self):
        ThreadedService.prepare(self)
        self._enabled = True
        self._ctx = AdministrativeContext(
            {},
            broker=self._broker,
            component_name=self.__service__,
        )
        self._ps = {}

        """
        Setup periodic job for checking job queues and status
        """
        self.schedule_at_interval(
            'recordEngineStatus',
            message=ADMIN_TICK_TOCK,
            seconds=ADMIN_TICK_TOCK_INTERVAL,
        )

        """
        Setup periodic job for pinging parked processes

        self.schedule_at_interval(
            'pingParkedProcesses',
            message=ADMIN_PING_PARKED,
            seconds=ADMIN_PING_PARKED_INTERVAL,
        )
        """

    def process_service_specific_event(self, event_class, event_data):
        if event_class in COMMAND_MAP:
            method_name = COMMAND_MAP.get(event_class)
            if method_name:
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(event_data)
                else:
                    self.log.error(
                        'Method "{0}" mapped from event "{1}" does not exist.'
                        .format(method_name, event_class, ))
            else:
                self.log.info(
                    'Event "{0}" mapped as no-operation'
                    .format(event_class, ))
        else:
            self.log.warn(
                'Event "{0}" is not in command processing map'
                .format(event_class, )
            )

    def send_to_process_log(self, process_id, message, ):
        self.send(
            Packet(
                None,
                'coils.workflow.logger/log',
                {
                    'process_id': process_id,
                    'message': message,
                },
            )
        )

    @property
    def ps(self):
        return self._ps

    def manager_record_state(self):
        """
        Record manager's view of the engine state as the server property
        {http://www.opengroupware.us/oie}engineStatus
        """

        """Retrieve a list of locked routegroups"""
        locked_route_groups = (
            self._ctx.db_session()
            .query(RouteGroup.object_id, RouteGroup.name)
            .join(Lock, Lock.object_id == RouteGroup.object_id)
            .filter(
                and_(
                    Lock.exclusive == 'Y',
                    Lock.expires > self._ctx.get_timestamp()
                )
            ).all()
        )

        """Record status to the server property"""
        self._ctx.property_manager.set_server_property(
            namespace='http://www.opengroupware.us/oie',
            name='engineStatus',
            value=json.dumps(
                {
                    'version': 1,
                    'operatingMode': (
                        'online' if self._enabled else 'maintenance'
                    ),
                    'processTableSize': len(self._ps),
                    'runningProccesses': len(
                        [p for p in self._ps.values() if p['status'] == 'R']
                    ),
                    'queuedProcesses': len(
                        [p for p in self._ps.values() if p['status'] == 'Q']
                    ),
                    'lockedRouteGroups': locked_route_groups
                }
            )
        )

    def manager_register_process(
        self, _process, status='?', executor_id='', run_token=None
    ):
        '''
        Make the manager aware of the specified process and record it in
        the requested state.

        :param _process: Either a Process entity or a process id
        :param status: The status to record for the process
        :param executor_id: The executor of the process, currently blank.
        This is a place holder for the implementation of multiple executors.
        :param run_token: The run token / run lock of the process.
        '''

        if isinstance(_process, Process):
            pid = long(_process.object_id)
            process = _process
        elif isinstance(_process, int) or isinstance(_process, long):
            pid = long(_process)
            process = None
        else:
            raise CoilsException(
                'Can only register a process by entity or pid, got a "{0}"'
                .format(type(_process), )
            )
        _process = None

        if pid not in self.ps:
            # this process is not already registered, so learn about it

            if not process:
                process = self._ctx.run_command('process::get', id=pid, )
                if not process:
                    self.log.info(
                        'Cannot marshall OGo#{0}, discarding registration '
                        'request.'.format(pid, )
                    )
                    return False

            if process.state in ('X', 'F', 'C', ):
                self.log.info(
                    'OGo#{0} [Process] in state "{1}", refusing registration'
                    .format(process.object_id, process.state, )
                )
                return False

            singleton = False
            routegroup = str(process.object_id)
            if process.route:
                if process.route.route_group:
                    routegroup = process.route.route_group.name.upper()
                else:
                    routegroup = process.route.name.upper()
                if process.route.is_singleton:
                    singleton = True
            else:
                self.log.error(
                    'No route found for OGo#{0} [Process]; '
                    'refusing registration.'.format(process.object_id, )
                )
                # TODO: Send adminsitrative notice
                return False

            """
            NOTE: the executorId value is to identify the executor that own
            the process, or owned the process last.  This is for *future*
            support of multiple executors.
            """
            self.ps[pid] = {
                'processId': process.object_id,
                'contextId': process.owner_id,
                'status': '?',
                'executor': executor_id,
                'routeGroup': routegroup,
                'registered': time(),
                'routeId': 0,
                'routeName': 'n/a',
                'lockToken': None,
                'lastPing': 0.0,
                'lastPong': 0.0,
                'missCount': 0,
                'singleton': singleton,
            }

            if process.route:
                self.ps[process.object_id]['routeId'] = process.route.object_id
                self.ps[process.object_id]['routeName'] = process.route.name
            """
            Set the contextName, used in process listings such as
            available in snurtle
            """
            if process.owner_id == 8999:
                self.ps[pid]['contextName'] = 'Coils\Network'
            elif process.owner_id == 0:
                self.ps[pid]['contextName'] = 'Coils\Anonymous'
            elif process.owner_id == 10000:
                self.ps[pid]['contextName'] = 'Coils\Administrator'
            elif process.owner_id > 10000:
                owner = self._ctx.run_command(
                    'contact::get', id=process.owner_id,
                )
                if owner:
                    self.ps[pid]['contextName'] = owner.login
                    owner = None
                else:
                    self.ps[pid]['contextName'] = (
                        'OGo{0}'.format(process.owner_id, )
                    )
            else:
                self.ps[pid]['contextName'] = '_undefined_'

            self.log.debug(
                'New OGo#{0} [Process] registered; routeGroup="{1}" '
                'singleton="{2}"'.format(pid, routegroup, singleton, )
            )

            self.send_to_process_log(
                process.object_id, 'Process registered by workflow manager.'
            )

        self.ps[pid]['status'] = status
        self.ps[pid]['updated'] = time()

        if run_token:
            self.ps[pid]['lockToken'] = run_token.strip()
        self.log.debug(
            'OGo#{0} [Process] registered in state "{1}"'.format(pid, status, )
        )

        if status == 'R' and pid:
            self.manager_refresh_run_lock(pid)

        return True

    def manager_get_run_locktoken(self, pid):

        lock_token = None
        if pid in self.ps:
            lock_token = self.ps[pid]['lockToken']
            if lock_token:
                self.log.debug(
                    'OGo#{0} [Process] lock-token known in registered '
                    'process list'.format(pid, )
                )

        # Verify run-lock token between registration and database
        prop = self._ctx.property_manager.get_property(
            pid, 'http://www.opengroupware.us/oie', 'lockToken',
        )
        if prop and lock_token:
            """
            Manager has a lock token on file for the process AND there is a
            lock token recorded in the object property.
            """
            if lock_token != prop.get_string_value().strip():
                """
                Lock token on file does not match the lock token in the
                database.
                """
                self.log.error(
                    'Run lock token mismatch detected for OGo#{0}!  '
                    'Registered lock token is "{1}" but found lock '
                    'token of "{2}"'.format(pid, lock_token, prop.get_value, )
                )
                self.log.warn(
                    'Workflow manager has no choice but to wait '
                    'for run lock expiration.'
                )
                self.send_administrative_notice(
                    category='workflow',
                    urgency=6,
                    subject=(
                        'Run-lock token mismatch on OGo#{0}'
                        .format(pid, )
                    ),
                    message=(
                        'Run lock token mismatch detected for OGo#{0}.\n'
                        'Registered lock token is "{1}" but found lock '
                        'token of:\n  {2}\n'
                        .format(
                            pid, lock_token, prop.get_string_value(),
                        )
                    )
                )  # End send_administrative_notice
                self.ps[pid]['lockToken'] = None
                return False
            self.log.debug(
                'Registered run lock token matches lock token discovered.'
            )
            prop = None
        elif prop and (not lock_token):
            """
            Lock token not in manager's PS table, but found in database
            stored in object property.
            """
            lock_token = prop.get_string_value()
            self.log.info(
                'No run lock token was registered, discovered '
                'token "{0}" for OGo#{1}'
                .format(lock_token, pid, )
            )
            self.send_administrative_notice(
                category='workflow',
                urgency=2,
                subject=(
                    'Existing run-lock discovered for OGo#{0}'
                    .format(pid, )
                ),
                message=(
                    'No run lock token registered for OGo#{0}, '
                    'however a lock token has been discovered:\n'
                    '  {1}\n'
                    .format(
                        pid, lock_token,
                    )
                )
            )  # End send_administrative_notice
        elif lock_token and (not prop):
            self.log.info(
                'No run lock token discovered for OGo#{0}, '
                'but a token was registered.'.format(pid, )
            )
            self._ctx.property_manager.set_property(
                entity=pid,
                namespace='http://www.opengroupware.us/oie',
                attribute='lockToken',
                value=lock_token,
            )
        elif (not lock_token) and (not prop):
            self.log.info(
                'No run lock token was registered or discovered for OGo#{0}'
                .format(pid, )
            )

        return lock_token

    def manager_refresh_run_lock(self, pid):
        """
        TODO: if a process is in state running and has no lock a lock should
          be acquired and an administrative alert of this condition sent
        TODO: send an administrative alert if a runlock cannot be refreshed
        """

        lock_token = self.manager_get_run_locktoken(pid)
        if lock_token:
            if not (
                self._ctx.lock_manager.administratively_refresh_lock(
                    lock_token, duration=360000,
                )
            ):
                self.log.warn(
                    'Run lock for OGo#{0} not refreshed!'.format(pid, )
                )
            else:
                self.log.debug(
                    'Run lock for OGo#{0} [Process] refreshed.'.format(pid, )
                )
        else:
            self.log.error(
                'Could not find lock token for OGo#{0} [Process]; '
                'not refreshed!'.format(pid, )
            )

    def manager_ping_parked_processes(self):
        """
        Ping all the parked processes so they check if they can run now
        TODO: only ping processes that have been Parked for awhile
        """
        if not self._enabled:
            return
        processes = self._ctx.db_session().query(Process).filter(
            Process.state == 'P',
        )
        if not processes:
            self.log.debug('No processes found in parked state.')
        return
        for process in processes:
            ping_process = False
            prop = self._ctx.property_manager.get_property(
                entity=process,
                namespace='http://www.opengroupware.us/oie',
                attribute='waitingOnLabel',
            )
            if not prop:
                """no property, always try to start the process"""
                ping_process = True
            else:
                """
                a waitingOnLabel has been specified, only ping the
                process if a message with that label exists.
                """
                waiting_for_message_label = prop.get_string_value()
                message = self._ctx.run_command(
                    'message::get',
                    process=process,
                    label=waiting_for_message_label,
                )
                if message:
                    ping_process = True
            if ping_process:
                self._ctx.run_command(
                    'process::start', process=process, runas=process.owner_id,
                )
                self.log.debug(
                    'Requesting start of parked process OGo#{0}'
                    .format(process.object_id, )
                )
        return

    def manager_deregister_process(self, process):

        if isinstance(process, Process):
            pid = long(process.object_id)
        elif isinstance(process, int) or isinstance(process, long):
            pid = long(process)
        else:
            raise CoilsException(
                'Can only deregister a process by entity or '
                'objectId, got a "{0}"'.format(type(process, ))
            )

        lock_token = self.manager_get_run_locktoken(pid)

        # Release the run lock
        if lock_token:
            if (
                not self._ctx.lock_manager.administratively_release_lock(
                    lock_token
                )
            ):
                self.log.warn(
                    'Run lock for OGo#{0} not found to be removed!'
                    .format(pid, )
                )
                self.send_to_process_log(
                    pid,
                    'Run lock "{0}" not found to be removed'
                    .format(lock_token, )
                )
            else:
                self.log.debug(
                    'Removed run lock for OGo#{0} [Process]'.format(pid, )
                )
                self.send_to_process_log(
                    pid, 'Removed run lock "{0}"'.format(lock_token, )
                )
        else:
            self.log.error(
                'Requested to deregister a process for which there '
                'was no lock token'
            )
        self._ctx.property_manager.delete_property(
            pid, 'http://www.opengroupware.us/oie', 'lockToken',
        )

        if pid in self.ps:
            del self.ps[pid]
            self.log.info('Registration of OGo#{0} deleted'.format(pid, ))
            self.send_to_process_log(
                pid, 'Deleted process registration',
            )

        return False

    #
    # Internal methods
    #

    def manager_process_hierarchy_check(self, pid):
        if not self._enabled:
            return
        process = self._ctx.run_command('process::get', id=pid)
        if not process:
            return
        if process.parent_id:
            parent = self._ctx.run_command(
                'process::get', id=process.parent_id,
            )
            if not parent:
                self.log.info(
                    'Unable to marshall process OGo#{0} which is a parent '
                    'of OGo#{0}'.format(process.parent_id, process.object_id, )
                )
                return
            if parent.state in ('P', 'Q', ):
                self.log.debug(
                    'Requesting start of OGo#{0} due to completion of '
                    'child process OGo#{0}'
                    .format(
                        parent.object_id,
                        process.object_id,
                    )
                )
                self._ctx.run_command(
                    'process::start', process=parent, runas=parent.owner_id,
                )

    def manager_request_process_start(self, pid, cid):
        self.log.debug('Requesting process start for OGo#{0}'.format(pid, ))
        self.manager_register_process(pid, status='U', )
        self.send(
            Packet(
                'coils.workflow.manager/is_running',
                'coils.workflow.executor/start',
                {
                    'processId': pid,
                    'contextId': cid,
                },
            )
        )

    def manager_scan_running_processes(self):
        """
        Create a list of process ids which are believed to be running and
        ping the executor regarding thier status; the executor is expected to
        respond with a message to is_running indicating if it has a worker
        for that process alive.
        """

        self.log.info('Checking processes we believe in running state')
        db = self._ctx.db_session()
        """
        Retrieve any processes recorded as running in the database that the
        manager is now aware of; possibly left behind by a previous crash?
        """

        criteria = and_()
        criteria.append(Process.state == 'R')
        if self.ps:
            criteria.append(
                not_(
                    Process.object_id.in_(self.ps.keys())
                )
            )

        for running_pid in [
            x[0] for x in
            db.query(Process.object_id).filter(criteria).all()
        ]:
            if running_pid not in self.ps:
                """
                A process is in the database that is running but is not in
                the manager's process table.  This is a bug or the manager
                component was restarted - in this way it can relearn running
                processes.
                """
                self.manager_register_process(
                    running_pid, status='R',
                )

        """
        Create a list of PIDs we believe are processes which are running - and
        that we have not pinged for at least nine seconds.
        """
        running_pids = [
            x['processId'] for x in self.ps.values() if (
                (x['status'] in ('R', 'U', )) and
                (x['lastPing'] < (time() - 9.0))
            )
        ]

        """
        If we found any running processes request from their executor
        if they are running
        """
        if running_pids:
            self.log.info(
                'Found {0} processes in running state'
                .format(len(running_pids), )
            )
            for pid in running_pids:
                self.send(
                    Packet(
                        'coils.workflow.manager/is_running',
                        'coils.workflow.executor/is_running:{0}'.format(pid),
                        None)
                    )
                self.manager_record_ping(pid)
        else:
            self.log.info('Found no processes in running state')

    def manager_start_queued_processes(self):
        """
        Discover queued processed from database

        TODO: send adminsitrative alert on exception
        """

        if not self._enabled:
            self.log.info(
                'Workflow manager is in a disbaled state, will '
                'not start new processes.'
            )
            return False

        self.log.info('Checking for queued processes')

        db = self._ctx.db_session()
        try:

            query = (
                db.query(Process, Route).
                join(Route, Route.object_id == Process.route_id).
                filter(
                    and_(
                        Process.state.in_(['Q', ]),
                        Process.status != 'archived',
                    )
                ).
                order_by(Process.priority.desc(), Process.object_id).
                limit(150)
            )
            result = query.all()

            if result:

                for process, route in result:

                    context_id = self._ctx.account_id  # OGo Admin
                    if route.is_singleton:
                        """
                        For a singleton we apply the lock as if it is owned
                        by the process, so the context of the lock is the PID.
                        Otherwise the context of the lock is the Administrator
                        account, so there is no blocking that occurs as that
                        context will own all the locks and be able to
                        additively acquire more locks.
                        """
                        context_id = process.object_id

                    lock_target = route.route_group
                    if not lock_target:
                        lock_target = route

                    locked, my_lock = self._ctx.lock_manager.lock(
                        entity=lock_target,
                        duration=3600,
                        data=str(process.object_id),
                        run=True,
                        context_id=context_id,
                    )
                    if locked:
                        self._ctx.property_manager.set_property(
                            process,
                            'http://www.opengroupware.us/oie',
                            'lockToken',
                            my_lock.token,
                        )
                        self.log.info(
                            'Workflow manager acquired run lock "{0}"'
                            ' on OGo#{1} [{2}] as OGo#{3}'.
                            format(
                                my_lock.token.strip(),
                                lock_target.object_id,
                                lock_target.__entityName__,
                                context_id,
                                process.object_id,
                            )
                        )
                        self.send_to_process_log(
                            process.object_id,
                            'Acquired run lock "{0}" on OGo#{1} as OGo#{2};'
                            ' process will be started.'.format(
                                my_lock.token,
                                lock_target.object_id,
                                context_id,
                            )
                        )
                        self.manager_register_process(
                            process, status='Q', run_token=my_lock.token,
                        )
                        self.manager_request_process_start(
                            process.object_id, process.owner_id,
                        )
                        self._ctx.flush()  # Get the lock info into the DB
                    else:
                        self.log.info(
                            'Manager unable to acquire lock on OGo#{0} '
                            '[{1}/{2}] as OGo#{3} in order to start OGo#{4}'.
                            format(
                                lock_target.object_id,
                                lock_target.__entityName__,
                                lock_target.name,
                                context_id,
                                process.object_id,
                            )
                        )
                        """
                        self._ctx.audit_at_commit(
                            object_id=process.object_id,
                            action='10_commented',
                            message=(
                                'Unable to acquire run lock on OGo#{0} '
                                '[{1}/{2}] as OGo#{3}; process not started.'
                                .format(
                                    lock_target.object_id,
                                    lock_target.__entityName__,
                                    lock_target.name,
                                    context_id,
                                )
                            ),
                            version=process.version,
                        )
                        """

                self.manager_record_state()

        except Exception as exc:
            self.log.exception(exc)
            message = traceback.format_exc()
            self.send_administrative_notice(
                category='workflow',
                urgency=9,
                subject='Exception starting queued processes',
                message=message,
            )
            return False

        self.log.debug('Start Queueud Processes Commit')
        return True

    def manager_detect_zombie(self, process_id):

        process = self._ctx.run_command('process::get', id=process_id, )

        if not process:
            self.log.debug(
                'Can find no such process as OGo#{0}, assuming deleted.'
                .format(process_id, )
            )
            self.manager_deregister_process(process_id)
            return

        if process.state == 'C':
            self.send(
                Packet(
                    None,
                    'coils.workflow.manager/completed:{0}'.format(
                        process_id,
                    ),
                    None,
                )
            )
            self.log.debug(
                'Suspected Zombie process was in state complete, ignored.'
            )
            return
        elif process.state == 'F':
            self.send(
                Packet(
                    None,
                    'coils.workflow.manager/failed:{0}'.format(process_id, ),
                    None,
                )
            )
            self.log.debug(
                'Suspected Zombie process was in state failed, ignored.'
            )
            return
        elif not process.state == 'R':
            self.log.debug(
                'Not a Zombie, OGo#{0} [Process] in state "{1}", '
                'not in state "running"'.format(process_id, process.state, )
            )
            return

        self.log.warn(
            'Processing OGo#{0} [Process] as a zombie.'.format(process_id, )
        )

        """
        Generate a very descriptive message for the process we have determined
        has become one of the living dead.
        """

        route_id = process.route_id
        if process.route:
            route_name = process.route.name
        else:
            route_name = 'n/a'

        owner = self._ctx.run_command('contact::get', id=process.owner_id, )
        if owner:
            owners_name = owner.login
        else:
            owners_name = 'n/a'

        process_messages = self._ctx.run_command(
            'process::get-messages', process=process,
        )
        process_messages = [
            '    UUID#{0} \n      Version:{1} Size:{2} Label:{3}'.format(
                x.uuid, x.version, x.size, x.label
            ) for x in process_messages
        ]

        message = (
            'objectId#{0} [Process] determined to be in zombie state.\n'
            '  Route: {1} "{2}"\n'
            '  Owner: {3} "{4}"\n'
            '  Version: {5}\n'
            '  Messages:\n'
            '{6}'.format(
                process.object_id,
                route_id, route_name,
                process.owner_id, owners_name,
                process.version,
                '\n'.join(process_messages),
            )
        )

        self.send_administrative_notice(
            category='workflow',
            urgency=3,
            subject='OGo#{0} [Process] Flagged As Zombie'.format(process_id),
            message=message,
        )

        self.send_to_process_log(process_id, message, )

        process.state = 'Z'
        self.manager_deregister_process(process_id)
        self.manager_record_state()

    def job_tick_tock(self, data):

        if not self._enabled:
            self.log.debug('Engine disabled')
            return

        self.log.debug('Engine enabled: running maintenance processes')
        try:
            self.manager_scan_running_processes()
        except Exception as exc:
            self.log.error('Exception in manager_scan_running_processes')
            self.log.exception(exc)
            self._ctx.rollback()
            return
        try:
            self.manager_start_queued_processes()
        except Exception as exc:
            self.log.error('Exception in manager_start_queued_processes')
            self.log.exception(exc)
            self._ctx.rollback()
            return
        self._ctx.commit()

    def job_ping_parked(self, data):
        """Ping processes in parked state, at least every 60 seconds"""
        try:
            self.manager_ping_parked_processes()
        except Exception as exc:
            self.log.error('Exception in manager_ping_parked_processes')
            self.log.exception(exc)
            self._ctx.rollback()
        else:
            self._ctx.commit()

    #
    # message receivers
    #

    def do_checkqueue(self, parameter, packet):
        if self.manager_start_queued_processes():
            self._ctx.commit()
            self.send(
                Packet.Reply(packet, {'status': 201, 'text': 'OK'})
            )
            self._ctx.db_close()
            return

        self._ctx.rollback()

        self.send(
            Packet.Reply(packet, {'status': 400, 'text': 'NO'})
        )
        self._ctx.db_close()

    def do_disabled(self, parameter, packet):
        """
        Disable the starting of new processes
        """
        self._enabled = False
        self.log.info(
            'DoDisable: Workflow manager is now disabled, now new processes '
            'will be started.'
        )
        self.manager_record_state()
        self._ctx.commit()
        self._ctx.db_close()
        return

    def do_enable(self, parameter, packet):
        """
        Enable the running of processes
        """
        self._enabled = True
        self.log.info(
            'DoDisable: Workflow manager is now enabled, '
            'new processes may be started.'
        )
        self.manager_record_state()
        self._ctx.commit()
        return

    def do_failed(self, parameter, packet):
        """
        A process is reported as failed.
        TODO: what about parent process that may be parked?
        """
        process_id = long(parameter)
        self.log.info(
            'Request to mark OGo#{0} [Process] as failed.'
            .format(process_id, )
        )
        self.send_to_process_log(
            process_id, 'Process reported as state "F" (failed)'
        )
        process = self._ctx.run_command('process::get', id=process_id, )

        if not process:
            self.log.debug(
                'DoFail: OGo#{0} [Process] not found'
                .format(process_id, )
            )
            self.manager_deregister_process(process_id)
            self._ctx.rollback()
            if not self._enabled:
                self._ctx.db_close()
            return

        if process.state == 'R':
            """
            A process may mark *ITSELF* as failed, but since something
            went wrong this is here as a double-check.
            """
            self.log.warn(
                'DoFail: Marking "running" OGo#{0} [Process] as failed.'
                .format(process_id, )
            )
            self.send_administrative_notice(
                category='workflow',
                urgency=4,
                subject='Defunct OIE Worker Detected',
                message=(
                    'Detected OGo#{0} [Process] in defunct state, '
                    'process will be failed.'.format(process_id, )
                )
            )

            process.state = 'F'

        self.manager_deregister_process(process_id)

        self.manager_record_state()

        self._ctx.commit()
        if not self._enabled:
            self._ctx.db_close()

        self.send_to_process_log(
            process_id, 'Manager set state of process to failed.',
        )

    def do_completed(self, parameter, packet):
        process_id = long(parameter)
        self.log.info(
            'DoComplete: OGo#{0} [Process] reported completed'
            .format(process_id, )
        )
        self.send_to_process_log(
            process_id, 'Process reported as state "C" (completed)'
        )
        try:
            self.manager_process_hierarchy_check(process_id)
        except Exception as exc:
            self.log.error('Exception in manager_process_hierarchy_check')
            self.log.exception(exc)
        self.manager_deregister_process(process_id)
        self.manager_start_queued_processes()
        self._ctx.commit()
        if not self._enabled:
            self._ctx.db_close()

    def do_parked(self, parameter, packet):
        """
        A process has reported as parked
        """
        process_id = long(parameter)
        self.log.info(
            'OGo#{0} [Process] reported parked'.format(process_id, )
        )
        self.send_to_process_log(
            process_id, 'Process reported as state "P" (parked)',
        )
        self.manager_deregister_process(process_id)
        self.manager_start_queued_processes()
        self._ctx.commit()
        if not self._enabled:
            self._ctx.db_close()

    def do_is_running(self, parameter, packet):
        """
        A process has been reported as running
        """
        pid = long(packet.data['processId'])
        if packet.data['running'] == 'YES':
            self.log.info(
                'OGo#{0} [Process] reported as running by {1}'
                .format(pid, packet.source, ))
            self.manager_record_pong(pid)
        else:
            miss_count = 1
            if pid in self.ps:
                self.ps[pid]['missCount'] += 1
                miss_count = self.ps[pid]['missCount']
            self.log.info(
                'OGo#{0} [Process] reported as not '
                'running, occurance #{1}'.format(pid, miss_count, )
            )
            if miss_count > 3:
                self.log.info(
                    'DoIsRunning: OGo#{0} [Process] possible zombie, '
                    'has missed more than two run scans'.format(pid, )
                )
                self.manager_detect_zombie(pid)
        self._ctx.commit()
        if not self._enabled:
            self._ctx.db_close()

    def do_queue(self, parameter, packet):
        """Request to change state of process to queued."""

        if not self._enabled:
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 400, 'text': 'Engine in maintenance mode', }
                )
            )

        process_id = long(parameter)

        self.log.debug(
            'DoQueue: Request to queue OGo#{0} [Process].'
            .format(process_id, )
        )
        self.send_to_process_log(
            process_id, 'Request to place in queued state.',
        )

        process = self._ctx.run_command('process::get', id=process_id, )

        if not process:
            self.log.warn(
                'DoQueue: Request to queue OGo#{0} [Process] but process '
                'could not be found.'.format(process_id, )
            )
            self.send(
                Packet.Reply(
                    packet, {'status': 404, 'text': 'No such process', }
                )
            )
            self._ctx.rollback()
            return

        self.log.debug(
            'DoQueue: OGo#{0} [Process] state is "{1}"'
            .format(process_id, process.state, )
        )

        if process.state in ('I', 'H', 'P', ):
            """Process in state to queued"""
            old_state = process.state
            process.state = 'Q'
            self.manager_record_state()
            self.log.debug(
                'DoQueue: OGo#{0} [Process] changed into '
                'queued state'.format(process_id, )
            )
            self.send(
                Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
            )
            self.send_to_process_log(
                process.object_id,
                'Manager changed process state to "Q" from state "{0}"'
                .format(old_state, )
            )
            self.manager_start_queued_processes()
            self._ctx.commit()

        elif process.state == 'Q':
            """Process already queued"""
            self._ctx.rollback()

            self.log.debug(
                'DoQueue: OGo#{0} [Process] already in queued state'
                .format(process_id, )
            )
            self.send_to_process_log(
                process_id, 'Process is already in queued state',
            )
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 201, 'text': 'OK, No action.', },
                )
            )
        else:
            """Process not in an acceptable state to be queued"""
            self._ctx.rollback()

            self.log.info(
                'DoQueue: OGo#{0} [Process] cannot be queued '
                'from state "{1}"'.format(process_id, process.state, )
            )
            message = (
                'OGo#{0} [Process] cannot be queued from state "{1}"'
                .format(process_id, process.state, )
            )
            self.send_to_process_log(process_id, message, )
            self.send(
                Packet.Reply(packet, {'status': 403, 'text': message, }, )
            )

    def do_ps(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {
                    'status': 200,
                    'text': 'OK',
                    'processList': self.ps.values(),
                },
            )
        )

    def manager_record_ping(self, pid):
        if pid in self.ps:
            self.ps[pid]['lastPing'] = time()

    def manager_record_pong(self, pid):

        if pid not in self.ps:
            self.manager_register_process(pid, status='R')
            return

        self.ps[pid]['lastPong'] = time()
        self.ps[pid]['missCount'] = 0
