#
# Copyright (c) 2015, 2016, 2018
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
import hashlib
from lxml import etree
from coils.core import BLOBManager, NoSuchPathException, CoilsException
from coils.net import PathObject, json_encode
from coils.logic.workflow import XSLTDocument, OIEXSLTExtensionPoints
from coils.net.ossf import MarshallOSSFChain

class XSLTObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.template_text = None
        PathObject.__init__(self, parent, **params)

    def _marshall_xslt_template_text(self, xslt_name):
        stylesheet = XSLTDocument(xslt_name)
        if stylesheet:
            handle = stylesheet.read_handle
            if handle:
                xslt_ = handle.read()
                BLOBManager.Close(handle)
            else:
                raise CoilsException(
                    'Unable to open XSLT stylesheet "{0}" for reading'.
                    format(xslt_name, )
                )
            stylesheet.close()
        else:
            raise NoSuchPathException(
                'XSLT Stylesheet "{0}" not found.'.
                format(xslt_name, )
            )
        return xslt_

    def _marshall_extensions_object(
        self, context, process, scope_stack, ctx_ids,
    ):
        oie_extentions = OIEXSLTExtensionPoints(
            context=context,
            process=process,
            scope=scope_stack,
            ctxids=ctx_ids,
        )

        extensions = etree.Extension(
            oie_extentions,
            (
                # Reset/set the value of a named sequence
                'sequencereset',
                # Retrieve the value of a named sequence
                'sequencevalue',
                # Increment a named sequence, returning the new value
                'sequenceincrement',
                # Retrieve the content of a message by label
                'messagetext',
                # Search for an objectId by criteria
                'searchforobjectid',
                # Performa table lookup
                'tablelookup',
                # Reformat a StandardXML date to some other format
                'reformatdate',
                # Transform a StandardXML datetime value to a StandardXML date
                'datetimetodate',
                # Convert string from the spec'd format to a StandardXML date
                'stringtodate',
                # Convert string from the spec'd form to a StandardXML datetime
                'stringtodate',
                # Retrieve the value of a process XATTR property
                'xattrvalue',
                # Count the number of objects matching the criteria
                'countobjects',
                # Return the object id of the current process
                'getpid',
                # Return the month value from a date or datetime
                'month',
                # Return the year value from a date or datetime
                'year',
                # Return the first date in the specified year + month
                'monthstart',
                # Return the last date in the specified year + month
                'monthend',
                # Return a date representation of today
                'today',
                # Return a date representation of the previous day
                'yesterday',
                # Return a date representation of the upcming day
                'tomorrow',
                # Return a date the spec'd number of days from the spec'd date
                'dateplusdays',
                # Return the number of days between the specified dates
                'days',
                # Return the number of weekdays between the specified dates
                'weekdays',
                'replace',
                'getuuid',
                'getguid',
                'generateguid',
                'generatehexguid',
                'getblobpath',
                'newline',
                'localizedatetime',
                'searchforobjects',
                'xpath',
                'truncate',
            ),
            ns='http://www.opengroupware.us/oie',
        )

        return extensions

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        xslt_ = self._marshall_xslt_template_text(name)

        self.log.debug(
            'Template size is {0}b'.format(len(xslt_), ),
        )

        return XSLTObject(
            self, name,
            template_text=xslt_,
            parameters=self.parameters,
            request=self.request,
            context=self.context,
        )

    def do_GET(self):

        if not self.template_text:
            # return a list [JSON] of the defined formats
            names = XSLTDocument.List()
            self.request.simple_response(
                200,
                data=json_encode(names),
                mimetype='text/json',
            )
            return

        chk = hashlib.md5()
        chk.update(self.template_text)
        etag = chk.hexdigest()

        # return the markup of the named format
        self.request.simple_response(
            200,
            data=self.template_text,
            mimetype='application/xml',
            headers={
                'ETag': etag,
                'Content-Disposition': 'inline; filename={0}'.format(
                    self.name,
                ),
                'X-OpenGroupware-Filename': self.name,
            },
        )

    def do_PUT(self, name):

        if name == 'transform':
            self._do_put_transform()

    def _do_put_transform(self):

        if 'mimetype' in self.parameters:
            mimetype = self.parameters.get('mimetype')[0]
        else:
            mimetype = 'application/xml'

        if 'processId' in self.parameters:
            process_id = int(self.parameters.get('processId')[0])
            process = self.context.run_command(
                'process::get', id=process_id,
            )
            if not process:
                raise CoilsException(
                    'Unable to marshall OGo#{0} [Process] for XSLT test mode'
                    .format(process_id, )
                )
        else:
            process_id = None
            process = None

        rfile = BLOBManager.ScratchFile()
        rfile.write(self.request.get_request_payload())
        rfile.seek(0)

        extension_object = self._marshall_extensions_object(
            context=self.context,
            process=process,
            scope_stack=list(),
            ctx_ids=self.context.context_ids,
        )

        source = etree.parse(rfile)

        xslt = etree.XSLT(
            etree.XML(self.template_text),
            extensions=extension_object,
        )

        xslt_params = dict()

        wfile = BLOBManager.ScratchFile()
        wfile.write(
            unicode(
                xslt(
                    source,
                    **xslt_params
                )
            )
        )
        wfile.seek(0)

        wfile, mimetype = MarshallOSSFChain(
            wfile, mimetype, self.parameters,
        )

        self.request.stream_response(
            200,
            stream=wfile,
            mimetype=mimetype,
            headers={
                'Content-Disposition': 'inline; filename=transformed.xml',
                'X-OpenGroupware-Filename': '{0}'.format('transformed.xml', ),
                'etag': '{0}OIE'.format(time.time(), )
            },
        )
