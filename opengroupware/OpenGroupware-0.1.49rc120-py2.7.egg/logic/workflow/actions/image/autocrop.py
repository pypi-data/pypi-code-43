#
# Copyright (c) 2015
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
from coils.core import NotImplementedException
from coils.core.logic import ActionCommand

from utility import get_format_support_map

try:
    from PIL import Image
except:
    HAS_PIL = False
else:
    HAS_PIL = True
    if not Image.MIME:
        Image.preinit()

if HAS_PIL:
    class AutoCropImageAction(ActionCommand):
        __domain__ = "action"
        __operation__ = "autocrop-image"
        __aliases__ = ['autoCropImage', 'autoCropImageAction', ]

        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return self.input_mimetype

        def do_action(self):

            """
            reverse the PIL.Image.MIME dictionary
            {                           - > {
                'GIF': 'image/gif',     - >     'image/gif': 'GIF',
                'PNG': ''image/png',    - >     'image/png': 'PNG',
                'TIFF': 'image/tiff',   - >     'image/tiff': 'TIFF',
                'JPEG': 'image/jpeg',   - >     'image/jpeg': 'JPEG',
            }                           - > }
            """
            format_support_map = get_format_support_map()

            if self.input_mimetype not in format_support_map:
                raise NotImplementedException(
                    'Image type "{0}" not supported'
                    .format(self.input_mimetype, )
                )

            image = Image.open(self.rfile).convert('RGBA')
            signature = image.crop(image.getbbox())
            signature.load()
            signature.save(
                self.wfile, format_support_map[self.input_mimetype],
            )
            image = None
            signature = None

        def parse_action_parameters(self):
            pass

        def do_epilogue(self):
            pass

else:
    class AutoCropImageAction(object):
        pass
