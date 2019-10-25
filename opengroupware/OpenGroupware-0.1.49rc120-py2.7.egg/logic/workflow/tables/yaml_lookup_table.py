#
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
#
import logging
import yaml
from coils.core import walk_ogo_uri_to_target
from coils.foundation import BLOBManager
from coils.core import CoilsException, Document
from table import Table


class YAMLLookupTable(Table):

    def __init__(self, context=None, process=None, scope=None, ):
        """
        ctor

        :param context: Security and operation context for message lookup
        :param process: Proccess to use when resolving message lookup
        :param scope: Scope to use when resolving message lookup
        """

        Table.__init__(self, context=context, process=process, scope=scope, )

        self._yamldoc = None  # The YAML document

        # Lookup table references a workflow message in description
        self._message_label = None  #

        # Lookup table references a project document in description
        self._document_path = None

        # Initialize attributes
        self._rfile = None
        self._root_key = None
        self._do_input_upper = False
        self._do_input_strip = False
        self._do_output_upper = False
        self._do_output_strip = False
        self.log = logging.getLogger('OIE.YAMLLookupTable')

    def __repr__(self):
        return '<YAMLLookupTable name="{0}" />'.format(self.name, )

    def _load_message(self):

        if not self._rfile:
            message = self.context.run_command(
                'message::get',
                process=self._process,
                scope=self._scope,
                label=self._message_label,
            )
            if message:
                self.log.debug(
                    'Retrieved message labelled "{0}" in scope "{1}"'.
                    format(self._label, self._label, )
                )
                rfile = self.context.run_command(
                    'message::get-handle', message=message,
                )
                self.log.debug(
                    'Opened handle for message text"'.
                    format(self._label, self._label, ))
                self._rfile = rfile
            else:
                raise CoilsException(
                    'No message labelled "{0}" found in scope "{0}" of '
                    'OGo#{2} [Process]'.
                    format(
                        self._label,
                        self._scope,
                        self._process.object_id,
                    )
                )

        self._yamldoc = yaml.load(self._rfile)
        self.log.debug('Content of message parsed')

    def _load_document(self):

        document = walk_ogo_uri_to_target(self.context, self._document_path, )
        if isinstance(document, Document):
            self._rfile = self.context.run_command(
                'document::get-handle',
                document=document,
            )
        else:
            raise CoilsException(
                'Unable to marshall document at path "{0}"'
                .format(self._document_path, )
            )
        self._yamldoc = yaml.load(self._rfile)
        self.log.debug('Content of message parsed')

    def _load_content(self):
        '''
        Load the content, possibly already loaded. If yaml content is not
        initialized load it from either the workflow message or the document
        '''
        if self._yamldoc:
            return
        elif self._message_label:
            return self._load_message()
        elif self._document_path:
            return self._load_document()
        raise CoilsException('No content defined for YAML lookup')

    def _fallback_return(self, *values):
        '''
        No value was resolved from the lookup so we exercise the fallback
        options of either a chained table or a default value
        '''
        if self._chained_table:
            return self._chained_table.lookup_value(*values)
        elif self._default_value is not None:
            return self._default_value
        return None

    def _stringify_result(self, result):
        self.log.info('YAMLLookupTable result: "{0}"'.format(result, ))
        if isinstance(result, list):
            result = ','.join([unicode(x) for x in result])
        return result

    def set_rfile(self, rfile):
        """
        Directly set the rfile attribute.

        :param rfile: Provides the table with a file handle to read the
            document, this is used for testing (otherwise the table cannot
            execute outside of a process instance).
        """
        self._rfile = rfile

    def set_description(self, description):
        """
        Load description of the table

        :param description: A dict describing the table
        """

        self.c = description
        self._name = self.c.get('name', None)

        self._default_value = self.c.get('defaultValue', None)
        if self.c.get('chainedTable', None):
            self._chained_table = Table.Load(self.c['chainedTable'])
        else:
            self._chained_table = None

        self._root_key = self.c.get('rootKey', None)

        if 'messageLabel' in self.c:
            self._message_label = self.c.get('messageLabel')
        elif 'documentPath' in self.c:
            self._document_path = self.c.get('documentPath')

    def lookup_value(self, *values):
        """
        Perform XPath lookup into referenced document.

        :param values: list of values to load into the XPath
        """

        if not values:
            return None

        self.log.debug(
            'YAML lookup requested via table "{0}" with values: {1}'.
            format(self.name, values, )
        )

        self._load_content()

        if self._root_key is None:
            result = self._yamldoc
        else:
            try:
                result = self._yamldoc[self._root_key]
            except KeyError:
                raise CoilsException(
                    'Expected key "{0}" does not exist at root of YAML data'
                    .format(self._root_key, )
                )

        try:
            for value in values:
                try:
                    result = result[value]
                except KeyError as exc:
                    if isinstance(value, basestring):
                        if value.isdigit():
                            result = result[long(value)]
                        else:
                            raise exc
                    elif isinstance(value, int):
                        result = result[unicode(value)]
                    else:
                        raise exc
                if result is None:
                    break
        except KeyError:
            result = None

        if not result:
            self.log.debug(
                'YAML lookup evaluated to None, '
                'returning values from fallback [if any]'
            )
            return self._fallback_return(*values)

        return self._stringify_result(result)

    def shutdown(self):
        """
        Tear down any externally referenced resources
        """

        if self._rfile:
            BLOBManager.Close(self._rfile)
        Table.shutdown(self)
