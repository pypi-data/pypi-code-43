#
# Copyright (c) 2009, 2010, 2012, 2013, 2015, 2016
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
import re
import time
import pprint
import traceback
from lxml import etree
from datetime import datetime, timedelta, date
from xml.sax.saxutils import escape, unescape
from coils.core import Command, CoilsException, AssumedContext
from coils.foundation import BLOBManager


COILS_DEFAULT_NAMESPACES = {
    'dsml': u'http://www.dsml.org/DSML',
    'apache': u'http://apache.org/dav/props',
    'caldav': u'urn:ietf:params:xml:ns:caldav',
    'carddav': u'urn:ietf:params:xml:ns:carddav',
    'coils': u'57c7fc84-3cea-417d-af54-b659eb87a046',
    'ogo': 'http://www.opengroupware.us/model',
    'dav': u'dav',
    'xhtml': u'http://www.w3.org/1999/xhtml',
    'mswebdav': u'urn:schemas-microsoft-com',
}

COILS_XML_MIMETYPES = [
    'application/xml', 'text/xml',
]


def week_ranges_of_month(year, month):
    weeks = []
    tmp = datetime(year, month, 1)
    week = []
    while tmp.month == month:
        week.append(tmp.day)
        if tmp.weekday() == 6:
            weeks.append(week)
            week = []
        tmp += timedelta(days=1)
    if week:
        weeks.append(week)
    return weeks


def week_offset_of_date(dt):
    week_ranges = week_ranges_of_month(dt.year, dt.month)
    counter = 0
    for week in week_ranges:
        if dt.day in week:
            break
        counter += 1
    return (counter + 1,
            week_ranges[counter][0],
            week_ranges[counter][-1], )


def week_range_name_of_date(dt):
    week_number, start_day, end_day = week_offset_of_date(dt)
    return '{0:02d}-{1:02d}'.format(start_day, end_day)


class ActionCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self._rfile = None
        self._wfile = None
        self._shelf = None
        self._proceed = True
        self._continue = True
        self._input_xml_doc = None
        self._input_xml_nsm = None
        self._gong_timer = None

#
# Implement your action here!
#

    def parse_xpath_value_from_input(self, path):
        if not self._input_xml_doc:
            '''
            if self.input_mimetype not in COILS_XML_MIMETYPES:
                raise CoilsException(
                    'Input message must be an XML payload in order to '
                    'use XPath: parameter strings. Input message MIME '
                    'type is "{0}"'.format(self.input_message, ))
            '''
            self._input_xml_doc = etree.parse(self._rfile)
            self.log.debug('Content of XML input message parsed')
            nsm = self._input_xml_doc.getroot().nsmap
            for ab, ns in COILS_DEFAULT_NAMESPACES.items():
                if ab not in nsm:
                    nsm[ab] = ns
            self._input_xml_nsm = nsm
            for illegal_namespace_value in ('', None, ):
                if illegal_namespace_value in self._input_xml_nsm:
                    self.log_message(
                        'Removing illegal namespace value "{0}" '
                        'from XPath namespace map'
                        .format(illegal_namespace_value, ),
                        category='debug',
                    )
                    del self._input_xml_nsm[illegal_namespace_value]
        if path.startswith('$XPath:'):
            xpath = path[7:]
        else:
            xpath = path
        self.log_message(
            'Evaluating XPath expression "{0}" for action parameter value'
            .format(xpath, ),
            category='debug',
        )
        try:
            self.log.debug(
                'Evaluating XPath for parameter value: {0}'.
                format(xpath, )
            )
            result = self._input_xml_doc.xpath(
                xpath,
                namespaces=self._input_xml_nsm,
            )
        except Exception as exc:
            # record exception in process log
            self.log_message(
                'XPath evaluation of "{0}" against message {1} failed:\n'
                '{2}\n'
                'XPath namespace dictionary = {3}'
                .format(
                    xpath,
                    self.input_message,
                    traceback.format_exc(),
                    pprint.pformat(nsm),
                ),
                category='error',
            )
            # log exception in server's log
            self.log.error(
                'Error evaluating XPath expression {0} against "{1}"'.
                format(xpath, self.input_message, )
            )
            self.log.exception(exc)
            raise exc

        if not result:
            self.log_message(
                'No result for XPath expression "{0}"'.format(xpath, ),
                category='debug',
            )
            return None

        result = result[0]
        self.log_message(
            'Result for XPath expression is of type {0}'
            .format(type(result), ),
            category='debug',
        )
        if isinstance(result, basestring):
            self.log.debug('XPath result is type string')
        else:
            self.log.debug('XPath result is not a string; serializing.')
            result = etree.tostring(result)
        self.log.debug(
            'Returning {0}b from XPath evaluation'.format(len(result), )
        )
        return result

    def parse_action_parameters(self):
        pass

    def do_action(self):
        # Child MUST implement
        pass

    def do_epilogue(self):
        # Child MAY implement
        pass

    def audit_action(self):
        # Disable logging!
        pass

