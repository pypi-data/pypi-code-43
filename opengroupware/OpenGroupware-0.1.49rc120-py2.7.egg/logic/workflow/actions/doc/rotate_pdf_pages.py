#
# Copyright (c) 2015, 2019
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
from coils.core import BLOBManager
from coils.core.logic import ActionCommand
from coils.foundation.api.pypdf2 import PdfFileReader, PdfFileWriter
from scrubbrush import ScrubBrush


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class PageRotationTimeoutException(Exception):
    pass


class RotatePDFPagesAction(ActionCommand):
    __domain__ = 'action'
    __operation__ = 'rotate-pdf-pages'
    __aliases__ = ['rotatePDFPages', 'rotatePDFPagesAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/pdf'

    def do_action(self):

        scrubbrush = ScrubBrush(self)
        if not self._enable_scrubbrush:
            scrubbrush.disable()
        tfile = scrubbrush.scrub_stream(self.rfile)

        signal.signal(signal.SIGALRM, timeout_alarm_handler)
        signal.alarm(15)

        reader = PdfFileReader(tfile, strict=False, )

        page_files = list()

        """
        Each page is rotated to a unique document, keeping the reference to
        the file in page_files.  The reader is disposed after processing
        each page.  Subsequently each page is composed back into a single file.
        This enables PyPDF to do a much more efficient sweeping of document
        resources - if the rotated pages are composed directly to the target
        document a large amount of redundant information ends up in the target
        file which can be a file orders of magnitude larger than the source
        document.
        """

        for pagenum in range(reader.numPages):
            try:
                signal.alarm(15)
                page = reader.getPage(pagenum)
                if not self._counter_clockwise:
                    page.rotateClockwise(self._rotate_degrees)
                else:
                    page.rotateCounterClockwise(self._rotate_degrees)
                page.compressContentStreams()

                writer = PdfFileWriter()
                writer.addPage(page)
                page_file = BLOBManager.ScratchFile()
                writer.write(page_file)
                page_files.append(page_file)
                del writer
                page = None

                signal.alarm(0)

            except TimeOutAlarm:
                raise PageRotationTimeoutException

        del reader

        writer = PdfFileWriter()  # create writer for composite document
        for page_file in page_files:
            page_file.seek(0)
            reader = PdfFileReader(page_file, strict=False, )
            writer.addPage(reader.getPage(0))
            del reader

        writer.write(self.wfile)
        del writer

        """
        Page file MUST be closed AFTER the writer writes, otherwise you
        will fail with an "I/O operation on closed file" during the writer's
        call to self._sweepIndirectReferences(externalReferenceMap, self._root)
        """
        for page_file in page_files:
            BLOBManager.Close(page_file)

    def parse_action_parameters(self):
        self._counter_clockwise = (
            self.process_label_substitutions(
                self.action_parameters.get('counterClockwise', 'NO'),
            )
        )
        if self._counter_clockwise == 'YES':
            self._counter_clockwise = True
        else:
            self._counter_clockwise = False

        self._rotate_degrees = int(
            self.process_label_substitutions(
                self.action_parameters.get('rotateDegrees', '90'),
            )
        )

        self._enable_scrubbrush = \
            True if self.process_label_substitutions(
                self.action_parameters.get('enableScrubBrush', 'NO')
            ).upper() == 'YES' else False

    def do_epilogue(self):
        pass
