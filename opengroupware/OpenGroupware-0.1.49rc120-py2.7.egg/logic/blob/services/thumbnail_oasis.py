#
# Copyright (c) 2015
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
import shutil
from PIL import Image
import zipfile
from coils.core import BLOBManager, CoilsException

OPEN_DOCUMENT_MIMETYPES = (
    'application/vnd.oasis.opendocument.database',
    'application/vnd.oasis.opendocument.chart ',
    'application/vnd.oasis.opendocument.formula',
    'application/vnd.oasis.opendocument.graphics',
    'application/vnd.oasis.opendocument.image',
    'application/vnd.oasis.opendocument.text-master',
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.oasis.opendocument.graphics-template',
    'application/vnd.oasis.opendocument.text-web',
    'application/vnd.oasis.opendocument.presentation-template',
    'application/vnd.oasis.opendocument.spreadsheet-template',
    'application/vnd.oasis.opendocument.text-template',
)


class ThumbnailOASIS(object):

    def __init__(self, ctx, mimetype, entity, path):
        self.mimetype = mimetype
        self.context = ctx
        self.entity = entity
        self.pathname = path

    def create(self):

        if self.mimetype not in OPEN_DOCUMENT_MIMETYPES:
            raise Exception(
                'Input type for thumbnail is not a supported '
                'OASIS MIME-type'
            )

        rfile = self.context.run_command(
            'document::get-handle', document=self.entity,
        )
        if not rfile:
            return False

        try:
            zfile = zipfile.ZipFile(rfile, 'r', )
        except Exception as exc:
            raise CoilsException(
                'Unable to open OASIS document OGo#{0} as a ZIP archive'
                .format(self.entity.object_id, ),
                inner_exception=exc,
            )

        try:
            zipinfo_to_extract = zfile.getinfo('Thumbnails/thumbnail.png')
        except KeyError as exc:
            zfile.close()
            raise CoilsException(
                'Zip file does not contain expected thumbnail',
                inner_exception=exc,
            )

        zhandle = zfile.open(zipinfo_to_extract, 'r')

        scratch = BLOBManager.ScratchFile()
        shutil.copyfileobj(zhandle, scratch)
        scratch.seek(0)

        zhandle.close()  # Close OASIS thumbnail
        zfile.close()  # Close ZIP archive

        self.image = Image.open(scratch)
        self.image.thumbnail((175, 175), Image.ANTIALIAS, )
        wfile = BLOBManager.Open(
            self.pathname, mode='w', encoding='binary', create=True,
        )
        self.image.save(wfile, 'png')
        wfile.flush()
        wfile.close()  # Close output file - the thumbnail image file

        del self.image

        return True
