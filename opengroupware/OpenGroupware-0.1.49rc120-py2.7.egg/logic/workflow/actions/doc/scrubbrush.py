
#
# Copyright (c) 2016, 2019
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
import os
import signal
import shutil
import traceback
from coils.core import BLOBManager, CoilsException
from subprocess import Popen, PIPE

CONVERSION_TIMEOUT_SECONDS = 5


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class ScrubBrush(object):

    def __init__(self, action):
        self.action = action
        self.context = action._ctx

        self._cairo_path = self.context.server_defaults_manager.string_for_default(  # noqa
            'PDFToCairoPath', value='/usr/bin/pdftocairo',
        )
        if not os.path.exists(self._cairo_path):
            self.action.log_message(
                'Scrub-brush disabled - PDFToCairoPath "{0}" does not exist'
                .format(self._cairo_path, ),
                category='info',
            )
            self._brush_status = False
        else:
            self.action.log_message(
                'Scrub-brush enabled - PDFToCairoPath "{0}" found'
                .format(self._cairo_path, ),
                category='info',
            )
            self._brush_status = True

    def close(self):
        self.disable()

    @property
    def is_enabled(self):
        return self._brush_status

    @property
    def is_disabled(self):
        return not self._brush_status

    def enable(self):
        if os.path.exists(self._cairo_path):
            self._brush_status = True
        else:
            self.action.log_message(
                'Scrub-brush disabled - PDFToCairoPath "{0}" does not exist'
                .format(self._cairo_path, ),
                category='info',
            )
            self._brush_status = False
        return self._brush_status

    def disable(self):
        if self._brush_status:
            self.action.log_message(
                'Scrub-brush programatically disabled',
                category='info',
            )
            self._brush_status = False
        return self._brush_status

    def scrub_stream(self, rfile):

        if self.is_disabled:
            return rfile

        converter = None
        converter_result = False
        sfile = BLOBManager.ScratchFile(require_named_file=True, )
        efile = BLOBManager.ScratchFile()

        converter = Popen(
            [
                self._cairo_path, '-pdf', '-origpagesizes', '-', '-'
            ],
            stdin=PIPE,
            stdout=sfile,
            stderr=efile,
        )
        try:
            signal.signal(signal.SIGALRM, timeout_alarm_handler)
            signal.alarm(CONVERSION_TIMEOUT_SECONDS)
            shutil.copyfileobj(rfile, converter.stdin)
            converter.stdin.close()
            converter.communicate()
            signal.alarm(0)
        except TimeOutAlarm:
            self.action.log_message(
                'Scrubbing timeout, stream not scrubbed',
                category='warn',
            )
            converter_result = False
        except Exception:
            self.action.log_message(
                'Scrubbing of stream failed with exception.:\n{0}'
                .format(traceback.format_exc(), ),
                category='warn',
            )
            converter_result = False
        else:
            converter_result = True
            self.action.log_message(
                'Scrubbing of stream completed',
                category='debug',
            )
        finally:
            """
            Stop the alarm clock, close the  stream, ensure the
            converter process is terminated, and finally record any standard-
            error content to the audit log of the source document.
            """

            signal.alarm(0)
            BLOBManager.Close(efile)
            if converter.returncode is None:
                # we are in the finally but the converter is not completed
                self.action.log_message(
                    'scrubbing of stream incomplete',
                    category='error',
                )
                try:
                    converter.terminate()
                except Exception:
                    self.action.log_message(
                        'Unable to terminate incomplete scrub process:\n{0}'
                        .format(
                            traceback.format_exc(),
                        ),
                        category='error',
                    )

        if converter_result:
            BLOBManager.Close(rfile)
            sfile.seek(0)
            return sfile

        rfile.seek(0)
        return rfile

    def scrub(self, document):

        rfile = self.context.run_command(
            'document::get-handle', document=document,
        )
        if not rfile:
            raise CoilsException(
                'Unable to marshall a handle for OGo#{0} [Document]'
                .format(document.object_id, )
            )

        if self.is_disabled:
            self.action.log_message('Scrub-brush disabled', category='info', )
            return rfile

        mimetype = self.context.type_manager.get_mimetype(document)
        if mimetype not in ('application/pdf', ):
            self.action.log_message(
                'Scrub-brush does not handle type "{0}", '
                'no scrubbing performed'.format(mimetype, ),
                category='info',
            )
            return rfile

        """
        Attempt to create a scrubbed PDF
        """
        converter = None
        converter_result = False
        sfile = BLOBManager.ScratchFile(require_named_file=True, )
        efile = BLOBManager.ScratchFile()

        converter = Popen(
            [
                self._cairo_path, '-pdf', '-origpagesizes', '-', '-'
            ],
            stdin=PIPE,
            stdout=sfile,
            stderr=efile,
        )
        try:
            signal.signal(signal.SIGALRM, timeout_alarm_handler)
            signal.alarm(CONVERSION_TIMEOUT_SECONDS)
            shutil.copyfileobj(rfile, converter.stdin)
            converter.stdin.close()
            converter.communicate()
            signal.alarm(0)
        except TimeOutAlarm:
            self.action.log_message(
                'Scrub timeout for OGo#{0} [Document], document not scrubbed'
                .format(document.object_id, ),
                category='warn',
            )
            converter_result = False
        except Exception:
            self.action.log_message(
                'Scrubbing of document OGo#{0} failed with exception.:\n{1}'
                .format(document.object_id, traceback.format_exc(), ),
                category='warn',
            )
            converter_result = False
        else:
            converter_result = True
            self.action.log_message(
                'Scrubbing of document OGo#{0} completed'
                .format(document.object_id, ),
                category='debug',
            )
        finally:
            """
            Stop the alarm clock, close the  stream, ensure the
            converter process is terminated, and finally record any standard-
            error content to the audit log of the source document.
            """

            signal.alarm(0)
            BLOBManager.Close(efile)
            if converter.returncode is None:
                # we are in the finally but the converter is not completed
                self.action.log_message(
                    'scrubbing incomplete for document OGo#{0}'
                    .format(document.object_id, ),
                    category='error',
                )
                try:
                    converter.terminate()
                except Exception:
                    self.action.log_message(
                        'Unable to terminate incomplete convert process '
                        'for OGo#{0}:\n{1}'.format(
                            document.object_id,
                            traceback.format_exc(),
                        ),
                        category='error',
                    )

        if converter_result:
            BLOBManager.Close(rfile)
            sfile.seek(0)
            return sfile

        rfile.seek(0)
        return rfile