#
# Properties
#

    @property
    def rfile(self):
        return self._rfile

    @property
    def wfile(self):
        return self._wfile

    @property
    def input_message(self):
        return self._input

    @property
    def input_mimetype(self):
        return self._input_mimetype

    @property
    def action_parameters(self):
        return self._params

    @property
    def process(self):
        return self._process

    @property
    def pid(self):
        return self._process.object_id

    @property
    def state(self):
        return self._state

    @property
    def result_mimetype(self):
        # Actions that produce output other than XML MUST override this so that
        # their messages are approprately marked.
        return 'application/xml'

    @property
    def result_encoding(self):
        # TODO: Document
        return 'binary'

    @property
    def scope_stack(self):
        return self._scope

    @property
    def scope_tip(self):
        # Returns the outermost scope id; which is the UUID of the action which
        # created the scope.  Scopes are created by the Workflow Executor's
        # Process workers.  Honoring scope is implemented in the appropriate
        # Workflow bundle's Logic commands.
        if (len(self._scope) > 0):
            return self._scope[-1]
        return None

    @property
    def shelf(self):
        # CLUSTER-TODO
        # WARN: shelf transfer needs to be dealt with to add clustering
        if (self._shelf is None):
            self._shelf = BLOBManager.OpenShelf(uuid=self._process.uuid)
            self.log.debug(
                'Shelf {0} open for {1}.'.
                format(
                    self._shelf,
                    self._process.uuid,
                )
            )
        return self._shelf

    @property
    def uuid(self):
        return self._uuid

#
# Utility
#

    def encode_text(self, text, encoding='utf-8'):
        '''
        Wraps xml.sax.saxutils.escape so descendents don't have
        to do an import .
        TODO: should we unicode BEFORE we escape???
        '''
        if isinstance(text, unicode):
            return escape(text)
        return unicode(escape(text), encoding, )

    def decode_text(self, text):
        '''
        Wraps xml.sax.saxutils.unescape so descendents don't have
        to do an import .
        '''
        return unescape(text)

    def store_in_message(
        self,
        label,
        wfile,
        mimetype='application/octet-stream',
        in_transaction=True,
    ):
        '''
        Store the contents of wfile into a message with the specified
        label and MIME type.  A new message will be created in no message
        with the given label exists in the current scope.

        If in_transaction==False perform the message storage in an isolated
        transaction, otherwise the message storage occurs in the transaction
        of the action.
        '''
        if in_transaction:
            ctx = self._ctx
        else:
            ctx = AssumedContext(self._ctx.account_id)
            self.log.debug(
                'Storing workflow message in auxilliary transaction'
            )

        message = None
        if label is not None:
            message = ctx.run_command(
                'message::get',
                process=self._process,
                scope=self._scope,
                label=label,
            )
        if message is None:
            ctx.run_command(
                'message::new',
                process=self._process,
                handle=wfile,
                scope=self.scope_tip,
                mimetype=mimetype,
                label=label,
            )
        else:
            ctx.run_command(
                'message::set',
                object=message,
                handle=wfile,
                mimetype=mimetype,
            )

        if not in_transaction:
            ctx.commit()
            self.log.debug(
                'Auxilliary transaction committed'
            )
            ctx.close()

    def log_message(self, message, category=None):
        if category is None:
            category = 'info'
        if (self._ctx.amq_available):
            self._ctx.send(None,
                           'coils.workflow.logger/log',
                           {'process_id': self._process.object_id,
                            'stanza': self.uuid,
                            'category': category,
                            'message': message, }, )
        else:
            self.log.debug('[{0}] {1}'.format(category, message))

