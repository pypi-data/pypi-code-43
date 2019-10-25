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
import logging

from coils.core import walk_ogo_uri_to_folder

from utility import expand_labels_in_name

from events import \
    DOCUMENT_AUTOMOVE_COMPLETED, \
    DOCUMENT_AUTOMOVE_FAILED, \
    DOCUMENT_AUTOMOVE_DISCARDED


class DocumentAutoMove(object):

    def __init__(self, ctx, document, version, propmap, ):
        self.context = ctx
        self.document = document
        self.version = version
        self.propmap = propmap
        self.log = logging.getLogger(
            'coils.blob.automove.{0}'
            .format(document.object_id, )
        )

    def resolve_path(self, target_path):

        target_path = expand_labels_in_name(
            text=target_path,
            context=self.context,
            document=self.document,
            propmap=self.propmap,
        )
        self.log.debug(
            'expanded path for auto-move is "{0}"'
            .format(target_path, )
        )
        folder, arguments, = None, None,
        try:
            folder, arguments, = \
                walk_ogo_uri_to_folder(
                    context=self.context,
                    uri=target_path,
                    create_path=True,
                    default_params={'deleteafterfiling': 'NO', },
                    default_project=self.document.project,
                )
        except Exception as exc:
            self.log.error(
                'Exception walking path from OGo URI "{0}"'
                .format(target_path, )
            )
            self.log.exception(exc)
            return None

        return folder

    def move_to(self, folder):

        if self.document.folder.object_id == folder.object_id:
            return DOCUMENT_AUTOMOVE_DISCARDED
        else:
            if self.document.file_size < 1:
                return DOCUMENT_AUTOMOVE_DISCARDED

            document = self.context.run_command(
                'document::move',
                document=self.document,
                to_folder=folder,
            )
            if not document:
                return DOCUMENT_AUTOMOVE_FAILED

        return DOCUMENT_AUTOMOVE_COMPLETED
