#
# Copyright (c) 2017
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
import requests
from coils.core import CoilsException
from coils.core.logic import ActionCommand


class HttpPutAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "http-put"
    __aliases__ = ['httpPut', 'httpPutAction', ]

    def __init__(self):
        ActionCommand.__init__(self)
        self._result_mimetype = 'application/octet-stream'

    @property
    def result_mimetype(self):
        return self._result_mimetype

    def do_action(self):

        self.log_message(
            'http PUT operation URL="{0}" sending mimetype="{1}" size={2}'
            .format(
                self._put_url,
                self.input_message.mimetype,
                self.input_message.size,
            ),
            category='info',
        )

        request = requests.put(
            self._put_url,
            headers={
                'Content-Type': self.input_message.mimetype,
                'Content-Length': str(self.input_message.size),
                'X-OpenGroupware-Process-Id': str(self.pid),
            },
            data=self.rfile,
            allow_redirects=True,
            stream=True,
        )
        status_code = request.status_code
        self.log_message(
            'http status code for request was {0}'.format(status_code, )
            .format(status_code, ),
            category='info',
        )
        """
        200: OK
        201: Created
        202: Accepted
        203: Non-authoritative [even seen in the wild?]
        204: No content
        Perhaps 205 (Reset) or 206 (Partial) are valid?  but again, are they
        ever seen in the wild?
        We are assuming 207 (multi-status) and 208 (already reported) are
        considered abnormal responses to BLOB PUT requests
        """
        if status_code not in (200, 201, 202, 203, 204, ):
            request.raise_for_status()

        """log all the response headers"""
        for key, value in request.headers.items():
            self.log_message(
                'http header "{0}" = "{1}"'
                .format(key, value, ),
                category='debug',
            )

        """determine the mime type of result"""
        if 'content-type' in request.headers:
            mimetype = request.headers['content-type']
            self._result_mimetype = mimetype.split(';')[0].strip()
            self.log_message(
                'content type of message will be: "{0}"'
                .format(mimetype, ),
                category='info',
            )

        """store the payload"""
        for chunk in request.iter_content(chunk_size=4096):
            self.wfile.write(chunk)

        request.close()

    def parse_action_parameters(self):
        self._put_url = self.process_label_substitutions(
            self.action_parameters.get('URL', None)
        )
        if not self._put_url:
            raise CoilsException('httpPutAction with no URL specified')

    def do_epilogue(self):
        pass
