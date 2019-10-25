#
# Copyright (c) 2014, 2015
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
import time
import traceback
from coils.core import BLOBManager, NoSuchPathException
from coils.net import PathObject, json_encode
from coils.logic.workflow import Format


class FormatObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.format_entity = None  # Overriden by params if this is a format
        PathObject.__init__(self, parent, **params)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        format_ = self.context.run_command('format::get', name=name, )
        if format_:
            self.log.debug(
                'Marshalled format "{0}" via attachfs.'
                .format(name, )
            )
            return FormatObject(
                self, name,
                format_entity=format_,
                parameters=self.parameters,
                request=self.request,
                context=self.context,
            )

        raise NoSuchPathException(
            'No child named "{0}" for object {1}'
            .format(name, self, )
        )

    def do_GET(self):

        if not self.format_entity:
            # return a list [JSON] of the defined formats
            names = Format.ListFormats()
            self.request.simple_response(
                200,
                data=json_encode(names),
                mimetype='application/json',
            )
        else:
            # return the markup of the named format
            self.request.simple_response(
                200,
                data=self.format_entity.as_yaml(),
                mimetype='text/plain',
                headers={
                    'ETag': self.format_entity.get_name()
                },
            )

    def do_PUT(self, name):

        mimetype = 'text/plain'
        filename = None

        rfile = BLOBManager.ScratchFile()
        rfile.write(self.request.get_request_payload())
        rfile.seek(0)

        wfile = BLOBManager.ScratchFile()

        error_message = None

        if name == 'read':

            try:
                self.format_entity.process_in(rfile, wfile, )
            except Exception:
                error_message = (
                    'Exception in format read using format "{0}".\n{1}'
                    .format(
                        self.format_entity.get_name(),
                        traceback.format_exc(),
                    )
                )
            else:
                mimetype = 'application/xml'
                filename = 'standard.xml'
                wfile.seek(0)

        elif name == 'write':

            try:
                self.format_entity.process_out(rfile, wfile, )
            except Exception:
                error_message = (
                    'Exception in format write using format "{0}".\n{1}'
                    .format(
                        self.format_entity.get_name(),
                        traceback.format_exc(),
                    )
                )
            else:
                mimetype = self.format_entity.mimetype
                filename = 'output.data'
                wfile.seek(0)

        elif name == 'readwrite':

            interim_file = BLOBManager.ScratchFile()
            try:
                self.format_entity.process_in(rfile, interim_file, )
            except Exception:
                error_message = (
                    'Exception in format read using format "{0}".\n{1}'
                    .format(
                        self.format_entity.get_name(),
                        traceback.format_exc(),
                    )
                )
            else:
                interim_file.seek(0)
                try:
                    self.format_entity.process_out(interim_file, wfile, )
                except Exception:
                    error_message = (
                        'Exception in format write using format "{0}".\n{1}'
                        .format(
                            self.format_entity.get_name(),
                            traceback.format_exc(),
                        )
                    )
                else:
                    mimetype = self.format_entity.mimetype
                    filename = 'convertedOutput.data'
                    wfile.seek(0)
            BLOBManager.Close(interim_file)

        else:

            raise NoSuchPathException(
                'No child named "{0}" for object {1}'
                .format(name, self, )
            )

        if not error_message:
            self.request.stream_response(
                200,
                stream=wfile,
                mimetype=mimetype,
                headers={
                    'Content-Disposition': (
                        'inline; filename={0}'.format(filename, )
                    ),
                    'X-OpenGroupware-Filename': '{0}'.format(filename, ),
                    'etag': '{0}OIE'.format(time.time(), )
                },
            )
        else:
            self.request.simple_response(
                418,
                data=error_message,
                mimetype='text/plain',
            )
