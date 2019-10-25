#!/usr/bin/python
# Copyright (c) 2010, 2012, 2015, 2016
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
from coils.foundation import BLOBManager
from coils.core import Contact, Enterprise, Team, CoilsException
from render_contact import render_contact
from render_enterprise import render_enterprise
from render_team import render_team

VCF_CACHE_ENABLED = True

VCF_RENDER_VERSION = 101  # Increment when render code base is changed


class Render(object):

    @staticmethod
    def render(entity, ctx, **params):

        # TODO: log duration of render at debug level
        # TODO: Allow a config directive to disable VCF cache
        # TODO: how can we assure cache write is atomic?

        if (entity is None):
            raise CoilsException('Attempt to render a None')

        if isinstance(entity, list):
            """
            if we received a collection of entities render then as a VCF
            collection, each vCard object is seperated by a blank line.
            """
            payload = ''
            for tmp in entity:
                single_payload = Render.render(tmp, ctx, **params)
                if single_payload:
                    payload += single_payload
                    payload += '\r\n'
            return payload

        cache_pathname = None

        if VCF_CACHE_ENABLED:
            cache_filename = '{0}.{1}.{2}.{3}.vcf'.format(
                entity.object_id,
                entity.version,
                ctx.user_agent_id,
                VCF_RENDER_VERSION,
            )
            cache_pathname = (
                'cache/vcf/{0}/{1}'
                .format(cache_filename[2:3], cache_filename, )
            )

            rfile = BLOBManager.Open(
                cache_pathname,
                'r',
                encoding='binary',
            )
            if rfile:
                payload = rfile.read()
                BLOBManager.Close(rfile)
                return payload

        if isinstance(entity, Contact):
            payload = render_contact(entity, ctx, **params)
        elif isinstance(entity, Enterprise):
            payload = render_enterprise(entity, ctx, **params)
        elif isinstance(entity, Team):
            payload = render_team(entity, ctx, **params)
        else:
            raise CoilsException(
                'Entity %s cannot be rendered as a vCard'
                .format(entity.__entityName__, )
            )

        if VCF_CACHE_ENABLED:
            try:
                wfile = BLOBManager.Open(
                    cache_pathname, 'w',  encoding='binary',
                )
                wfile.write(payload)
                BLOBManager.Close(wfile)
            except:
                # stashing to cache has failed; OK
                pass

        return payload
