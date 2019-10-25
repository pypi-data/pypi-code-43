#
# Copyright (c) 2010, 2012, 2013, 2014, 2015, 2016, 2018, 2019
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
import uuid
import calendar
from StringIO import StringIO
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MO, TU, WE, TH, FR, DAILY
from dateutil.tz import gettz
from xml.sax.saxutils import escape
from coils.core import \
    CoilsException, \
    NotImplementedException, \
    walk_ogo_uri_to_target, \
    BLOBManager, \
    CoilsDateFormatException, \
    Document, \
    Message, \
    StandardXML
from coils.core.xml import Render as RenderAsXML
from coils.logic.workflow.tables import Table
from lxml import etree
import pprint


HARD_NAMESPACES = {
    'dsml': u'http://www.dsml.org/DSML',
    'apache': u'http://apache.org/dav/props',
    'caldav': u'urn:ietf:params:xml:ns:caldav',
    'carddav': u'urn:ietf:params:xml:ns:carddav',
    'coils': u'57c7fc84-3cea-417d-af54-b659eb87a046',
    'omphalos': 'http://www.opengroupware.us/model',
    'dav': u'dav',
    'xhtml': u'http://www.w3.org/1999/xhtml',
    'mswebdav': u'urn:schemas-microsoft-com',
}


