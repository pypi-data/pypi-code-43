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
import uuid
import time
import traceback
from email.mime.text import MIMEText
from email.Utils import formatdate
from sqlalchemy.exc import IntegrityError
from coils.core import \
    ThreadedService, \
    Packet, \
    ServerDefaultsManager, \
    AdministrativeContext, \
    SMTP, \
    ObjectInfoManager, \
    DocumentVersion, \
    CoilsException
from perflog import PerformanceLog

MSG_UNEXPECTED_EXC_OBJINFO_REPAIR = \
    'Unexpected exception repairing ObjectInfo for OGo#{0}'

ATTACHMENT_OVERKEEP_THRESHOLD = 14400  # Four hours
ATTACHMENT_EXPIRATION_INTERVAL = 14400  # Four hours

LOCK_OVERKEEP_THRESHOLD = 14400  # Four hours
LOCK_EXPIRATION_INTERVAL = 28800  # Eight hours

CHECKSUM_BUILD_INTERVAL = 14400  # Four hours
CHECKSUM_ITERATION_LIMIT = 50  # Only fix 50 documents per interval

TOKEN_OVERKEEP_THRESHOLD = 86400  # 24 hours
TOKEN_EXPIRATION_INTERVAL = 86400  # Eight hours

ADMIN_EXPIRE_ATTACHMENTS = 200
ADMIN_EXPIRE_LOCKS = 201
ADMIN_EXPIRE_TOKENS = 202
ADMIN_CHECKSUM_BUILD = 203


COMMAND_MAP = {
    ADMIN_EXPIRE_ATTACHMENTS: 'job_expire_attachments',
    ADMIN_EXPIRE_LOCKS: 'job_expire_locks',
    ADMIN_EXPIRE_TOKENS: 'job_expire_tokens',
    ADMIN_CHECKSUM_BUILD: 'job_checksum_build',
}


