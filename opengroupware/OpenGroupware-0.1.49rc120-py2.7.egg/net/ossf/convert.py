#
# Copyright (c) 2011, 2015 Adam Tauno Williams <awilliam@whitemice.org>
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
try:
    from PIL import Image
except:
    HAS_PIL = False
    IMAGE_OSSF_CONVERSION_RULES = {}
else:
    HAS_PIL = True
    if not Image.MIME:
        Image.preinit()
    IMAGE_OSSF_CONVERSION_RULES = Image.MIME
    """
    Generally this results in something like:
    {
        'GIF': 'image/gif',
        'PNG': 'image/png',
        'JPEG': 'image/jpeg',
        'TIFF': 'image/tiff',
    }
    We use this to adapt the types of images supported by the version of
    PIL which the server is utilizing.
    """

from coils.core import \
    NotImplementedException, \
    BLOBManager, \
    CoilsException
from filter import OpenGroupwareServerSideFilter

from utility import get_format_support_map


if HAS_PIL:
    class ImageConvertOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):

            if not (hasattr(self, '_type')):
                raise CoilsException(
                    'Required URL parameter "type" not specified'
                )
            if not isinstance(self._type, basestring):
                raise CoilsException(
                    'URL parameter "type" not of required type String'
                )

            kind = self._type.upper()

            if kind not in IMAGE_OSSF_CONVERSION_RULES:
                raise NotImplementedException(
                    'Unsupported image type "{0}", must be one of: {1}'
                    .format(
                        self._type,
                        ','.join(IMAGE_OSSF_CONVERSION_RULES.keys()),
                    )
                )

            image = Image.open(self.rfile)
            s = BLOBManager.ScratchFile()
            image.save(s, kind, )
            image.close()

            return s

        @property
        def mimetype(self):
            return IMAGE_OSSF_CONVERSION_RULES.get(self._type.upper())

else:
    class ImageConvertOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            return self._rfile

        @property
        def mimetype(self):
            return self._mimetype
