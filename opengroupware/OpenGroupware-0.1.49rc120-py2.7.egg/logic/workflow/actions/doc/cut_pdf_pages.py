#
# Copyright (c) 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
import signal
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from coils.foundation.api.pypdf2 import PdfFileReader, PdfFileWriter


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class BurstingTimeOutException(Exception):
    pass


class CutPagesFromPDFAction(ActionCommand):
    __domain__ = 'action'
    __operation__ = 'cut-pages-from-pdf'
    __aliases__ = ['cutPagesFromPDF', 'cutPagesFromPDFAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/pdf'

    def _calculate_start_and_end_range(self, page_count):

        # NEGATIVE PAGE START
        if self._start_page < 0:
            """
            start page is negative, meaning we work backwords from last page.
            remember math class - adding a negative number to a positive
            number is effectively subtraction.
            """
            self._start_page = page_count + self._start_page
            if self._start_page < 0:
                self._start_page = 1
                self.log_message(
                    'First page of page selection range is negative, '
                    'defaulting to first page of the document',
                    category='info',
                )
        else:
            # back off start to make a true selection range
            self._start_page -= 1

        # NEGATIVE PAGE END
        if self._end_page < 0:
            self._end_page = page_count + self._end_page
            if self._end_page < 0:
                self._end_page = 1
                self.log_message(
                    'End page of page selection range is negative, '
                    'defaulting to first page of the document',
                    category='info',
                )
        # ZERO PAGE END
        elif self._end_page == 0:
            self._end_page = page_count
            self.log_message(
                'End page of page selection range is zero, so last page '
                'defaulted to {0}, the last page of the document.'
                .format(page_count, ),
                category='info'
            )
        # OVERRUN OF PAGE END
        elif self._end_page > page_count:
            self.log_message(
                'End page {0} of page selection range exceeds the number of '
                'pages in the input document ({1} pages); '
                'selecting to end of document'
                .format(self._end_page, page_count, ),
                category='info'
            )
            self._end_page = page_count

        self.log_message(
            'Cutting page range {0} - {1} from source document of {2} pages'
            .format(self._start_page, self._end_page, page_count, ),
            category='info'
        )

        if self._end_page == self._start_page:
            raise CoilsException('Page selection range is zero width')

        if self._end_page < self._start_page:
            raise CoilsException('Page selection invalid, end less than start')

    def do_action(self):

        signal.signal(signal.SIGALRM, timeout_alarm_handler)
        signal.alarm(15)
        reader = PdfFileReader(self.rfile, strict=False, )

        self._calculate_start_and_end_range(page_count=reader.getNumPages())

        writer = PdfFileWriter()
        for page in range(self._start_page, self._end_page):
            try:
                signal.alarm(15)
                writer.addPage(reader.getPage(page))
                signal.alarm(0)
            except TimeOutAlarm:
                raise BurstingTimeOutException
            else:
                writer.write(self.wfile)
        writer = None

    def parse_action_parameters(self):
        self._start_page = int(
            self.process_label_substitutions(
                self.action_parameters.get('startPage', '1'),
            )
        )
        self._end_page = int(
            self.process_label_substitutions(
                self.action_parameters.get('endPage', '0'),
            )
        )

    def do_epilogue(self):
        pass
