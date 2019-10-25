#
# Copyright (c) 2013, 2015
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
import traceback
import shutil
import signal
from coils.core import BLOBManager
from subprocess import Popen, PIPE

CONVERSION_TIMEOUT_SECONDS = 15


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class ThumbnailPDF(object):

    def __init__(self, ctx, mimetype, entity, path):
        self.mimetype = mimetype
        self.context = ctx
        self.entity = entity
        self.pathname = path

    def create(self):

        rfile = self.context.run_command(
            'document::get-handle', document=self.entity,
        )
        if not rfile:
            return False

        converter = None
        converter_result = False
        sfile = BLOBManager.ScratchFile()
        efile = BLOBManager.ScratchFile()

        try:
            signal.signal(signal.SIGALRM, timeout_alarm_handler)
            signal.alarm(CONVERSION_TIMEOUT_SECONDS)

            # convert -format pdf -[0] -thumbnail 175x -bordercolor white png:-

            converter = Popen(
                [
                    '/usr/bin/convert', '-format', 'pdf', '-[0]',
                    '-thumbnail', '175x', '-bordercolor', 'white', 'png:-',
                ],
                stdin=PIPE,
                stdout=sfile,
                stderr=efile,
            )

            shutil.copyfileobj(rfile, converter.stdin)
            converter.stdin.close()
            converter.communicate()
            signal.alarm(0)
        except TimeOutAlarm:
            self.context.log.debug(
                'PDF Thumbnail generation timeout for OGo#{0} [Document]'
                .format(self.entity.object_id, )
            )
            self.context.audit_at_commit(
                object_id=self.entity.object_id,
                action='notification',
                message='Converter for PDF thumbnail creation timed-out',
                version=self.entity.version,
            )
        except Exception as exc:
            self.context.log.error(
                'Unexpected exception occurred in PDF thumbnail '
                'generation for OGo#{0} [Document]'
                .format(self.entity.object_id, )
            )
            self.context.log.exception(exc)
        else:
            """
            Success?
            """
            if converter.returncode == 0:
                self.context.log.debug(
                    'converter completed with exit code 0 '
                    'for OGo#{0} [Document]'
                    .format(self.entity.object_id, )
                )
                sfile.flush()
                sfile.seek(0)
                wfile = BLOBManager.Open(
                    self.pathname, mode='w', encoding='binary', create=True,
                )
                shutil.copyfileobj(sfile, wfile)
                BLOBManager.Close(wfile)
                converter_result = True
            else:
                self.context.log.debug(
                    'converter completed with exit code {0} '
                    'for OGo#{1} [Document]'
                    .format(converter.returncode, self.entity.object_id, )
                )

            efile.seek(0, 2)  # seek end of file
            if efile.tell():
                # there is text in the standard-error stream
                efile.seek(0)
                error_text = efile.read(65535)
                self.context.log.info(
                    'recording {0}b of stderr content from convert for '
                    'OGo#{1} [Document] to audit log'
                    .format(
                        len(error_text),
                        self.entity.object_id,
                    )
                )
                # standard out may not be nice UTF-8
                error_text = error_text.decode('utf8', 'ignore')
                self.context.audit_at_commit(
                    object_id=self.entity.object_id,
                    action='notification',
                    message=(
                        'Standard error output from PDF thumbnail creation: '
                        '{0}'.format(error_text, )
                    ),
                    version=self.entity.version,
                )
                self.context.log.info('stderr content queued for commit')
            else:
                self.context.log.debug(
                    'no stderr content from convert for OGo#{0} [Document]'
                    .format(self.entity.object_id, )
                )

        finally:
            """
            Stop the alarm clock, close the thumbnail stream, ensure the
            converter process is terminated, and finally record any standard-
            error content to the audit log of the source document.
            """

            signal.alarm(0)

            BLOBManager.Close(sfile)
            BLOBManager.Close(efile)

            if converter.returncode is None:
                # we are in the finally but the converter is not completed
                self.context.log.debug(
                    'attempting to terminate incomplete convert '
                    'for PDF thumbnail of OGo#{0}'
                    .format(self.entity.object_id, )
                )
                try:
                    converter.terminate()
                except Exception as exc:
                    self.context.log.error(
                        'Unable to terminate incomplete convert process '
                        'for OGo#{0}'
                        .format(self.entity.object_id, )
                    )
                    self.log.exception(exc)
                    self.context.audit_at_commit(
                        object_id=self.entity.object_id,
                        action='notification',
                        message=(
                            'Unable to terminate incomplete convert '
                            'for thumbnail creation:\n{0}'
                            .format(traceback.format_exc(), )
                        ),
                        version=self.entity.version,
                    )
                else:
                    self.context.log.debug(
                        'Incomplete convert for PDF thumbnail of '
                        'OGo#{0} terminated'
                        .format(self.entity.object_id, )
                    )
                    self.context.audit_at_commit(
                        object_id=self.entity.object_id,
                        action='notification',
                        message=(
                            'Incomplete convert for PDF thumbnail '
                            'creation terminated'
                        ),
                        version=self.entity.version,
                    )

        return converter_result