class OIEXSLTExtensionPoints:

    def __init__(self, process, context, scope, ctxids):
        self.process = process
        self.context = context
        self.scope = scope
        self.ctxids = ctxids
        self.tables = {}
        self.txt_cache = {}

    def shutdown(self):
        self.txt_cache = {}
        for name, table in self.tables.items():
            table.shutdown()

    def _make_date(self, value, method, param):
        value = value.strip()
        if len(value) == 10:
            value = datetime.strptime(value, '%Y-%m-%d')
        elif len(value) == 19:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            raise CoilsDateFormatException(
                '{0} received value {1} which is not a StandardXML '
                'formatted date: "{2}"'.format(method, param, value, ))
        return value

    def _get_sequence_value(self, scope, name):

        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException(
                'Invalid execution path! Possible security model violation.')

        if not sequence_target:
            raise CoilsException(
                'Unable to determine the target for scope of sequence "{0}"'.
                format(name))

        name = 'sequence_{0}'.format(name.lower(), )

        prop = \
            self.context.property_manager.get_property(
                sequence_target,
                'http://www.opengroupware.us/oie',
                name,
            )

        if prop:
            value = prop.get_value()
            try:
                value = long(value)
            except:
                raise CoilsException(
                    'Workflow sequence value is corrupted: sequence={0} '
                    'value="{1}" scope={2}'.format(name, value, scope, ))
            return value
        else:
            raise CoilsException(
                'No such sequence as "{0}" in scope "{1}" for processId#{2}'.
                format(name, scope, self.process.object_id, ))

    def _set_sequence_value(self, scope, name, value):

        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException(
                'Invalid execution path! Possible security model violation.')

        if not sequence_target:
            raise CoilsException(
                'Unable to determine the target for scope of sequence "{0}"'.
                format(name, ))

        name = 'sequence_{0}'.format(name.lower(), )

        self.context.property_manager.set_property(
            sequence_target,
            'http://www.opengroupware.us/oie',
            name,
            long(value),
        )

    def sequencevalue(self, _, scope, name):
        # TODO: Test
        return self._get_sequence_value(scope, name)

    def sequencereset(self, _, scope, name, value):
        # TODO: Test
        self._set_sequence_value(scope, name, value)

    def sequenceincrement(self, _, scope, name, increment):
        # TODO: Test
        value = self._get_sequence_value(scope, name)
        value += int(increment)
        self._set_sequence_value(scope, name, value)
        return unicode(value)

    def messagetext(self, _, label):
        if label in self.txt_cache:
            return self.txt_cache[label]
        data = self.context.run_command('message::get-text',
                                        process=self.process,
                                        scope=self.scope,
                                        label=label, )
        if not data:
            data = ''
        if len(data) < 32769:
            self.txt_cache[label] = data
        return data

    def _search_for_objects(self, domain, args):
        criteria = []
        while len(args) > 0:
            criteria.append({
                'key': args.pop(0),
                'value': args.pop(0),
            })
        result = self.context.run_command(
            '{0}::search'.format(domain),
            criteria=criteria,
            contexts=self.ctxids,
        )
        return result

    def searchforobjectid(self, _, domain, *args):
        result = self._search_for_objects(domain, list(args))
        if len(result) == 1:
            result = result[0]
            if hasattr(result, 'object_id'):
                return unicode(result.object_id)
        return ''

    def searchforobjects(self, _, domain, *args):
        result = self._search_for_objects(domain, list(args))
        print(
            'oie:searchforobjects found {0} objects'
            .format(len(result), )
        )
        return unicode(
            RenderAsXML.render(result, self.context, detail_level=57311, )
        )

    def xpath(self, _, value, path):
        xmldoc = etree.parse(StringIO(value))
        nsm = xmldoc.getroot().nsmap
        for ab, ns in HARD_NAMESPACES.items():
            if ab not in nsm:
                nsm[ab] = ns
        if '' in nsm:
            del nsm['']
        if None in nsm:
            del nsm[None]
        try:
            result = xmldoc.xpath(path, namespaces=nsm, )
        except Exception as exc:
            self.context.log.error('XPath: {0}'.format(path, ))
            self.context.log.error(
                'XPath namespaces: {0}'.format(pprint.pformat(nsm), )
            )
            self.context.log.exception(exc)
            raise exc
        if result and isinstance(result, list):
            result = result[0]
        elif isinstance(result, list) and not result:
            result = ''
        if not isinstance(result, basestring):
            result = etree.tostring(result)
        return result

    def countobjects(self, _, domain, *args):
        result = self._search_for_objects(domain, list(args))
        return unicode(len(result))

    def tablelookup(self, _, name, *values):
        if name not in self.tables:
            try:
                table = self.context.run_command('table::get', name=name, )
                if not table:
                    raise CoilsException(
                        'Unable to marshall table "{0}"'
                        .format(name, )
                    )
                table.setup(
                    context=self.context,
                    process=self.process,
                    scope=self.scope,
                )
                self.tables[name] = table
            except Exception as exc:
                self.context.log.error(
                    'Exception occuring marshalling table "{0}"'.
                    format(name, )
                )
                self.context.log.exception(exc)
                raise exc
        table = self.tables[name]
        try:
            result = table.lookup_value(*values)
        except Exception as exc:
            self.context.log.error(
                'Exception occurring during look-up '
                'table "{0}" with values {1}'
                .format(
                    name,
                    values,
                )
            )
            self.context.log.exception(exc)
            raise exc
        if result is not None:
            return unicode(result)
        return None

    def reformatdate(self, _, value, format):
        value = self._make_date(value, 'reformatdate', 'date')
        return value.strftime(format)

    def datetimetodate(self, _, value):
        value = value.strip()
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value.strftime('%Y-%m-%d')

    def stringtodate(self, _, value, format):
        value = value.strip()
        value = datetime.strptime(value.strip(), format)
        return value.strftime('%Y-%m-%d')

    def stringtodatetime(self, _, value, format):
        value = value.strip()
        value = datetime.strptime(value.strip(), format)
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def xattrvalue(self, _, name):
        name = name.strip().lower()
        prop = \
            self.context.property_manager.get_property(
                self.process,
                'http://www.opengroupware.us/oie',
                'xattr_{0}'.format(name))
        if prop:
            return unicode(prop.get_value())
        return u''

    def getpid(self, _):
        return unicode(self.process.object_id)

    def getuuid(self, _):
        return unicode(self.process.uuid)

    def getguid(self, _):
        return unicode(self.process.uuid[1:-1])

    def generateguid(self, _):
        return unicode(uuid.uuid4())

    def generatehexguid(self, _):
        return unicode(uuid.uuid4().hex)

    def month(self, _, value):
        value = datetime.strptime(value.strip(), '%Y-%m-%d')
        return unicode(value.month)

    def year(self, _, value):
        value = datetime.strptime(value.strip(), '%Y-%m-%d')
        return unicode(value.year)

    def monthstart(self, _, year, month):

        try:
            year = int(year)
        except:
            raise CoilsException(
                'Non-numeric year provided to oie:monthstart')

        try:
            month = int(month)
        except:
            raise CoilsException(
                'Non-numeric month provided to oie:monthstart')

        return date(year=year, month=month, day=1, ).strftime('%Y-%m-%d')

    def monthend(self, _, year, month):
        day = calendar.monthrange(year, month)[1]
        return date(year=year, month=month, day=day, ).strftime('%Y-%m-%d')

    def today(self, _, ):
        return date.today().strftime('%Y-%m-%d')

    def dateplusdays(self, _, start, delta):
        start = datetime.strptime(start.strip(), '%Y-%m-%d')
        result = start + timedelta(days=int(delta))
        return result.strftime('%Y-%m-%d')

    def yesterday(self, _):
        return (date.today() + timedelta(days=-1)).strftime('%Y-%m-%d')

    def tomorrow(self, _):
        return (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    def days(self, _, start, end):
        start = self._make_date(start, 'days', 'start')
        end = self._make_date(end, 'days', 'end')
        return (end - start).days

    def weekdays(self, _, start, end):
        start = self._make_date(start, 'weekdays', 'start')
        end = self._make_date(end, 'weekdays', 'end')
        rule = rrule(DAILY,
                     byweekday=(MO, TU, WE, TH, FR, ),
                     dtstart=start,
                     until=end, )
        return unicode(rule.count())

    def replace(self, _, value, text1, text2):
        if isinstance(value, list):
            if not value:
                return ''
            value = value[0]
        return value.replace(text1, text2)

    def truncate(self, _, value, length, ):
        if isinstance(value, list):
            if not value:
                return ''
            value = value[0]
        length = int(length)
        return value[:length].strip()

    def localizedatetime(self, _, value, *tzstrings):

        if isinstance(value, list):
            if not value:
                raise CoilsException('No value provided for localizedatetime')
            value = value[0]
        if not isinstance(value, basestring):
            raise CoilsException(
                'Value provided for localizedatetime is of type "{0}", '
                'must be basestring'
                .format(type(value), )
            )

        self.context.log.debug(
            'Invoking oie:localizedatetime({0}, {1})'.format(value, tzstrings,)
        )

        if len(tzstrings) == 0:
            input_tz = gettz('UTC')
            output_tz = gettz('UTC')
        elif len(tzstrings) == 1:
            input_tz = gettz('UTC')
            output_tz = gettz(tzstrings[0])
        elif len(tzstrings) == 2:
            input_tz = gettz(tzstrings[0])
            output_tz = gettz(tzstrings[1])

        value = StandardXML.Create_Date_Value(value)  # from string to datetime
        value = value.replace(tzinfo=input_tz)  # localize datetime to in TZ
        value = value.astimezone(output_tz)  # translate datetime to out TZ
        return StandardXML.Format_Date_Value(value)  # Datetime back to string

    def round(self, _, value, sigs):
        return unicode(round(float(value), int(sigs)))

    def newline(self, _, value, text1, mode):

        escape_toggle = False
        if len(mode) == 2:
            escape_toggle = True if mode[1] == 'e' else False
        mode = mode[0]

        if isinstance(value, list):
            if not value:
                return ''
            value = value[0]

        if mode == 'n':
            umulat = '\n'
        elif mode == 'd':
            umulat = '\r\n'
        elif mode == 'r':
            umulat = '\r'
        elif mode == 'h':
            umulat = '<br/>'

        if escape_toggle:
            value = escape(value)

        return value.replace(text1, umulat)

    def getblobpath(self, _, target):
        """
        Return a full literal file-system path to the underlying BLOB
        content; this does not skip access permissions or workflow scope as
        the object is still openened via Logic - then the path is returned.
        This is a HACK - and usage should be generally avoided - but currently
        for purposes of RML and like operations the underlying file path is
        required.

        Support input values are an objectId [assumed if the value is numeric],
        "ogo://" URIs and "oie://{message}" in order to directly reference
        the value of a workflow message.
        """

        blob_object = None

        if target.isdigit():
            blob_object = self.context.run_command(
                'document::get', id=int(target),
            )
        elif target.startswith('ogo://'):
            blob_object = walk_ogo_uri_to_target(self.context, target, )
        elif target.startswith('oie://'):
            # implement loading message full path
            label = target[6:]
            blob_object = self.context.run_command(
                'message::get',
                process=self.process,
                scope=self.scope,
                label=label,
            )

        if blob_object is None:
            raise CoilsException(
                'Failed to marshall BLOB referenced by target "{0}"'
                .format(target)
            )

        blob_handle = None

        if isinstance(blob_object, Document):
            blob_handle = self.context.run_command(
                'document::get-handle', document=blob_object,
            )
        elif isinstance(blob_object, Message):
            blob_handle = self.context.run_command(
                'message::get-handle', message=blob_object,
            )
        else:
            raise CoilsException(
                'BLOB object marshalled {0} is of unexpected type'
                .format(blob_object, )
            )

        if blob_object is None:
            raise CoilsException(
                'Failed to create handle for BLOB object {0}'
                .format(blob_object, )
            )

        result = blob_handle.name

        BLOBManager.Close(blob_handle)
        blob_handle = None
        blob_object = None

        return result
