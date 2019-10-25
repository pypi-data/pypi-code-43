#
# Copyright (c) 2011, 2012, 2013, 2015, 2018
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
import os
import traceback
from coils.foundation import BLOBManager
from coils.core import MultiProcessWorker, AdministrativeContext

from thumbnail_image import ThumbnailImage
from thumbnail_pdf import ThumbnailPDF
from thumbnail_oasis import ThumbnailOASIS

from events import \
    AUTOTHUMB_NAIL_REQUEST, \
    AUTOTHUMB_NAIL_CREATED, \
    AUTOTHUMB_NAIL_FAILED, \
    AUTOTHUMB_NAIL_EXPUNGE

from edition import AUTOTHUMBNAILER_VERSION

THUMBERS = {
    'image/jpeg': ThumbnailImage,
    'image/png': ThumbnailImage,
    'application/pdf': ThumbnailPDF,
    'image/gif': ThumbnailImage,
    'image/tiff': ThumbnailImage,
    'image/bmp': ThumbnailImage,
    'application/vnd.oasis.opendocument.database': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.chart': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.formula': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.graphics': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.image': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.text-master': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.presentation': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.spreadsheet': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.text': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.graphics-template': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.text-web': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.presentation-template': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.spreadsheet-template': ThumbnailOASIS,
    'application/vnd.oasis.opendocument.text-template': ThumbnailOASIS,
}


class ThumbWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, silent=True):
        MultiProcessWorker.__init__(
            self,
            name=name,
            work_queue=work_queue,
            event_queue=event_queue,
            silent=silent,
        )
        self.context = AdministrativeContext(
            {},
            component_name=name,
        )

    def process_worker_message(self, command, payload, ):
        if command in (
            AUTOTHUMB_NAIL_REQUEST, AUTOTHUMB_NAIL_EXPUNGE,
        ):
            try:
                object_id = long(payload)
            except Exception as e:
                self.log.exception(e)
                self.log.error(
                    'Unable to convert payload "{0}" to objectId'.
                    format(payload, )
                )
                return

            if command == AUTOTHUMB_NAIL_REQUEST:
                self.thumbnail_document(object_id)
            elif command == AUTOTHUMB_NAIL_EXPUNGE:
                # TODO: implement thumbnail expunge
                pass
        self.context.db_close()

    def thumbail_expunge(self, object_id):
        """
        Expunge the thumbnails for the specified document, the document
        in question has probably been deleted.
        """
        # WARN: duplicated code for filepath creation
        filename = '{0}.*.thumb'.format(object_id, )
        filepath = 'cache/thumbnails/{0}/{1}/{2}'.format(
            filename[1:2],
            filename[2:3],
            filename,
        )
        self.log.debug(
            'Deleting thumbails of OGo#{0} [Document], glob is "{1}"'
            .format(object_id, filepath, )
        )
        for filename in BLOBManager.GlobFiles(filepath):
            try:
                os.remove(filename)
            except:
                self.log.warn('Failed to remove thumbnail "{0}"'.format(
                    filename,
                ))
            else:
                self.log.debug('Removed thumbnail "{0}"'.format(
                    filename,
                ))

    def thumbnail_document(self, object_id):
        """
        Create a new thumbnail for the current version of the document
        """

        document = self.context.run_command(
            'document::get',
            id=object_id,
        )
        if not document:
            self.log.debug(
                'Unable to marshall OGo#{0} [Document] for thumbnailing'.
                format(object_id, )
            )
            return
        self.log.debug(
            'Autothumb service attempting to thumbnail OGo#{0} [Document]'.
            format(object_id, )
        )

        # WARN: duplicated code for filepath creation
        filename = (
            '{0}.{1}.{2}.thumb'.
            format(
                document.object_id,
                AUTOTHUMBNAILER_VERSION,
                document.version,
            )
        )
        filename = (
            'cache/thumbnails/{0}/{1}/{2}'.
            format(
                filename[1:2],
                filename[2:3],
                filename,
            )
        )

        # TODO: If the current thumbnail exists, do not recaclulate

        mimetype = self.context.type_manager.get_mimetype(document)
        thumber = THUMBERS.get(mimetype, None)
        if thumber:
            thumber = thumber(
                self.context,
                mimetype,
                document,
                filename,
            )

            thumbnail_created = False

            try:
                thumbnail_created = thumber.create()
            except Exception as exc:
                self.log.debug(
                    'Thumbnail creation failed with exception for '
                    'OGo#{0} [Document] of type "{1}"'
                    .format(object_id, mimetype, )
                )
                self.log.exception(exc)
                self.context.rollback()
                self.enqueue_event(
                    AUTOTHUMB_NAIL_FAILED,
                    (
                        object_id,
                        'Document',
                        traceback.format_exc(),
                    ),
                )
            else:
                """
                we need to commit in order to get any audit entries or
                object properties created by the thumbing event.
                """
                self.context.commit()

                if not thumbnail_created:
                    self.enqueue_event(
                        AUTOTHUMB_NAIL_FAILED,
                        (
                            object_id,
                            'Document',
                            'unknown, no exception, see log file',
                        ),
                    )
                    self.log.debug(
                        'Thumbnail creation failed for OGo#{0} [Document] of '
                        'type "{1}"'.format(object_id, mimetype, )
                    )
                    return

                self.log.debug(
                    'Thumbnail created for OGo#{0} [Document] of '
                    'type "{1}"'.format(object_id, mimetype, )
                )
                self.enqueue_event(
                    AUTOTHUMB_NAIL_CREATED, (object_id, ),
                )
            finally:
                thumber = None
