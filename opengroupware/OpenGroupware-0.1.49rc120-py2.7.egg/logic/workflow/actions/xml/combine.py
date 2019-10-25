#
# Copyright (c) 2018
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation import StandardXML
from coils.core.logic import ActionCommand


class StandardXMLCombine(ActionCommand):
    __domain__ = "action"
    __operation__ = "standard-xml-combine"
    __aliases__ = ['standardXMLCombine', 'standardXMLCombineAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _get_handle_for_document_b(self):
        message = self._ctx.run_command(
            'message::get',
            process=self.process,
            label=self._input_label,
        )
        self.log.debug('Merging with message {0}'.format(message.uuid))
        input_handle = self._ctx.run_command(
            'message::get-handle', object=message,
        )
        return input_handle

    @property
    def result_mimetype(self):
        return 'application/xml'

    def do_action(self):

        rfile1 = self.rfile
        rfile2 = self._get_handle_for_document_b()

        """
        Build ResultSet container element
        NOTE: ResultSet attributes come from the primary input document
        """
        table_, format_, class_ = StandardXML.Read_ResultSet_Metadata(rfile1)
        if table_ is None:
            table_ = '_xmlCombine_'
        if format_ is None:
            format_ = ''
        if class_ is None:
            class_ = ''
        self.wfile.write(
            '<ResultSet tableName="{0}" formatName="{1}" className="{2}">'
            .format(table_, format_, class_, )
        )

        counter = 1
        # process rows from primary input message
        for k_, f_, m_ in StandardXML.Read_Rows(rfile1, with_metadata=True):
            StandardXML.Write_Row(self.wfile, k_, f_, m_[2], row_id=counter, )
            counter += 1
            if not (counter % 32768):
                self.gong()  # gong every 32K rows
        # TODO: log number of rows from primary message

        # process rows from secondary message
        for k_, f_, m_ in StandardXML.Read_Rows(rfile2, with_metadata=True):
            StandardXML.Write_Row(self.wfile, k_, f_, m_[2], row_id=counter, )
            counter += 1
            if not (counter % 32768):
                self.gong()  # gong every 32K rows

        # TODO: log number of rows from secondary message

        # close ResultSet container element
        self.wfile.write('</ResultSet>')

        rfile1 = None
        rfile2.close()

    def parse_action_parameters(self):
        self._input_label = self.action_parameters.get('label', None)

    def do_epilogue(self):
        pass
