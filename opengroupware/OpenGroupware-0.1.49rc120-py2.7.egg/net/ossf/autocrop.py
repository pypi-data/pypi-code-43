#
# Copyright (c) 2015 Adam Tauno Williams <awilliam@whitemice.org>
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
else:
    HAS_PIL = True
    if not Image.MIME:
        Image.preinit()

from coils.core import BLOBManager
from filter import OpenGroupwareServerSideFilter

from utility import get_format_support_map


if HAS_PIL:
    class ImageAutoCropOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):

            """
            reverse the PIL.Image.MIME dictionary
            {                           - > {
                'GIF': 'image/gif',     - >     'image/gif': 'GIF',
                'PNG': ''image/png',    - >     'image/png': 'PNG',
                'TIFF': 'image/tiff',   - >     'image/tiff': 'TIFF',
                'JPEG': 'image/jpeg',   - >     'image/jpeg': 'JPEG',
            }                           - > }
            """
            output_format_map = get_format_support_map()
            kind = output_format_map.get(self._mimetype)

            s = BLOBManager.ScratchFile()

            image = Image.open(self.rfile).convert('RGBA')
            signature = image.crop(image.getbbox())
            signature.load()
            signature.save(s, kind, )
            image.close()

            return s

        @property
        def mimetype(self):
            return self._mimetype

else:
    class ImageAutoCropOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            return self._rfile

        @property
        def mimetype(self):
            return self._mimetype