class AdministratorService (ThreadedService):
    __service__ = 'coils.administrator'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)
        self._id_queue = []

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext(
            {},
            broker=self._broker,
            component_name=self.__service__,
        )
        self._sd = ServerDefaultsManager()
        server_uuid_prop = self._ctx.property_manager.get_server_property(
            'http://www.opengroupware.us/global',
            'clusterGUID',
        )
        if (server_uuid_prop is None):
            self._cluster_guid = '{{{0}}}'.format(str(uuid.uuid4()))
            self._ctx.property_manager.set_server_property(
                'http://www.opengroupware.us/global',
                'clusterGUID',
                self._cluster_guid,
            )
            self._ctx.commit()
        else:
            self._cluster_guid = server_uuid_prop.get_value()
            server_uuid_prop = None

        """
        Setup periodic job for attachment expiration
        Run every ATTACHMENT_EXPIRATION_INTERVAL seconds
        """
        self.schedule_at_interval(
            'attachmentExpiration',
            message=ADMIN_EXPIRE_ATTACHMENTS,
            seconds=ATTACHMENT_EXPIRATION_INTERVAL,
        )

        """
        Setup periodic job for attachment expiration
        Run every LOCK_EXPIRATION_INTERVAL seconds
        """
        self.schedule_at_interval(
            'lockExpiration',
            message=ADMIN_EXPIRE_LOCKS,
            seconds=LOCK_EXPIRATION_INTERVAL,
        )

        """
        Setup periodic job for token expiration
        Run every TOKEN_EXPIRATION_INTERVAL seconds
        """
        self.schedule_at_interval(
            'tokenExpiration',
            message=ADMIN_EXPIRE_TOKENS,
            seconds=TOKEN_EXPIRATION_INTERVAL,
        )

        """
        Setup periodic job for document checksum build
        Run every CHECKSUM_BUILD_INTERVAL seconds
        """
        self.schedule_at_interval(
            'checksumBuild',
            message=ADMIN_CHECKSUM_BUILD,
            seconds=CHECKSUM_BUILD_INTERVAL,
        )

        """
        Setup Performance Log
        """
        self.perflog = PerformanceLog()
        self.proxylog = dict()
        self.rpc2log = dict()
        self._ctx.db_close()

    def job_expire_attachments(self, data):
        count = 0
        try:
            count = self._ctx.run_command(
                'attachment::expire',
                overkeep=ATTACHMENT_OVERKEEP_THRESHOLD,
            )
        except Exception as exc:
            self.send_notice(
                subject='Exception occured during Attachment expiration.',
                message=(
                    '{0} Attachments expired.\n'
                    'Exception: {1}\n{2}\n'
                    .format(
                        count,
                        exc,
                        traceback.format_exc(),
                    )
                ),
                urgency=8,
                category='error',
                alert_id='attachmentExpiration',
            )
            self.log.debug('Rolling back Attachment expiration transaction.')
            self._ctx.rollback()
            self.log.debug('Attachment expiration transaction rolled back.')
        else:
            self.log.debug('Committing Attachment expiration transaction.')
            self._ctx.commit()
            self.log.debug('Attachment expiration transaction committed.')
            self.send_notice(
                subject='Attachment expiration performed',
                message=(
                    '{0} attachments expired from data store'.format(count, )
                ),
                urgency=1,
                category='data-retention',
                alert_id='attachmentExpiration',
            )
        finally:
            self._ctx.db_close()

    def job_expire_locks(self, data):
        if self._ctx.lock_manager.administratively_expire_locks(
            overkeep=ATTACHMENT_OVERKEEP_THRESHOLD
        ):
            self._ctx.commit()
        else:
            self._ctx.rollback()
        self._ctx.db_close()

    def job_expire_tokens(self, data):
        count = 0
        try:
            count = self._ctx.run_command(
                'token::expire',
                overkeep=TOKEN_OVERKEEP_THRESHOLD,
            )
        except Exception as exc:
            self.send_notice(
                subject='Exception occured during token expiration.',
                message=(
                    '{0} tokens expired.\n'
                    'Exception: {1}\n{2}\n'
                    .format(
                        count,
                        exc,
                        traceback.format_exc(),
                    )
                ),
                urgency=8,
                category='error',
                alert_id='tokenExpiration',
            )
            self._ctx.rollback()
        else:
            self._ctx.commit()
            self.send_notice(
                subject='Token expiration performed',
                message=(
                    '{0} token expired from data store'.format(count, )
                ),
                urgency=1,
                category='data-retention',
                alert_id='tokenExpiration',
            )
        finally:
            self._ctx.db_close()

    def job_checksum_build(self, data):
        count = 0
        db = self._ctx.db_session()
        try:
            document_versions = db.query(DocumentVersion).filter(
                DocumentVersion.checksum == None
            ).limit(CHECKSUM_ITERATION_LIMIT).all()
            if len(document_versions) == 0:
                self.log.info('Found no document versions without checksum.')
                return
            for document_version in document_versions:
                document = document_version.document
                if not document:
                    raise CoilsException(
                        'Could not marshall document for documentVersion; '
                        'OGo#{0} [Document] / OGo#{1} [documentVersion]'
                        .format(
                            document_version.document_id,
                            document_version.object_id,
                        )
                    )
                document_version.checksum = self._ctx.run_command(
                    'document::generate-checksum',
                    document=document,
                    version=document_version.version,
                )
                count += 1
        except Exception as exc:
            self.send_notice(
                subject='Exception occured during Checksum Build task.',
                message=(
                    '{0} document checksums generate.\n'
                    'Exception: {1}\n{2}\n'
                    .format(
                        count,
                        exc,
                        traceback.format_exc(),
                    )
                ),
                urgency=8,
                category='error',
                alert_id='checksumGeneration',
            )
            self.log.debug('Rolling back checksum build transaction.')
            self._ctx.rollback()
            self.log.debug('Checksum build transaction rolled back.')
        else:
            self.log.debug('Committing checksum build transaction.')
            self._ctx.commit()
            self.log.debug('Checksum build transaction committed.')
            self.send_notice(
                subject='Checksum build performed',
                message=(
                    '{0} checksum generated for document version'
                    .format(count, )
                ),
                urgency=1,
                category='data-retention',
                alert_id='checksumGeneration',
            )
        finally:
            self._ctx.db_close()

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

    @property
    def administrative_email(self):
        return self._sd.string_for_default(
            'AdministrativeEMailAddress',
            value='root@localhost',
        )

    def send_notice(
        self,
        subject,
        message,
        urgency=5,
        category='unspecified',
        alert_id=None,
    ):
        if (subject is None):
            subject = (
                u'[OpenGrouware] Administrative Notice {0}'.
                format(alert_id, )
            )
        else:
            subject = u'[OpenGroupware] {0}'.format(subject)
        message = MIMEText(message)
        message['Subject'] = subject
        message['From'] = ''
        message['To'] = self.administrative_email
        message['Date'] = formatdate(localtime=True)
        message['X-Opengroupware-Alert'] = alert_id
        message['X-Opengroupware-Cluster-GUID'] = self._cluster_guid
        SMTP.send('', [self.administrative_email, ], message)
        self.log.info('Message sent to administrator.')
        return True

    #
    # Message Handlers
    #

    def do_expire_attachments(self, parameter, packet):
        self.log.info(
            'Request to expire attachments received via bus from "{0}".'
            .format(
                packet.source,
            )
        )
        self.event_queue.put((ADMIN_EXPIRE_ATTACHMENTS, None, ))
        self.send(
            Packet.Reply(
                packet,
                {
                    'status': 200,
                    'text': 'OK',
                }
            )
        )

    def do_get_server_defaults(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'OK',
                 'GUID': self._cluster_guid,
                 'defaults': self._sd.defaults, }
            )
        )

    def do_get_cluster_guid(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'OK',
                 'GUID': self._cluster_guid, }
            )
        )

    def do_notify(self, parameter, packet):
        try:
            self.log.info('Received a request to notify administrator')
            category = packet.data.get('category', 'unspecified')
            urgency = packet.data.get('urgency', 5)
            subject = packet.data.get('subject', None)
            message = unicode(packet.data.get('message'))
            self.send_notice(
                subject,
                message,
                urgency=urgency,
                category=category,
                alert_id=packet.uuid,
            )
        except Exception as exc:
            # TODO: log something and make response more informative
            self.log.exception(exc)
            self.send(
                Packet.Reply(
                    packet, {
                        'status': 500,
                        'text': 'Failure',
                    }
                )
            )
        else:
            self.send(
                Packet.Reply(
                    packet,
                    {
                        'status': 201,
                        'text': 'OK',
                    }
                )
            )

    def do_repair_objinfo(self, parameter, packet):
        self.log.info(
            'Request from {0} to repair Object Info for objectId#{1}'.
            format(packet.source, parameter, )
        )
        try:
            object_id = int(parameter)
        except:
            self.log.error(
                'Received non-integer value for objinfo repair request'
            )
        else:
            if object_id < 1000:
                return
            om = ObjectInfoManager(self._ctx, log=self.log, service=self, )
            try:
                if (om.repair(object_id=object_id)):
                    self.log.debug(
                        'Object Info repaired for objectId#{0}'
                        .format(object_id, )
                    )
                else:
                    self.log.info(
                        'No action performed, ObjectInfo is not '
                        'modified (objectId#{0})'
                        .format(object_id, )
                    )
                self._ctx.flush()
            except IntegrityError as exc:
                self.log.info(
                    'IntegrityError repairing Object Info, assuming OK. We '
                    'are likely just behind the front-end worker.'
                )
                self._ctx.rollback()
            except Exception as exc:
                self.log.error(
                    MSG_UNEXPECTED_EXC_OBJINFO_REPAIR.format(object_id, )
                )
                self.log.exception(exc)
                self.send_notice(
                    (
                        MSG_UNEXPECTED_EXC_OBJINFO_REPAIR.format(object_id, )
                    ),
                    str(exc),
                )
                self._ctx.rollback()
            else:
                self._ctx.commit()
            finally:
                self._ctx.db_close()
                om = None

    def do_performance_log(self, parameter, packet):
        try:
            lname = packet.data.get('lname')
            oname = packet.data.get('oname')
            runtime = packet.data.get('runtime')
            error = packet.data.get('error')
        except Exception as exc:
            self.log.error(
                'Unable to parse performance log packet from "{0}"'.
                format(packet.source, )
            )
            self.log.exception(exc)
        else:
            try:
                self.perflog.insert_record(
                    lname, oname, runtime=runtime, error=error,
                )
            except Exception as exc:
                self.log.error('Error updating performance statistics')
                self.log.exception(exc)
                self.send_notice(
                    'Error updating performance statistics',
                    str(exc)
                )

    def do_get_performance_log(self, parameter, packet):
        try:
            self.log.info(
                'Request for performance log from "{0}"'.
                format(packet.source, )
            )
            data = self.perflog.data.get(parameter, {})
        except Exception, e:
            self.log.error('Exception retrieving performance statistics')
            self.log.exception(e)
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 500, 'text': 'Exception', }
                )
            )
        else:
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 200,
                     'text': 'Performance Log Data',
                     'payload': data, },
                )
            )

    def do_proxy_log(self, parameter, packet):
        self._do_rpc_log(parameter, packet, self.proxylog, )

    def do_rpc2_log(self, parameter, packet):
        self._do_rpc_log(parameter, packet, self.rpc2log, )

    def do_get_proxy_log(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {
                    'status': 200,
                    'text': 'Proxy Log Data',
                    'payload': self.proxylog.values(),
                },
            )
        )

    def do_get_rpc2_log(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {
                    'status': 200,
                    'text': 'RPC2 Log Data',
                    'payload': self.rpc2log.values(),
                },
            )
        )

    def _do_rpc_log(self, parameter, packet, calllog):
        try:
            callid = packet.data.get('callid')
            status = packet.data.get('status', 'new')
            login = packet.data.get('login', None)
            method = packet.data.get('method', None)
            params = packet.data.get('params', None)
            duration = packet.data.get('duration', None)
            result = packet.data.get('result', None)
            errors = packet.data.get('errors', None)
        except Exception as exc:
            self.log.error(
                'Unable to parse RPC log packet from "{0}"'.
                format(
                    packet.source,
                )
            )
            self.log.exception(exc)
        else:
            if status == 'new':
                calllog[callid] = {
                    'callid': callid,
                    'errors': 0,
                    'status': 'new',
                    'login': login,
                    'method': method,
                    'params': params,
                    'duration': 0,
                    'result': '',
                    'time': time.time(),
                }
            else:
                if callid in calllog:
                    calllog[callid]['status'] = status
                    calllog[callid]['duration'] = duration
                    calllog[callid]['result'] = result
                    calllog[callid]['errors'] = errors
                else:
                    self.log.warn(
                        'Received proxy log update for unknown call'
                    )

        if len(calllog) > 512:
            floor_time = time.time() - 300  # Five minutes
            callids_to_delete = [
                x['callid'] for x in calllog.values()
                if x['time'] < floor_time
            ]
            for callid in callids_to_delete:
                del calllog[callid]
