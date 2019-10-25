#
# Copyright (c) 2010, 2011, 2013, 2015, 2016
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
import traceback
import Queue
from uuid import uuid4
from datetime import datetime
from time import time
from coils.core import \
    ThreadedService, \
    AdministrativeContext, \
    BLOBManager, \
    Packet, \
    ProcessLogEntry

LOGGER_FLUSH = 200
LOGGER_TASK_COMMENT = 201

PROCESS_STATE = {
    'Q': 'Queued',
    'I': 'Initialized',
    'R': 'Running',
    'F': 'Failed',
    'C': 'Completed',
    'Z': 'Zombie',
    'X': 'Cancelled',
    'P': 'Parked',
}


class LoggerService(ThreadedService):
    __service__ = 'coils.workflow.logger'
    __auto_dispatch__ = True
    __is_worker__ = False

    def __init__(self):
        ThreadedService.__init__(self)

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext(
            {},
            broker=self._broker,
            component_name=self.__service__,
        )
        self._log_queue = BLOBManager.OpenShelf(uuid='coils.workflow.logger')

        self.schedule_at_interval(
            name='flush process log message queue',
            minutes=2,
            message=LOGGER_FLUSH,
            data=None,
        )

        self._last_flush = None

    def process_service_specific_event(self, event_class, event_data):
        if event_class == LOGGER_FLUSH:
            self._empty_queue()
        elif event_class == LOGGER_TASK_COMMENT:
            self._comment_on_task(event_data)

    def _comment_on_task(self, process_id):
        """
        Comment on the task which is assigned to the process as the Process
        Task.  This places a comment on the task with the current state of
        the process and the process log.
        """

        self.log.debug(
            'Performing task comment for OGo#{0} [Process]'
            .format(process_id, )
        )

        process = self._ctx.run_command('process::get', id=process_id, )
        if not process:
            self.log.debug(
                'Unable to marshall OGo#{0} [Process]'
                .format(process_id, )
            )
            return
        if not process.task_id:
            self.log.debug(
                'No process task assgined to OGo#{0} [Process]'
                .format(process_id, )
            )
            process = None
            return

        # First, flush the queue to the database
        self._empty_queue(close_after=False)

        self.log.debug(
            'Task for OGo#{0} [Process] is OGo#{1}'
            .format(process.object_id, process.task_id, )
        )

        task = self._ctx.run_command('task::get', id=process.task_id, )
        if not task:
            self.log.warn(
                'Cannot marshall OGo#{0} [Task] for OGo#{1} [Process]'
                .format(process.task_id, process_id, )
            )
            self.send_administrative_notice(
                subject=(
                    'Unable to marshall task OGo#{0} to record process log'
                    .format(process.task_id, )
                ),
                message=(
                    'Unable to marshall task OGo#{0} to record process log.'
                    'Expected task comment could not be recorded.'
                    .format(process.task_id, )
                ),
                urgency=5,
                category='workflow'
            )
            process = None
            return

        self.log.debug(
            'Marshalled OGo#{0} [Task]'
            .format(task.object_id, )
        )

        comment = (
            'Process OGo#{0} created at {1} now has a state of "{2}"\n'
            '---Begin Process Log---\n'
            '{3}\n'
            '---End Process Log---\n'
            .format(
                process.object_id,
                process.created,
                PROCESS_STATE.get(process.state, 'undefined', ),
                self._ctx.run_command(
                    'process::get-log',
                    process=process,
                )
            )
        )

        self._ctx.run_command(
            'task::comment',
            task=task,
            values={'comment': comment, }
        )

        self._ctx.commit()
        self._ctx.db_close()

    def _log_message(
        self,
        source,
        process_id,
        message,
        stanza=None,
        timestamp=None,
        category='undefined',
        uuid=None
    ):
        try:
            if (timestamp is None):
                timestamp = float(time())
            if isinstance(message, tuple) or isinstance(message, list):
                # turn the tuple/list into a multi-line string
                message = '\n'.join([str(x).strip() for x in message])
            elif isinstance(message, basestring):
                message = message.strip()
            else:
                message = str(message).strip()
            self._log_queue[uuid4().hex] = (
                source,
                process_id,
                message,
                stanza,
                timestamp,
                category,
                uuid,
            )
            self._log_queue.sync()
        except Exception as exc:
            self.log.exception(exc)
            return False
        else:
            return True

    def _empty_queue(self, close_after=True, ):
        """
        Empy the process log queue into the database.  We hold back a queue
        and write all-at-once to avoid a continuous stream of transactions.
        After the queue is emptied the database connection is closed unless
        the value of close_after is False.
        """
        if self._last_flush:
            self.log.debug(
                'Last process log flush completed @ {0}'
                .format(self._last_flush.isoformat(), )
            )
        else:
            self.log.debug(
                'Performing first process log flush'
            )

        keys = list()
        try:

            for key in self._log_queue:
                (source,
                 process_id,
                 message,
                 stanza,
                 timestamp,
                 category,
                 uuid, ) = self._log_queue[key]

                # prevent excessively long string, trim to maximum lengths
                if stanza is not None:
                    stanza = stanza[:32]
                if category is not None:
                    category = category[:15]
                if source is not None:
                    source = source[:64]
                if uuid is not None:
                    uuid = uuid[:64]

                entry = ProcessLogEntry(
                    source,
                    process_id,
                    message,
                    stanza=stanza,
                    timestamp=timestamp,
                    category=category,
                    uuid=uuid,
                )
                self._ctx.db_session().add(entry)
                keys.append(key)
        except Exception as exc:
            message = (
                'Workflow process message log cannot be flushed to '
                'database.\n{0}'.format(traceback.format_exc(), )
            )
            subject = 'Exception creating process log entry!'
            self.log.error(subject)
            self.log.exception(exc)
            self.send_administrative_notice(
                subject=subject,
                message=message,
                urgency=9,
                category='workflow',
            )
        else:
            try:
                self.log.debug(
                    'Commiting {0} process log entries'.
                    format(len(keys), )
                )
                self._ctx.commit()
            except Exception as exc:
                # TODO: Send an administrative notice!
                self.log.exception(exc)
            else:
                for key in keys:
                    del self._log_queue[key]
            self._log_queue.sync()
            self.log.debug(
                '{0} process log entries purged from queue'.
                format(len(keys), )
            )

        if close_after:
            self._ctx.db_close()

        self.log.debug('Process log flush complete')
        # Update last flush time stampe
        self._last_flush = datetime.now()

    def do_log(self, parameter, packet):
        try:
            source = Packet.Service(packet.source)
            process_id = long(packet.data.get('process_id'))
            message = packet.data.get('message', None)
            stanza = packet.data.get('stanza', None)
            category = packet.data.get('category', 'undefined')
            uuid = packet.uuid
            timestamp = packet.time
        except Exception as exc:
            self.log.exception(exc)
            self._ctx.rollback()
            self.send(
                Packet.Reply(
                    packet,
                    {
                        'status': 500,
                        'text': 'Failure to parse packet payload.',
                    },
                )
            )
        else:
            if self._log_message(
                source,
                process_id,
                message,
                stanza=stanza,
                timestamp=timestamp,
                category=category,
                uuid=uuid,
            ):
                self.send(
                    Packet.Reply(packet, {'status': 201, 'text': 'OK'})
                )
            else:
                self.send(
                    Packet.Reply(
                        packet,
                        {'status': 500,
                         'text': 'Failure to record message.', },
                    )
                )

    def do_reap(self, parameter, packet):
        process_id = int(parameter)
        db = self._ctx.db_session()
        try:
            db.query(ProcessLogEntry).\
                filter(ProcessLogEntry.process_id == process_id).\
                delete(synchronize_session='fetch')
        except Exception as exc:
            self.log.exception(exc)
            self.send(
                Packet.Reply(
                    packet,
                    {
                        'status': 500,
                        'text': 'Failure to purge process log.',
                    }
                )
            )
        else:
            self._ctx.commit()
            self.send(
                Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
            )

    def do_flush(self, parameter, packet):
        try:
            # wait at most two seconds
            self.event_queue.put((LOGGER_FLUSH, packet.data, ), False, 2)
        except Queue.Full:
            self.log.warning(
                'event queue of size {0} is full; flush event skipped.'
                .format(self.event_queue.qsize(), )
            )
        self.send(
            Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
        )

    def do_comment(self, parameter, packet):
        """
        Request to perform process task comment on the process specified by
        the parmeter.
        """
        self.log.debug(
            'Request to perform process task comment for OGo#{0}'
            .format(parameter, )
        )

        try:
            parameter = long(parameter)
        except:
            self.log.error(
                'Comment request received with non-integer parameter of "{0}"'
                .format(parameter, )
            )
        else:
            self.event_queue.put((LOGGER_TASK_COMMENT, parameter, ))
            self.send(
                Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
            )
