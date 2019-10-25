#
# Copyright (c) 2016
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
from StringIO import StringIO
from coils.net import LogObject
from workflow import WorkflowPresentation


class ProcessLogObject(LogObject, WorkflowPresentation):

    def __init__(self, parent, name, **params):
        LogObject.__init__(self, parent, name, **params)

    def _load_contents(self):
        if (LogObject._load_contents(self)):
            self._messages = self.get_process_messages(self.entity)
            return True
        return False

    @property
    def messages(self):
        return self._messages

    def write_process_log_table(self, stream):
        log_text = self.context.run_command(
            'process::get-log', pid=self.entity.object_id,
        )
        stream.write('<table width="100%" border="1">\n')
        stream.write(
            '<tr><th bgcolor=black colspan=6><font color=white>'
            'OIE Process Log</font></tf></tr>\n'
        )
        if (len(log_text) > 0):
            stream.write('<tr><td><pre>{0}</pre></td></tr>'.format(log_text))
        else:
            stream.write(
                '<tr><td align="center">'
                'Log component did not respond.'
                '</td></tr>'
            )
        stream.write('</table>\n')

    def write_message_table(self, stream):
        stream.write('<table width="100%" border="1">\n')
        stream.write(
            '<tr><th bgcolor=black colspan=6><font color=white>'
            'Process Messages</font></tf></tr>\n'
        )
        stream.write(
            '<tr><th>UUID</th><th>Label</th><th>Scope</th><th>Version'
            '</th><th>Size</th><th>MIME</th></tr>\n'
        )
        for message in self.messages:
            if (message.scope is None):
                scope = 'n/a'
            else:
                scope = message.scope
            if (message.label is None):
                label = 'n/a'
            else:
                label = message.label
            stream.write(
                '<tr><td align="center"><a href="Messages/{0}">{1}</a></td>'
                '<td align="center">{2}</td>'
                '<td align="center">{3}</td>'
                '<td align="center">{4}</td>'
                '<td align="right">{5}</td>'
                '<td align="center">{6}</td></tr>\n'
                .format(
                    message.uuid[1:-1],
                    message.uuid,
                    label,
                    scope,
                    message.version,
                    message.truesize,
                    message.mimetype,
                )
            )
        stream.write('</table>\n')

    def get_representation(self):
        if (hasattr(self, 'representation')):
            return self.representation
        stream = StringIO(u'')
        self.write_header(stream, refresh_interval=15)
        self.write_audit_table(stream)
        self.write_process_log_table(stream)
        self.write_message_table(stream)
        self.write_footer(stream)
        self.representation = stream.getvalue()
        stream = None
        return self.representation
