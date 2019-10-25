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
from coils.net import PathObject
from coils.core import \
    NotImplementedException, \
    BLOBManager
from coils.core.xml import Render as XML_Render


class EnterpriseObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.entity = None
        self.request = None
        self.parameters = None
        PathObject.__init__(self, parent, **params)

    #
    # Method Handlers
    #

    def do_HEAD(self):
        # TODO: Implement
        raise NotImplementedException(
            'HEAD request for Contact content not implemented'
        )

    def do_GET(self):

        detail_level = 65535 - 32
        try:
            detail_level = int(self.parameters.get('level', str(detail_level)))
        except:
            pass

        get_mode = self.parameters.get('mode', 'vcard')
        if isinstance(get_mode, list):
            get_mode = get_mode[0]

        if get_mode == 'vcard':
            # TODO: Support If-None-Match header and HTTP/304 support
            # TODO: Support user-agent description passing
            data = self.context.run_command(
                'object::get-as-ics',
                object=self.entity,
            )
            if data:
                etag = '{0}.{1}.{2}.vcf'.format(
                    self.entity.object_id,
                    self.entity.version,
                    self.context.user_agent_id,
                )
                self.request.simple_response(
                    200,
                    data=data,
                    mimetype='text/x-vcard',
                    headers={
                        'etag': etag,
                        'X-OpenGroupware-Filename': '{0}.vcf'.format(
                            self.entity.object_id,
                        ),
                    },
                )
            return

        elif get_mode == 'xml':
            sfile = BLOBManager.ScratchFile()
            with XML_Render.open_stream(sfile, indent=True, ) as xml:
                XML_Render.render_entity(
                    self.entity,
                    self.context,
                    detail_level=detail_level,
                    container=xml,
                )
            etag = '{0}.{1}.{2}.xml'.format(
                self.entity.object_id,
                self.entity.version,
                self.context.user_agent_id,
            )
            self.request.simple_response(
                200,
                stream=sfile,
                mimetype='application/xml',
                headers={
                    'etag': etag,
                    'X-OpenGroupware-Filename': '{0}.{1}.xml'.format(
                        self.entity.object_id, self.entity.version,
                    ),
                }
            )
            BLOBManager.Close(sfile)
            return

        raise NotImplementedException(
            'undefined mode for Enterprise GET: {0}'
            .format(get_mode, )
        )
