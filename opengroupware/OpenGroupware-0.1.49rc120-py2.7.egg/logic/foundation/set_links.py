#
# Copyright (c) 2010, 2012, 2013, 2015
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import KVC, CoilsException, Command, AccessForbiddenException
from keymap import COILS_OBJECTLINK_KEYMAP


class SetObjectLinks(Command):
    __domain__ = "object"
    __operation__ = "set-links"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.obj, self.object_id, entity_name, = \
            self.get_object_id_from_parameters(**params)

        # we need a reference to the entity object
        if (not self.obj) and self.object_id:
            self.obj = self._ctx.type_manager.get_entity(self.object_id)
        if not self.obj:
            raise CoilsException(
                'Unable to marshall OGo#{0}'.format(self.object_id, )
            )

        self.links = params.get('links', [])

    def check_run_permissions(self):
        """
        What rights should adjusting the linkage for an object actually
        required?  Note that is isn't about adding a specific object link to
        an entity but adjust its list of links, so this must come from an
        operation such as zOGI putObject.
        """
        rights = self._ctx.access_manager.access_rights(self.obj, )
        if not set('iwa').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self.obj, )
            )

    def run(self, **params):

        links = list()
        for link in [
            KVC.translate_dict(x, COILS_OBJECTLINK_KEYMAP)
            for x in self.links
        ]:
            if 'direction' in link:
                """
                This is an Omphalos "compressed" link representation, it
                contains a direction value rather than both the source and
                target of the link,  we decompose the representation by
                setting both the source and target
                """
                if link['direction'].upper() == 'TO':
                    # Link points at the current entity (incoming)
                    link['source_id'] = link['target_id']
                    link['target_id'] = self.obj.object_id
                elif link['direction'].upper() == 'FROM':
                    # Link originates from the current object
                    link['source_id'] = self.obj.object_id
                else:
                    raise CoilsException(
                        'Omphalos compresses link representation '
                        'with invalid direction'
                    )
                del link['direction']
                links.append(link)

        self._ctx.link_manager.sync_links(self.obj, links)

        self.set_result(True)
