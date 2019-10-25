#
# Copyright (c) 2018
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
import zipfile
import shutil
from coils.foundation import BLOBManager
from coils.net import get_streams_from_smtp_message
from .command import MailAction


class StreamsFromMessagesAction(MailAction):
    __domain__ = "action"
    __operation__ = "streams-from-mail-messages"
    __aliases__ = ['streamsFromMailMessages', 'streamsFromMailMessagesAction', ]  # noqa

    def __init__(self):
        MailAction.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/zip'

    def do_action(self):

        def clean_up_message_id(message_id):
            return message_id.replace('<', '').replace('>', '')

        zfile = zipfile.ZipFile(
            self.wfile, 'w', compression=zipfile.ZIP_DEFLATED,
        )

        stored_streams = 0
        scanned_messages = 0

        # process messages from ZIP archive
        for handle, object_name, in self._yield_input_handles_and_name():

            try:
                # read archive content object as Mail Message
                message = self._get_message_from_input(handle)
            except Exception as exc:
                self.log_message(
                    'Unable to parse message from object named "{0}".'
                    .format(object_name, ),
                    category='debug',
                )
                self.log_exception(exc)
                continue

            # loop through interesing MIME types
            for mimetype in self._mimetypes_to_collect:
                # get streams of type X from message
                message_id, streams, rejects, = get_streams_from_smtp_message(
                    message, mimetype, self._ctx.log, with_types=True,
                )

                # loop through streams
                if not streams:
                    continue
                for filename in streams.keys():
                    if streams[filename][1].startswith('multipart/'):
                        continue
                    webdav_name = streams[filename][2]
                    if webdav_name is None:
                        webdav_name = filename
                    sfile_name = '{0}.{1}'.format(
                        clean_up_message_id(message_id),
                        webdav_name,
                    )
                    """
                    WARN: it takes a lot of work to get this to work
                    reliablely, it is easy to end up with truncated streams.
                    """
                    streams[filename][0].flush()
                    streams[filename][0].seek(0, 2)  # seek to end
                    stream_size = streams[filename][0].tell()  # get size
                    streams[filename][0].seek(0, 0)  # rewind
                    zfile.write(streams[filename][0].name, arcname=sfile_name, )
                    self.log_message(
                        'Stored attachment "{0}" from message "{1}" as "{2}"; '
                        'size={3}'.format(
                            webdav_name, message_id, sfile_name, stream_size,
                        ),
                        category='debug',
                    )
                    stored_streams += 1

            scanned_messages += 1

            self.gong()

        self.log_message(
            'stored {0} streams from {1} messages'
            .format(stored_streams, scanned_messages, )
        )

        zfile.close()

    def parse_action_parameters(self):

        tmp = self.action_parameters.get('mimetypes', 'application/pdf', )
        self._mimetypes_to_collect = [x.strip() for x in tmp.split(',')]