#
# Internal - these methods should never be overridden
#

    def run(self):
        self.do_prepare()
        self.parse_action_parameters()
        if (self.verify_action()):
            self.do_action()
            '''
            Must close _rfile before _wfile so messages can replace themselves!
            '''
            self._rfile.close()
            # Flush the output temp file
            self._wfile.flush()
            self.store_in_message(
                self._label,
                self._wfile,
                self.result_mimetype,
            )
            BLOBManager.Delete(self._wfile)
            self.do_epilogue()
            if (self._shelf is not None):
                self._shelf.close()
        else:
            raise CoilsException('Action verification failed.')
        self._result = (self._continue, self._proceed)

    def set_proceed(self, value):
        self._proceed = bool(value)

    def set_continue(self, value):
        self._continue = bool(value)

    def parse_parameters(self, **params):
        self._input = params.get('input', None)
        self._label = params.get('label', None)
        self._params = params.get('parameters', {})
        self._process = params.get('process')
        self._uuid = params.get('uuid')
        self._scope = params.get('scope', [])
        self._state = params.get('state', None)
        self._service = params.get('service', None)

    @staticmethod
    def get_builtin_value(ctx, process, label):
        """
        Return the value of the specified built-in label. This method is
        static as it is used both by this classes process_label_substitutions
        method and called possibly when creating XATTR values for processes
        created by the schedular component.

        :param ctx: The current operational context.
        :param process: The current process entity
        :param label: The full text of the label
        """

        # Tests for label values are in the CoilsCoreLogiActionLabelsTest test
        # tests/coils_cor_logic_action_labels

        if label == '$__DATE__;':
            return datetime.now().strftime('%Y%m%d')
        elif label == '$__TODAY__;':
            return date.today().strftime('%Y-%m-%d')
        elif label == '$__YESTERDAY__;':
            return (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        elif label == '$__WEEKAGO__;':
            return (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif label == '$__FORTNIGHTAGO__;':
            return (date.today() - timedelta(days=14)).strftime('%Y-%m-%d')
        elif label == '$__MONTHAGO__;':
            return (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif label == '$__TOMORROW__;':
            return (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif label == '$__USCIVILIANDATE__;':
            return datetime.now().strftime('%m/%d/%Y')
        elif label == '$__OMPHALOSDATE__;':
            return datetime.now().strftime('%Y-%m-%d')
        elif label == '$__MONTHSTART__;':
            return datetime.now().strftime('%Y-%m-01')
        elif label == '$__DATETIME__;':
            return datetime.now().strftime('%Y%m%dT%H:%M')
        elif label == '$__OMPHALOSDATETIME__;':
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        elif label == '$__NOW_Y2__;':
            return datetime.now().strftime('%y')
        elif label == '$__NOW_Y4__;':
            return datetime.now().strftime('%Y')
        elif label == '$__NOW_M2__;':
            return datetime.now().strftime('%m')
        elif label == '$__INITDATE__;':
            return process.created.strftime('%Y-%m-%d')
        elif label == '$__PID__;':
            return str(process.object_id)
        elif label == '$__PARENTPID__;':
            if process.parent_id:
                return str(process.parent_id)
            return ''
        elif label == '$__UUID__;':
            return process.uuid
        elif label == '$__GUID__;':
            return process.uuid[1:-1]
        elif label == '$__TASK__;':
            return str(process.task_id)
        elif label == '$__EMAIL__;':
            return ctx.email
        elif label == '$__LOGIN__;':
            return ctx.login
        elif label == '$__WEEKOFMONTH__;':
            return week_range_name_of_date(datetime.today())
        elif label == '$__ROUTE__;':
            if process.route:
                return process.route.name
            else:
                return u'UNKNOWN'
        else:
            '''
            self.log.debug(
                'Encountered unknown {0} content alias'.format(label)
            )
            '''
            pass
        return None

    @staticmethod
    def scan_and_replace_labels(
        ctx,
        process,
        text,
        default=None,
        builtin_only=False,
        scope=None,
    ):
        # Process special internal labels

        if not isinstance(text, basestring):
            return text

        labels = set(re.findall('\$__[A-z0-9]*__;', text))
        for label in labels:
            if label[0:9] == '$__XATTR_' and not builtin_only:
                propname = label[9:-3].lower()
                prop = ctx.property_manager.get_property(
                    process,
                    'http://www.opengroupware.us/oie',
                    'xattr_{0}'.format(propname, )
                )
                if prop:
                    value = str(prop.get_value())
                    text = text.replace(label, value)
                else:
                    if not default:
                        raise CoilsException(
                            'Encountered unknown xattr reference "{0}"'.
                            format(propname, )
                        )
                        # text = text.replace(label, '')
                    else:
                        text = text.replace(label, default)
            else:
                value = ActionCommand.get_builtin_value(ctx, process, label)
                if value:
                    text = text.replace(label, value)

        # Do not scan for message labels in builtin-only mode
        if builtin_only:
            return text

        # Process message labels
        labels = set(re.findall('\$[A-z0-9]*;', text))
        if len(labels) == 0:
            return text
        for label in labels:
            try:
                data = ctx.run_command('message::get-text',
                                       process=process,
                                       scope=scope,
                                       label=label[:-1][1:], )
            except Exception as exc:
                raise exc
            text = text.replace(label, data)
        return text

    def gong(self):
        """
        send an i-am-running message to the executor
        """
        if self._ctx.amq_available:
            now_time = time.time()
            if not self._gong_timer:
                self._gong_timer = now_time
            elif (now_time - self._gong_timer) > 17.0:
                # Ping the executor that this worker is running!
                self._ctx.send(
                    'coils.workflow.process.{0}/__null'.format(self.pid, ),
                    'coils.workflow.executor/running',
                    {'processId': self.pid, },
                )
                self.log_message(
                    'gong (is_running) message sent after {0}s'
                    .format(now_time - self._gong_timer, ),
                    category='debug',
                )
                self._ctx.log.debug('gong message sent')
                self._gong_timer = time.time()
                if self._service:
                    # we have a reference to our service component
                    self._ctx.log.debug('calling service\'s gong method')
                    counter = 0
                    while self._service.gong():
                        # drain the service's message queue
                        counter += 1
                    self.log_message(
                        'service processed {0} messages during gong'
                        .format(counter, ),
                        category='debug',
                    )
        else:
            self._ctx.log.debug('gong message not sent, bus not available')

    def process_label_substitutions(
        self,
        text,
        default=None,
        builtin_only=False,
    ):
        """
        Process the provided text for any values that should be replaced.
        This includes referrences to messages by label, references to
        extended attributes [aka XATTRs], and usable of built-in labels.

        :param text: The text to be scanned for labels.
        :param default: A default value to be used as the value for any
            message reference to which a corresponding XATTR reference
            where the XATTR does not exist.
        :param builtin_only: Only process for built-in labels.
        """

        # guardian clauses
        if not text:
            return ''
        if isinstance(text, basestring):
            if len(text) < 3:
                return text
            else:
                pass
        else:
            return text

        value = ActionCommand.scan_and_replace_labels(
            self._ctx,
            self._process,
            text,
            default=default,
            builtin_only=builtin_only,
            scope=self._scope,
        )
        # XPath: prefix'd parameter support
        if isinstance(value, basestring):
            if value.startswith('$XPath:'):
                return self.parse_xpath_value_from_input(value)
        return value

    def verify_action(self):
        # Make sure an action has the three requisite components for execution
        # 1.) An Input
        # 2.) A process context
        # 3.) A copy of the current Process state
        # if (self._input is None):
        #    raise CoilsException('No input message specified for action.')
        if (self._process is None):
            raise CoilsException('No process associated with action.')
        if (self._state is None):
            raise CoilsException('No process state provided for action.')
        return True

    def do_prepare(self):
        if (self._input is None):
            self._rfile = BLOBManager.ScratchFile()
            self._input_mimetype = 'application/octet-stream'
            self.log_message(
                'No message provided for input',
                category='debug',
            )
        else:
            self._rfile = self._ctx.run_command(
                'message::get-handle', object=self._input,
            )
            self._input_mimetype = self._input.mimetype
        self._wfile = BLOBManager.ScratchFile(
            suffix='message',
            encoding=self.result_encoding,
        )
        self.log_message(
            'Opened target message file as encoding "{0}"'
            .format(self.result_encoding, ),
            category='debug',
        )
