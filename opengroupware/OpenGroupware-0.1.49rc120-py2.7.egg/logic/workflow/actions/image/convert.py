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
    class ConvertImageAction(ActionCommand):
        __domain__ = "action"
        __operation__ = "convert-image"
        __aliases__ = ['convertImage', 'convertImageAction', ]

        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return self._output_mimetype

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

            if self._mimetype_out not in format_support_map:
                raise NotImplementedException(
                    'Unsupported target image type {0}, must be one of: {1}'
                    .format(
                        self._mimetype_out,
                        ','.join(format_support_map.keys()),
                    )
                )

            image = Image.open(self.rfile)
            image.save(
                self.wfile,
                format_support_map[self._mimetype_out],
            )
            image = None

            self._output_mimetype = self._mimetype_out

        def parse_action_parameters(self):
            self._mimetype_out = self.process_label_substitutions(
                self.action_parameters.get('targetFormat', 'image/jpeg', )
            )


else:
    class ConvertImageAction(object):
        pass
